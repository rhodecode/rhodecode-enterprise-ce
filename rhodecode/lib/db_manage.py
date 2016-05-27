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
Database creation, and setup module for RhodeCode Enterprise. Used for creation
of database as well as for migration operations
"""

import os
import sys
import time
import uuid
import logging
import getpass
from os.path import dirname as dn, join as jn

from sqlalchemy.engine import create_engine

from rhodecode import __dbversion__
from rhodecode.model import init_model
from rhodecode.model.user import UserModel
from rhodecode.model.db import (
    User, Permission, RhodeCodeUi, RhodeCodeSetting, UserToPerm,
    DbMigrateVersion, RepoGroup, UserRepoGroupToPerm, CacheKey, Repository)
from rhodecode.model.meta import Session, Base
from rhodecode.model.permission import PermissionModel
from rhodecode.model.repo import RepoModel
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.settings import SettingsModel


log = logging.getLogger(__name__)


def notify(msg):
    """
    Notification for migrations messages
    """
    ml = len(msg) + (4 * 2)
    print('\n%s\n*** %s ***\n%s' % ('*' * ml, msg, '*' * ml)).upper()


class DbManage(object):

    def __init__(self, log_sql, dbconf, root, tests=False,
                 SESSION=None, cli_args={}):
        self.dbname = dbconf.split('/')[-1]
        self.tests = tests
        self.root = root
        self.dburi = dbconf
        self.log_sql = log_sql
        self.db_exists = False
        self.cli_args = cli_args
        self.init_db(SESSION=SESSION)
        self.ask_ok = self.get_ask_ok_func(self.cli_args.get('force_ask'))

    def get_ask_ok_func(self, param):
        if param not in [None]:
            # return a function lambda that has a default set to param
            return lambda *args, **kwargs: param
        else:
            from rhodecode.lib.utils import ask_ok
            return ask_ok

    def init_db(self, SESSION=None):
        if SESSION:
            self.sa = SESSION
        else:
            # init new sessions
            engine = create_engine(self.dburi, echo=self.log_sql)
            init_model(engine)
            self.sa = Session()

    def create_tables(self, override=False):
        """
        Create a auth database
        """

        log.info("Existing database with the same name is going to be destroyed.")
        log.info("Setup command will run DROP ALL command on that database.")
        if self.tests:
            destroy = True
        else:
            destroy = self.ask_ok('Are you sure that you want to destroy the old database? [y/n]')
        if not destroy:
            log.info('Nothing done.')
            sys.exit(0)
        if destroy:
            Base.metadata.drop_all()

        checkfirst = not override
        Base.metadata.create_all(checkfirst=checkfirst)
        log.info('Created tables for %s' % self.dbname)

    def set_db_version(self):
        ver = DbMigrateVersion()
        ver.version = __dbversion__
        ver.repository_id = 'rhodecode_db_migrations'
        ver.repository_path = 'versions'
        self.sa.add(ver)
        log.info('db version set to: %s' % __dbversion__)

    def run_pre_migration_tasks(self):
        """
        Run various tasks before actually doing migrations
        """
        # delete cache keys on each upgrade
        total = CacheKey.query().count()
        log.info("Deleting (%s) cache keys now...", total)
        CacheKey.delete_all_cache()

    def upgrade(self):
        """
        Upgrades given database schema to given revision following
        all needed steps, to perform the upgrade

        """

        from rhodecode.lib.dbmigrate.migrate.versioning import api
        from rhodecode.lib.dbmigrate.migrate.exceptions import \
            DatabaseNotControlledError

        if 'sqlite' in self.dburi:
            print (
               '********************** WARNING **********************\n'
               'Make sure your version of sqlite is at least 3.7.X.  \n'
               'Earlier versions are known to fail on some migrations\n'
               '*****************************************************\n')

        upgrade = self.ask_ok(
            'You are about to perform a database upgrade. Make '
            'sure you have backed up your database. '
            'Continue ? [y/n]')
        if not upgrade:
            log.info('No upgrade performed')
            sys.exit(0)

        repository_path = jn(dn(dn(dn(os.path.realpath(__file__)))),
                             'rhodecode/lib/dbmigrate')
        db_uri = self.dburi

        try:
            curr_version = api.db_version(db_uri, repository_path)
            msg = ('Found current database under version '
                   'control with version %s' % curr_version)

        except (RuntimeError, DatabaseNotControlledError):
            curr_version = 1
            msg = ('Current database is not under version control. Setting '
                   'as version %s' % curr_version)
            api.version_control(db_uri, repository_path, curr_version)

        notify(msg)

        self.run_pre_migration_tasks()

        if curr_version == __dbversion__:
            log.info('This database is already at the newest version')
            sys.exit(0)

        upgrade_steps = range(curr_version + 1, __dbversion__ + 1)
        notify('attempting to upgrade database from '
               'version %s to version %s' % (curr_version, __dbversion__))

        # CALL THE PROPER ORDER OF STEPS TO PERFORM FULL UPGRADE
        _step = None
        for step in upgrade_steps:
            notify('performing upgrade step %s' % step)
            time.sleep(0.5)

            api.upgrade(db_uri, repository_path, step)
            self.sa.rollback()
            notify('schema upgrade for step %s completed' % (step,))

            _step = step

        notify('upgrade to version %s successful' % _step)

    def fix_repo_paths(self):
        """
        Fixes an old RhodeCode version path into new one without a '*'
        """

        paths = self.sa.query(RhodeCodeUi)\
                .filter(RhodeCodeUi.ui_key == '/')\
                .scalar()

        paths.ui_value = paths.ui_value.replace('*', '')

        try:
            self.sa.add(paths)
            self.sa.commit()
        except Exception:
            self.sa.rollback()
            raise

    def fix_default_user(self):
        """
        Fixes an old default user with some 'nicer' default values,
        used mostly for anonymous access
        """
        def_user = self.sa.query(User)\
                .filter(User.username == User.DEFAULT_USER)\
                .one()

        def_user.name = 'Anonymous'
        def_user.lastname = 'User'
        def_user.email = User.DEFAULT_USER_EMAIL

        try:
            self.sa.add(def_user)
            self.sa.commit()
        except Exception:
            self.sa.rollback()
            raise

    def fix_settings(self):
        """
        Fixes rhodecode settings and adds ga_code key for google analytics
        """

        hgsettings3 = RhodeCodeSetting('ga_code', '')

        try:
            self.sa.add(hgsettings3)
            self.sa.commit()
        except Exception:
            self.sa.rollback()
            raise

    def create_admin_and_prompt(self):

        # defaults
        defaults = self.cli_args
        username = defaults.get('username')
        password = defaults.get('password')
        email = defaults.get('email')

        if username is None:
            username = raw_input('Specify admin username:')
        if password is None:
            password = self._get_admin_password()
            if not password:
                # second try
                password = self._get_admin_password()
                if not password:
                    sys.exit()
        if email is None:
            email = raw_input('Specify admin email:')
        api_key = self.cli_args.get('api_key')
        self.create_user(username, password, email, True,
                         strict_creation_check=False,
                         api_key=api_key)

    def _get_admin_password(self):
        password = getpass.getpass('Specify admin password '
                                   '(min 6 chars):')
        confirm = getpass.getpass('Confirm password:')

        if password != confirm:
            log.error('passwords mismatch')
            return False
        if len(password) < 6:
            log.error('password is too short - use at least 6 characters')
            return False

        return password

    def create_test_admin_and_users(self):
        log.info('creating admin and regular test users')
        from rhodecode.tests import TEST_USER_ADMIN_LOGIN, \
            TEST_USER_ADMIN_PASS, TEST_USER_ADMIN_EMAIL, \
            TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS, \
            TEST_USER_REGULAR_EMAIL, TEST_USER_REGULAR2_LOGIN, \
            TEST_USER_REGULAR2_PASS, TEST_USER_REGULAR2_EMAIL

        self.create_user(TEST_USER_ADMIN_LOGIN, TEST_USER_ADMIN_PASS,
                         TEST_USER_ADMIN_EMAIL, True)

        self.create_user(TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS,
                         TEST_USER_REGULAR_EMAIL, False)

        self.create_user(TEST_USER_REGULAR2_LOGIN, TEST_USER_REGULAR2_PASS,
                         TEST_USER_REGULAR2_EMAIL, False)

    def create_ui_settings(self, repo_store_path):
        """
        Creates ui settings, fills out hooks
        and disables dotencode
        """
        settings_model = SettingsModel(sa=self.sa)

        # Build HOOKS
        hooks = [
            (RhodeCodeUi.HOOK_REPO_SIZE, 'python:vcsserver.hooks.repo_size'),

            # HG
            (RhodeCodeUi.HOOK_PRE_PULL, 'python:vcsserver.hooks.pre_pull'),
            (RhodeCodeUi.HOOK_PULL, 'python:vcsserver.hooks.log_pull_action'),
            (RhodeCodeUi.HOOK_PRE_PUSH, 'python:vcsserver.hooks.pre_push'),
            (RhodeCodeUi.HOOK_PUSH, 'python:vcsserver.hooks.log_push_action'),

        ]

        for key, value in hooks:
            hook_obj = settings_model.get_ui_by_key(key)
            hooks2 = hook_obj if hook_obj else RhodeCodeUi()
            hooks2.ui_section = 'hooks'
            hooks2.ui_key = key
            hooks2.ui_value = value
            self.sa.add(hooks2)

        # enable largefiles
        largefiles = RhodeCodeUi()
        largefiles.ui_section = 'extensions'
        largefiles.ui_key = 'largefiles'
        largefiles.ui_value = ''
        self.sa.add(largefiles)

        # set default largefiles cache dir, defaults to
        # /repo location/.cache/largefiles
        largefiles = RhodeCodeUi()
        largefiles.ui_section = 'largefiles'
        largefiles.ui_key = 'usercache'
        largefiles.ui_value = os.path.join(repo_store_path, '.cache',
                                           'largefiles')
        self.sa.add(largefiles)

        # enable hgsubversion disabled by default
        hgsubversion = RhodeCodeUi()
        hgsubversion.ui_section = 'extensions'
        hgsubversion.ui_key = 'hgsubversion'
        hgsubversion.ui_value = ''
        hgsubversion.ui_active = False
        self.sa.add(hgsubversion)

        # enable hggit disabled by default
        hggit = RhodeCodeUi()
        hggit.ui_section = 'extensions'
        hggit.ui_key = 'hggit'
        hggit.ui_value = ''
        hggit.ui_active = False
        self.sa.add(hggit)

        # set svn branch defaults
        branches = ["/branches/*", "/trunk"]
        tags = ["/tags/*"]

        for branch in branches:
            settings_model.create_ui_section_value(
                RhodeCodeUi.SVN_BRANCH_ID, branch)

        for tag in tags:
            settings_model.create_ui_section_value(RhodeCodeUi.SVN_TAG_ID, tag)

    def create_auth_plugin_options(self, skip_existing=False):
        """
        Create default auth plugin settings, and make it active

        :param skip_existing:
        """

        for k, v, t in [('auth_plugins', 'egg:rhodecode-enterprise-ce#rhodecode', 'list'),
                        ('auth_rhodecode_enabled', 'True', 'bool')]:
            if (skip_existing and
                    SettingsModel().get_setting_by_name(k) is not None):
                log.debug('Skipping option %s' % k)
                continue
            setting = RhodeCodeSetting(k, v, t)
            self.sa.add(setting)

    def create_default_options(self, skip_existing=False):
        """Creates default settings"""

        for k, v, t in [
            ('default_repo_enable_locking',  False, 'bool'),
            ('default_repo_enable_downloads', False, 'bool'),
            ('default_repo_enable_statistics', False, 'bool'),
            ('default_repo_private', False, 'bool'),
            ('default_repo_type', 'hg', 'unicode')]:

            if (skip_existing and
                    SettingsModel().get_setting_by_name(k) is not None):
                log.debug('Skipping option %s' % k)
                continue
            setting = RhodeCodeSetting(k, v, t)
            self.sa.add(setting)

    def fixup_groups(self):
        def_usr = User.get_default_user()
        for g in RepoGroup.query().all():
            g.group_name = g.get_new_name(g.name)
            self.sa.add(g)
            # get default perm
            default = UserRepoGroupToPerm.query()\
                .filter(UserRepoGroupToPerm.group == g)\
                .filter(UserRepoGroupToPerm.user == def_usr)\
                .scalar()

            if default is None:
                log.debug('missing default permission for group %s adding' % g)
                perm_obj = RepoGroupModel()._create_default_perms(g)
                self.sa.add(perm_obj)

    def reset_permissions(self, username):
        """
        Resets permissions to default state, useful when old systems had
        bad permissions, we must clean them up

        :param username:
        """
        default_user = User.get_by_username(username)
        if not default_user:
            return

        u2p = UserToPerm.query()\
            .filter(UserToPerm.user == default_user).all()
        fixed = False
        if len(u2p) != len(Permission.DEFAULT_USER_PERMISSIONS):
            for p in u2p:
                Session().delete(p)
            fixed = True
            self.populate_default_permissions()
        return fixed

    def update_repo_info(self):
        RepoModel.update_repoinfo()

    def config_prompt(self, test_repo_path='', retries=3):
        defaults = self.cli_args
        _path = defaults.get('repos_location')
        if retries == 3:
            log.info('Setting up repositories config')

        if _path is not None:
            path = _path
        elif not self.tests and not test_repo_path:
            path = raw_input(
                 'Enter a valid absolute path to store repositories. '
                 'All repositories in that path will be added automatically:'
            )
        else:
            path = test_repo_path
        path_ok = True

        # check proper dir
        if not os.path.isdir(path):
            path_ok = False
            log.error('Given path %s is not a valid directory' % (path,))

        elif not os.path.isabs(path):
            path_ok = False
            log.error('Given path %s is not an absolute path' % (path,))

        # check if path is at least readable.
        if not os.access(path, os.R_OK):
            path_ok = False
            log.error('Given path %s is not readable' % (path,))

        # check write access, warn user about non writeable paths
        elif not os.access(path, os.W_OK) and path_ok:
            log.warning('No write permission to given path %s' % (path,))

        q = ('Given path %s is not writeable, do you want to '
             'continue with read only mode ? [y/n]' % (path,))
        if not self.ask_ok(q):
                log.error('Canceled by user')
                sys.exit(-1)

        if retries == 0:
            sys.exit('max retries reached')
        if not path_ok:
            retries -= 1
            return self.config_prompt(test_repo_path, retries)

        real_path = os.path.normpath(os.path.realpath(path))

        if real_path != os.path.normpath(path):
            q = ('Path looks like a symlink, RhodeCode Enterprise will store '
                 'given path as %s ? [y/n]') % (real_path,)
            if not self.ask_ok(q):
                log.error('Canceled by user')
                sys.exit(-1)

        return real_path

    def create_settings(self, path):

        self.create_ui_settings(path)

        ui_config = [
            ('web', 'push_ssl', 'false'),
            ('web', 'allow_archive', 'gz zip bz2'),
            ('web', 'allow_push', '*'),
            ('web', 'baseurl', '/'),
            ('paths', '/', path),
            ('phases', 'publish', 'true')
        ]
        for section, key, value in ui_config:
            ui_conf = RhodeCodeUi()
            setattr(ui_conf, 'ui_section', section)
            setattr(ui_conf, 'ui_key', key)
            setattr(ui_conf, 'ui_value', value)
            self.sa.add(ui_conf)

        # rhodecode app settings
        settings = [
            ('realm', 'RhodeCode', 'unicode'),
            ('title', '', 'unicode'),
            ('pre_code', '', 'unicode'),
            ('post_code', '', 'unicode'),
            ('show_public_icon', True, 'bool'),
            ('show_private_icon', True, 'bool'),
            ('stylify_metatags', False, 'bool'),
            ('dashboard_items', 100, 'int'),
            ('admin_grid_items', 25, 'int'),
            ('show_version', True, 'bool'),
            ('use_gravatar', False, 'bool'),
            ('gravatar_url', User.DEFAULT_GRAVATAR_URL, 'unicode'),
            ('clone_uri_tmpl', Repository.DEFAULT_CLONE_URI, 'unicode'),
            ('support_url', '', 'unicode'),
            ('update_url', RhodeCodeSetting.DEFAULT_UPDATE_URL, 'unicode'),
            ('show_revision_number', True, 'bool'),
            ('show_sha_length', 12, 'int'),
        ]

        for key, val, type_ in settings:
            sett = RhodeCodeSetting(key, val, type_)
            self.sa.add(sett)

        self.create_auth_plugin_options()
        self.create_default_options()

        log.info('created ui config')

    def create_user(self, username, password, email='', admin=False,
                    strict_creation_check=True, api_key=None):
        log.info('creating user %s' % username)
        user = UserModel().create_or_update(
            username, password, email, firstname='RhodeCode', lastname='Admin',
            active=True, admin=admin, extern_type="rhodecode",
            strict_creation_check=strict_creation_check)

        if api_key:
            log.info('setting a provided api key for the user %s', username)
            user.api_key = api_key

    def create_default_user(self):
        log.info('creating default user')
        # create default user for handling default permissions.
        user = UserModel().create_or_update(username=User.DEFAULT_USER,
                                            password=str(uuid.uuid1())[:20],
                                            email=User.DEFAULT_USER_EMAIL,
                                            firstname='Anonymous',
                                            lastname='User',
                                            strict_creation_check=False)
        # based on configuration options activate/deactive this user which
        # controlls anonymous access
        if self.cli_args.get('public_access') is False:
            log.info('Public access disabled')
            user.active = False
            Session().add(user)
            Session().commit()

    def create_permissions(self):
        """
        Creates all permissions defined in the system
        """
        # module.(access|create|change|delete)_[name]
        # module.(none|read|write|admin)
        log.info('creating permissions')
        PermissionModel(self.sa).create_permissions()

    def populate_default_permissions(self):
        """
        Populate default permissions. It will create only the default
        permissions that are missing, and not alter already defined ones
        """
        log.info('creating default user permissions')
        PermissionModel(self.sa).create_default_user_permissions(user=User.DEFAULT_USER)
