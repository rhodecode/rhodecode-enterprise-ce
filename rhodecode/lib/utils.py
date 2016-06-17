# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, version 3
# (only), as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is dual-licensed. If you wish to learn more about the
# RhodeCode Enterprise Edition, including its added features, Support services,
# and proprietary license terms, please see https://rhodecode.com/licenses/

"""
Utilities library for RhodeCode
"""

import datetime
import decorator
import json
import logging
import os
import re
import shutil
import tempfile
import traceback
import tarfile
import warnings
from os.path import abspath
from os.path import dirname as dn, join as jn

import paste
import pkg_resources
from paste.script.command import Command, BadCommand
from webhelpers.text import collapse, remove_formatting, strip_tags
from mako import exceptions

from rhodecode.lib.fakemod import create_module
from rhodecode.lib.vcs.backends.base import Config
from rhodecode.lib.vcs.exceptions import VCSError
from rhodecode.lib.vcs.utils.helpers import get_scm, get_scm_backend
from rhodecode.lib.utils2 import (
    safe_str, safe_unicode, get_current_rhodecode_user, md5)
from rhodecode.model import meta
from rhodecode.model.db import (
    Repository, User, RhodeCodeUi, UserLog, RepoGroup, UserGroup)
from rhodecode.model.meta import Session
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.settings import VcsSettingsModel, SettingsModel

log = logging.getLogger(__name__)

REMOVED_REPO_PAT = re.compile(r'rm__\d{8}_\d{6}_\d{6}__.*')

_license_cache = None


def recursive_replace(str_, replace=' '):
    """
    Recursive replace of given sign to just one instance

    :param str_: given string
    :param replace: char to find and replace multiple instances

    Examples::
    >>> recursive_replace("Mighty---Mighty-Bo--sstones",'-')
    'Mighty-Mighty-Bo-sstones'
    """

    if str_.find(replace * 2) == -1:
        return str_
    else:
        str_ = str_.replace(replace * 2, replace)
        return recursive_replace(str_, replace)


def repo_name_slug(value):
    """
    Return slug of name of repository
    This function is called on each creation/modification
    of repository to prevent bad names in repo
    """

    slug = remove_formatting(value)
    slug = strip_tags(slug)

    for c in """`?=[]\;'"<>,/~!@#$%^&*()+{}|: """:
        slug = slug.replace(c, '-')
    slug = recursive_replace(slug, '-')
    slug = collapse(slug, '-')
    return slug


#==============================================================================
# PERM DECORATOR HELPERS FOR EXTRACTING NAMES FOR PERM CHECKS
#==============================================================================
def get_repo_slug(request):
    _repo = request.environ['pylons.routes_dict'].get('repo_name')
    if _repo:
        _repo = _repo.rstrip('/')
    return _repo


def get_repo_group_slug(request):
    _group = request.environ['pylons.routes_dict'].get('group_name')
    if _group:
        _group = _group.rstrip('/')
    return _group


def get_user_group_slug(request):
    _group = request.environ['pylons.routes_dict'].get('user_group_id')
    try:
        _group = UserGroup.get(_group)
        if _group:
            _group = _group.users_group_name
    except Exception:
        log.debug(traceback.format_exc())
        #catch all failures here
        pass

    return _group


def action_logger(user, action, repo, ipaddr='', sa=None, commit=False):
    """
    Action logger for various actions made by users

    :param user: user that made this action, can be a unique username string or
        object containing user_id attribute
    :param action: action to log, should be on of predefined unique actions for
        easy translations
    :param repo: string name of repository or object containing repo_id,
        that action was made on
    :param ipaddr: optional ip address from what the action was made
    :param sa: optional sqlalchemy session

    """

    if not sa:
        sa = meta.Session()
    # if we don't get explicit IP address try to get one from registered user
    # in tmpl context var
    if not ipaddr:
        ipaddr = getattr(get_current_rhodecode_user(), 'ip_addr', '')

    try:
        if getattr(user, 'user_id', None):
            user_obj = User.get(user.user_id)
        elif isinstance(user, basestring):
            user_obj = User.get_by_username(user)
        else:
            raise Exception('You have to provide a user object or a username')

        if getattr(repo, 'repo_id', None):
            repo_obj = Repository.get(repo.repo_id)
            repo_name = repo_obj.repo_name
        elif isinstance(repo, basestring):
            repo_name = repo.lstrip('/')
            repo_obj = Repository.get_by_repo_name(repo_name)
        else:
            repo_obj = None
            repo_name = ''

        user_log = UserLog()
        user_log.user_id = user_obj.user_id
        user_log.username = user_obj.username
        action = safe_unicode(action)
        user_log.action = action[:1200000]

        user_log.repository = repo_obj
        user_log.repository_name = repo_name

        user_log.action_date = datetime.datetime.now()
        user_log.user_ip = ipaddr
        sa.add(user_log)

        log.info('Logging action:`%s` on repo:`%s` by user:%s ip:%s',
                 action, safe_unicode(repo), user_obj, ipaddr)
        if commit:
            sa.commit()
    except Exception:
        log.error(traceback.format_exc())
        raise


def get_filesystem_repos(path, recursive=False, skip_removed_repos=True):
    """
    Scans given path for repos and return (name,(type,path)) tuple

    :param path: path to scan for repositories
    :param recursive: recursive search and return names with subdirs in front
    """

    # remove ending slash for better results
    path = path.rstrip(os.sep)
    log.debug('now scanning in %s location recursive:%s...', path, recursive)

    def _get_repos(p):
        dirpaths = _get_dirpaths(p)
        if not _is_dir_writable(p):
            log.warning('repo path without write access: %s', p)

        for dirpath in dirpaths:
            if os.path.isfile(os.path.join(p, dirpath)):
                continue
            cur_path = os.path.join(p, dirpath)

            # skip removed repos
            if skip_removed_repos and REMOVED_REPO_PAT.match(dirpath):
                continue

            #skip .<somethin> dirs
            if dirpath.startswith('.'):
                continue

            try:
                scm_info = get_scm(cur_path)
                yield scm_info[1].split(path, 1)[-1].lstrip(os.sep), scm_info
            except VCSError:
                if not recursive:
                    continue
                #check if this dir containts other repos for recursive scan
                rec_path = os.path.join(p, dirpath)
                if os.path.isdir(rec_path):
                    for inner_scm in _get_repos(rec_path):
                        yield inner_scm

    return _get_repos(path)


def _get_dirpaths(p):
    try:
        # OS-independable way of checking if we have at least read-only
        # access or not.
        dirpaths = os.listdir(p)
    except OSError:
        log.warning('ignoring repo path without read access: %s', p)
        return []

    # os.listpath has a tweak: If a unicode is passed into it, then it tries to
    # decode paths and suddenly returns unicode objects itself. The items it
    # cannot decode are returned as strings and cause issues.
    #
    # Those paths are ignored here until a solid solution for path handling has
    # been built.
    expected_type = type(p)

    def _has_correct_type(item):
        if type(item) is not expected_type:
            log.error(
                u"Ignoring path %s since it cannot be decoded into unicode.",
                # Using "repr" to make sure that we see the byte value in case
                # of support.
                repr(item))
            return False
        return True

    dirpaths = [item for item in dirpaths if _has_correct_type(item)]

    return dirpaths


def _is_dir_writable(path):
    """
    Probe if `path` is writable.

    Due to trouble on Cygwin / Windows, this is actually probing if it is
    possible to create a file inside of `path`, stat does not produce reliable
    results in this case.
    """
    try:
        with tempfile.TemporaryFile(dir=path):
            pass
    except OSError:
        return False
    return True


def is_valid_repo(repo_name, base_path, expect_scm=None, explicit_scm=None):
    """
    Returns True if given path is a valid repository False otherwise.
    If expect_scm param is given also, compare if given scm is the same
    as expected from scm parameter. If explicit_scm is given don't try to
    detect the scm, just use the given one to check if repo is valid

    :param repo_name:
    :param base_path:
    :param expect_scm:
    :param explicit_scm:

    :return True: if given path is a valid repository
    """
    full_path = os.path.join(safe_str(base_path), safe_str(repo_name))
    log.debug('Checking if `%s` is a valid path for repository', repo_name)

    try:
        if explicit_scm:
            detected_scms = [get_scm_backend(explicit_scm)]
        else:
            detected_scms = get_scm(full_path)

        if expect_scm:
            return detected_scms[0] == expect_scm
        log.debug('path: %s is an vcs object:%s', full_path, detected_scms)
        return True
    except VCSError:
        log.debug('path: %s is not a valid repo !', full_path)
        return False


def is_valid_repo_group(repo_group_name, base_path, skip_path_check=False):
    """
    Returns True if given path is a repository group, False otherwise

    :param repo_name:
    :param base_path:
    """
    full_path = os.path.join(safe_str(base_path), safe_str(repo_group_name))
    log.debug('Checking if `%s` is a valid path for repository group',
              repo_group_name)

    # check if it's not a repo
    if is_valid_repo(repo_group_name, base_path):
        log.debug('Repo called %s exist, it is not a valid '
                  'repo group' % repo_group_name)
        return False

    try:
        # we need to check bare git repos at higher level
        # since we might match branches/hooks/info/objects or possible
        # other things inside bare git repo
        scm_ = get_scm(os.path.dirname(full_path))
        log.debug('path: %s is a vcs object:%s, not valid '
                  'repo group' % (full_path, scm_))
        return False
    except VCSError:
        pass

    # check if it's a valid path
    if skip_path_check or os.path.isdir(full_path):
        log.debug('path: %s is a valid repo group !', full_path)
        return True

    log.debug('path: %s is not a valid repo group !', full_path)
    return False


def ask_ok(prompt, retries=4, complaint='Yes or no please!'):
    while True:
        ok = raw_input(prompt)
        if ok in ('y', 'ye', 'yes'):
            return True
        if ok in ('n', 'no', 'nop', 'nope'):
            return False
        retries = retries - 1
        if retries < 0:
            raise IOError
        print complaint

# propagated from mercurial documentation
ui_sections = [
    'alias', 'auth',
    'decode/encode', 'defaults',
    'diff', 'email',
    'extensions', 'format',
    'merge-patterns', 'merge-tools',
    'hooks', 'http_proxy',
    'smtp', 'patch',
    'paths', 'profiling',
    'server', 'trusted',
    'ui', 'web', ]


def config_data_from_db(clear_session=True, repo=None):
    """
    Read the configuration data from the database and return configuration
    tuples.
    """
    config = []

    sa = meta.Session()
    settings_model = VcsSettingsModel(repo=repo, sa=sa)

    ui_settings = settings_model.get_ui_settings()

    for setting in ui_settings:
        if setting.active:
            log.debug(
                'settings ui from db: [%s] %s=%s',
                setting.section, setting.key, setting.value)
            config.append((
                safe_str(setting.section), safe_str(setting.key),
                safe_str(setting.value)))
        if setting.key == 'push_ssl':
            # force set push_ssl requirement to False, rhodecode
            # handles that
            config.append((
                safe_str(setting.section), safe_str(setting.key), False))
    if clear_session:
        meta.Session.remove()

    # TODO: mikhail: probably it makes no sense to re-read hooks information.
    # It's already there and activated/deactivated
    skip_entries = []
    enabled_hook_classes = get_enabled_hook_classes(ui_settings)
    if 'pull' not in enabled_hook_classes:
        skip_entries.append(('hooks', RhodeCodeUi.HOOK_PRE_PULL))
    if 'push' not in enabled_hook_classes:
        skip_entries.append(('hooks', RhodeCodeUi.HOOK_PRE_PUSH))

    config = [entry for entry in config if entry[:2] not in skip_entries]

    return config


def make_db_config(clear_session=True, repo=None):
    """
    Create a :class:`Config` instance based on the values in the database.
    """
    config = Config()
    config_data = config_data_from_db(clear_session=clear_session, repo=repo)
    for section, option, value in config_data:
        config.set(section, option, value)
    return config


def get_enabled_hook_classes(ui_settings):
    """
    Return the enabled hook classes.

    :param ui_settings: List of ui_settings as returned
        by :meth:`VcsSettingsModel.get_ui_settings`

    :return: a list with the enabled hook classes. The order is not guaranteed.
    :rtype: list
    """
    enabled_hooks = []
    active_hook_keys = [
        key for section, key, value, active in ui_settings
        if section == 'hooks' and active]

    hook_names = {
        RhodeCodeUi.HOOK_PUSH: 'push',
        RhodeCodeUi.HOOK_PULL: 'pull',
        RhodeCodeUi.HOOK_REPO_SIZE: 'repo_size'
    }

    for key in active_hook_keys:
        hook = hook_names.get(key)
        if hook:
            enabled_hooks.append(hook)

    return enabled_hooks


def set_rhodecode_config(config):
    """
    Updates pylons config with new settings from database

    :param config:
    """
    app_settings = SettingsModel().get_all_settings()

    for k, v in app_settings.items():
        config[k] = v


def map_groups(path):
    """
    Given a full path to a repository, create all nested groups that this
    repo is inside. This function creates parent-child relationships between
    groups and creates default perms for all new groups.

    :param paths: full path to repository
    """
    sa = meta.Session()
    groups = path.split(Repository.NAME_SEP)
    parent = None
    group = None

    # last element is repo in nested groups structure
    groups = groups[:-1]
    rgm = RepoGroupModel(sa)
    owner = User.get_first_admin()
    for lvl, group_name in enumerate(groups):
        group_name = '/'.join(groups[:lvl] + [group_name])
        group = RepoGroup.get_by_group_name(group_name)
        desc = '%s group' % group_name

        # skip folders that are now removed repos
        if REMOVED_REPO_PAT.match(group_name):
            break

        if group is None:
            log.debug('creating group level: %s group_name: %s',
                       lvl, group_name)
            group = RepoGroup(group_name, parent)
            group.group_description = desc
            group.user = owner
            sa.add(group)
            perm_obj = rgm._create_default_perms(group)
            sa.add(perm_obj)
            sa.flush()

        parent = group
    return group


def repo2db_mapper(initial_repo_list, remove_obsolete=False):
    """
    maps all repos given in initial_repo_list, non existing repositories
    are created, if remove_obsolete is True it also checks for db entries
    that are not in initial_repo_list and removes them.

    :param initial_repo_list: list of repositories found by scanning methods
    :param remove_obsolete: check for obsolete entries in database
    """
    from rhodecode.model.repo import RepoModel
    from rhodecode.model.scm import ScmModel
    sa = meta.Session()
    repo_model = RepoModel()
    user = User.get_first_admin()
    added = []

    # creation defaults
    defs = SettingsModel().get_default_repo_settings(strip_prefix=True)
    enable_statistics = defs.get('repo_enable_statistics')
    enable_locking = defs.get('repo_enable_locking')
    enable_downloads = defs.get('repo_enable_downloads')
    private = defs.get('repo_private')

    for name, repo in initial_repo_list.items():
        group = map_groups(name)
        unicode_name = safe_unicode(name)
        db_repo = repo_model.get_by_repo_name(unicode_name)
        # found repo that is on filesystem not in RhodeCode database
        if not db_repo:
            log.info('repository %s not found, creating now', name)
            added.append(name)
            desc = (repo.description
                    if repo.description != 'unknown'
                    else '%s repository' % name)

            db_repo = repo_model._create_repo(
                repo_name=name,
                repo_type=repo.alias,
                description=desc,
                repo_group=getattr(group, 'group_id', None),
                owner=user,
                enable_locking=enable_locking,
                enable_downloads=enable_downloads,
                enable_statistics=enable_statistics,
                private=private,
                state=Repository.STATE_CREATED
            )
            sa.commit()
            # we added that repo just now, and make sure we updated server info
            if db_repo.repo_type == 'git':
                git_repo = db_repo.scm_instance()
                # update repository server-info
                log.debug('Running update server info')
                git_repo._update_server_info()

            db_repo.update_commit_cache()

        config = db_repo._config
        config.set('extensions', 'largefiles', '')
        ScmModel().install_hooks(
            db_repo.scm_instance(config=config),
            repo_type=db_repo.repo_type)

    removed = []
    if remove_obsolete:
        # remove from database those repositories that are not in the filesystem
        for repo in sa.query(Repository).all():
            if repo.repo_name not in initial_repo_list.keys():
                log.debug("Removing non-existing repository found in db `%s`",
                          repo.repo_name)
                try:
                    RepoModel(sa).delete(repo, forks='detach', fs_remove=False)
                    sa.commit()
                    removed.append(repo.repo_name)
                except Exception:
                    # don't hold further removals on error
                    log.error(traceback.format_exc())
                    sa.rollback()

        def splitter(full_repo_name):
            _parts = full_repo_name.rsplit(RepoGroup.url_sep(), 1)
            gr_name = None
            if len(_parts) == 2:
                gr_name = _parts[0]
            return gr_name

        initial_repo_group_list = [splitter(x) for x in
                                   initial_repo_list.keys() if splitter(x)]

        # remove from database those repository groups that are not in the
        # filesystem due to parent child relationships we need to delete them
        # in a specific order of most nested first
        all_groups = [x.group_name for x in sa.query(RepoGroup).all()]
        nested_sort = lambda gr: len(gr.split('/'))
        for group_name in sorted(all_groups, key=nested_sort, reverse=True):
            if group_name not in initial_repo_group_list:
                repo_group = RepoGroup.get_by_group_name(group_name)
                if (repo_group.children.all() or
                    not RepoGroupModel().check_exist_filesystem(
                        group_name=group_name, exc_on_failure=False)):
                    continue

                log.info(
                    'Removing non-existing repository group found in db `%s`',
                    group_name)
                try:
                    RepoGroupModel(sa).delete(group_name, fs_remove=False)
                    sa.commit()
                    removed.append(group_name)
                except Exception:
                    # don't hold further removals on error
                    log.exception(
                        'Unable to remove repository group `%s`',
                        group_name)
                    sa.rollback()
                    raise

    return added, removed


def get_default_cache_settings(settings):
    cache_settings = {}
    for key in settings.keys():
        for prefix in ['beaker.cache.', 'cache.']:
            if key.startswith(prefix):
                name = key.split(prefix)[1].strip()
                cache_settings[name] = settings[key].strip()
    return cache_settings


# set cache regions for beaker so celery can utilise it
def add_cache(settings):
    from rhodecode.lib import caches
    cache_settings = {'regions': None}
    # main cache settings used as default ...
    cache_settings.update(get_default_cache_settings(settings))

    if cache_settings['regions']:
        for region in cache_settings['regions'].split(','):
            region = region.strip()
            region_settings = {}
            for key, value in cache_settings.items():
                if key.startswith(region):
                    region_settings[key.split('.')[1]] = value

            caches.configure_cache_region(
                region, region_settings, cache_settings)


def load_rcextensions(root_path):
    import rhodecode
    from rhodecode.config import conf

    path = os.path.join(root_path, 'rcextensions', '__init__.py')
    if os.path.isfile(path):
        rcext = create_module('rc', path)
        EXT = rhodecode.EXTENSIONS = rcext
        log.debug('Found rcextensions now loading %s...', rcext)

        # Additional mappings that are not present in the pygments lexers
        conf.LANGUAGES_EXTENSIONS_MAP.update(getattr(EXT, 'EXTRA_MAPPINGS', {}))

        # auto check if the module is not missing any data, set to default if is
        # this will help autoupdate new feature of rcext module
        #from rhodecode.config import rcextensions
        #for k in dir(rcextensions):
        #    if not k.startswith('_') and not hasattr(EXT, k):
        #        setattr(EXT, k, getattr(rcextensions, k))


def get_custom_lexer(extension):
    """
    returns a custom lexer if it is defined in rcextensions module, or None
    if there's no custom lexer defined
    """
    import rhodecode
    from pygments import lexers
    # check if we didn't define this extension as other lexer
    extensions = rhodecode.EXTENSIONS and getattr(rhodecode.EXTENSIONS, 'EXTRA_LEXERS', None)
    if extensions and extension in rhodecode.EXTENSIONS.EXTRA_LEXERS:
        _lexer_name = rhodecode.EXTENSIONS.EXTRA_LEXERS[extension]
        return lexers.get_lexer_by_name(_lexer_name)


#==============================================================================
# TEST FUNCTIONS AND CREATORS
#==============================================================================
def create_test_index(repo_location, config, full_index):
    """
    Makes default test index

    :param config: test config
    :param full_index:
    # start test server:
    rcserver --with-vcsserver test.ini

    # build index and store it in /tmp/rc/index:
    rhodecode-index --force --api-host=http://vps1.dev:5000 --api-key=xxx --engine-location=/tmp/rc/index

    # package and move new packages
    tar -zcvf vcs_search_index.tar.gz -C /tmp/rc index
    mv vcs_search_index.tar.gz rhodecode/tests/fixtures/

    """
    import rc_testdata

    rc_testdata.extract_search_index(
        'vcs_search_index', os.path.dirname(config['search.location']))


def create_test_env(repos_test_path, config):
    """
    Makes a fresh database.
    """
    from rhodecode.lib.db_manage import DbManage

    # PART ONE create db
    dbconf = config['sqlalchemy.db1.url']
    log.debug('making test db %s', dbconf)

    # create test dir if it doesn't exist
    if not os.path.isdir(repos_test_path):
        log.debug('Creating testdir %s', repos_test_path)
        os.makedirs(repos_test_path)

    dbmanage = DbManage(log_sql=False, dbconf=dbconf, root=config['here'],
                        tests=True, cli_args={'force_ask': True})
    dbmanage.create_tables(override=True)
    dbmanage.set_db_version()
    # for tests dynamically set new root paths based on generated content
    dbmanage.create_settings(dbmanage.config_prompt(repos_test_path))
    dbmanage.create_default_user()
    dbmanage.create_test_admin_and_users()
    dbmanage.create_permissions()
    dbmanage.populate_default_permissions()
    Session().commit()

    create_test_repositories(repos_test_path, config)


def create_test_repositories(path, config):
    """
    Creates test repositories in the temporary directory. Repositories are
    extracted from archives within the rc_testdata package.
    """
    import rc_testdata
    from rhodecode.tests import HG_REPO, GIT_REPO, SVN_REPO, TESTS_TMP_PATH

    log.debug('making test vcs repositories')

    idx_path = config['search.location']
    data_path = config['cache_dir']

    # clean index and data
    if idx_path and os.path.exists(idx_path):
        log.debug('remove %s', idx_path)
        shutil.rmtree(idx_path)

    if data_path and os.path.exists(data_path):
        log.debug('remove %s', data_path)
        shutil.rmtree(data_path)

    rc_testdata.extract_hg_dump('vcs_test_hg', jn(TESTS_TMP_PATH, HG_REPO))
    rc_testdata.extract_git_dump('vcs_test_git', jn(TESTS_TMP_PATH, GIT_REPO))

    # Note: Subversion is in the process of being integrated with the system,
    # until we have a properly packed version of the test svn repository, this
    # tries to copy over the repo from a package "rc_testdata"
    svn_repo_path = rc_testdata.get_svn_repo_archive()
    with tarfile.open(svn_repo_path) as tar:
        tar.extractall(jn(TESTS_TMP_PATH, SVN_REPO))


#==============================================================================
# PASTER COMMANDS
#==============================================================================
class BasePasterCommand(Command):
    """
    Abstract Base Class for paster commands.

    The celery commands are somewhat aggressive about loading
    celery.conf, and since our module sets the `CELERY_LOADER`
    environment variable to our loader, we have to bootstrap a bit and
    make sure we've had a chance to load the pylons config off of the
    command line, otherwise everything fails.
    """
    min_args = 1
    min_args_error = "Please provide a paster config file as an argument."
    takes_config_file = 1
    requires_config_file = True

    def notify_msg(self, msg, log=False):
        """Make a notification to user, additionally if logger is passed
        it logs this action using given logger

        :param msg: message that will be printed to user
        :param log: logging instance, to use to additionally log this message

        """
        if log and isinstance(log, logging):
            log(msg)

    def run(self, args):
        """
        Overrides Command.run

        Checks for a config file argument and loads it.
        """
        if len(args) < self.min_args:
            raise BadCommand(
                self.min_args_error % {'min_args': self.min_args,
                                       'actual_args': len(args)})

        # Decrement because we're going to lob off the first argument.
        # @@ This is hacky
        self.min_args -= 1
        self.bootstrap_config(args[0])
        self.update_parser()
        return super(BasePasterCommand, self).run(args[1:])

    def update_parser(self):
        """
        Abstract method.  Allows for the class' parser to be updated
        before the superclass' `run` method is called.  Necessary to
        allow options/arguments to be passed through to the underlying
        celery command.
        """
        raise NotImplementedError("Abstract Method.")

    def bootstrap_config(self, conf):
        """
        Loads the pylons configuration.
        """
        from pylons import config as pylonsconfig

        self.path_to_ini_file = os.path.realpath(conf)
        conf = paste.deploy.appconfig('config:' + self.path_to_ini_file)
        pylonsconfig.init_app(conf.global_conf, conf.local_conf)

    def _init_session(self):
        """
        Inits SqlAlchemy Session
        """
        logging.config.fileConfig(self.path_to_ini_file)
        from pylons import config
        from rhodecode.config.utils import initialize_database

        # get to remove repos !!
        add_cache(config)
        initialize_database(config)


@decorator.decorator
def jsonify(func, *args, **kwargs):
    """Action decorator that formats output for JSON

    Given a function that will return content, this decorator will turn
    the result into JSON, with a content-type of 'application/json' and
    output it.

    """
    from pylons.decorators.util import get_pylons
    from rhodecode.lib.ext_json import json
    pylons = get_pylons(args)
    pylons.response.headers['Content-Type'] = 'application/json; charset=utf-8'
    data = func(*args, **kwargs)
    if isinstance(data, (list, tuple)):
        msg = "JSON responses with Array envelopes are susceptible to " \
              "cross-site data leak attacks, see " \
              "http://wiki.pylonshq.com/display/pylonsfaq/Warnings"
        warnings.warn(msg, Warning, 2)
        log.warning(msg)
    log.debug("Returning JSON wrapped action output")
    return json.dumps(data, encoding='utf-8')


class PartialRenderer(object):
    """
    Partial renderer used to render chunks of html used in datagrids
    use like::

        _render = PartialRenderer('data_table/_dt_elements.html')
        _render('quick_menu', args, kwargs)
        PartialRenderer.h,
                        c,
                        _,
                        ungettext
        are the template stuff initialized inside and can be re-used later

    :param tmpl_name: template path relate to /templates/ dir
    """

    def __init__(self, tmpl_name):
        import rhodecode
        from pylons import request, tmpl_context as c
        from pylons.i18n.translation import _, ungettext
        from rhodecode.lib import helpers as h

        self.tmpl_name = tmpl_name
        self.rhodecode = rhodecode
        self.c = c
        self._ = _
        self.ungettext = ungettext
        self.h = h
        self.request = request

    def _mako_lookup(self):
        _tmpl_lookup = self.rhodecode.CONFIG['pylons.app_globals'].mako_lookup
        return _tmpl_lookup.get_template(self.tmpl_name)

    def _update_kwargs_for_render(self, kwargs):
        """
        Inject params required for Mako rendering
        """
        _kwargs = {
            '_': self._,
            'h': self.h,
            'c': self.c,
            'request': self.request,
            'ungettext': self.ungettext,
        }
        _kwargs.update(kwargs)
        return _kwargs

    def _render_with_exc(self, render_func, args, kwargs):
        try:
            return render_func.render(*args, **kwargs)
        except:
            log.error(exceptions.text_error_template().render())
            raise

    def _get_template(self, template_obj, def_name):
        if def_name:
            tmpl = template_obj.get_def(def_name)
        else:
            tmpl = template_obj
        return tmpl

    def render(self, def_name, *args, **kwargs):
        lookup_obj = self._mako_lookup()
        tmpl = self._get_template(lookup_obj, def_name=def_name)
        kwargs = self._update_kwargs_for_render(kwargs)
        return self._render_with_exc(tmpl, args, kwargs)

    def __call__(self, tmpl, *args, **kwargs):
        return self.render(tmpl, *args, **kwargs)


def password_changed(auth_user, session):
    if auth_user.username == User.DEFAULT_USER:
        return False
    password_hash = md5(auth_user.password) if auth_user.password else None
    rhodecode_user = session.get('rhodecode_user', {})
    session_password_hash = rhodecode_user.get('password', '')
    return password_hash != session_password_hash


def read_opensource_licenses():
    global _license_cache

    if not _license_cache:
        licenses = pkg_resources.resource_string(
            'rhodecode', 'config/licenses.json')
        _license_cache = json.loads(licenses)

    return _license_cache
