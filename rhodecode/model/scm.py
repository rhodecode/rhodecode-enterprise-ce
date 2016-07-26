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
Scm model for RhodeCode
"""

import os.path
import re
import sys
import time
import traceback
import logging
import cStringIO
import pkg_resources

import pylons
from pylons.i18n.translation import _
from sqlalchemy import func
from zope.cachedescriptors.property import Lazy as LazyProperty

import rhodecode
from rhodecode.lib.vcs import get_backend
from rhodecode.lib.vcs.exceptions import RepositoryError, NodeNotChangedError
from rhodecode.lib.vcs.nodes import FileNode
from rhodecode.lib.vcs.backends.base import EmptyCommit
from rhodecode.lib import helpers as h

from rhodecode.lib.auth import (
    HasRepoPermissionAny, HasRepoGroupPermissionAny,
    HasUserGroupPermissionAny)
from rhodecode.lib.exceptions import NonRelativePathError, IMCCommitError
from rhodecode.lib import hooks_utils, caches
from rhodecode.lib.utils import (
    get_filesystem_repos, action_logger, make_db_config)
from rhodecode.lib.utils2 import (
    safe_str, safe_unicode, get_server_url, md5)
from rhodecode.model import BaseModel
from rhodecode.model.db import (
    Repository, CacheKey, UserFollowing, UserLog, User, RepoGroup,
    PullRequest, DbMigrateVersion)
from rhodecode.model.settings import VcsSettingsModel

log = logging.getLogger(__name__)


class UserTemp(object):
    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return "<%s('id:%s')>" % (self.__class__.__name__, self.user_id)


class RepoTemp(object):
    def __init__(self, repo_id):
        self.repo_id = repo_id

    def __repr__(self):
        return "<%s('id:%s')>" % (self.__class__.__name__, self.repo_id)


class SimpleCachedRepoList(object):
    """
    Lighter version of of iteration of repos without the scm initialisation,
    and with cache usage
    """
    def __init__(self, db_repo_list, repos_path, order_by=None, perm_set=None):
        self.db_repo_list = db_repo_list
        self.repos_path = repos_path
        self.order_by = order_by
        self.reversed = (order_by or '').startswith('-')
        if not perm_set:
            perm_set = ['repository.read', 'repository.write',
                        'repository.admin']
        self.perm_set = perm_set

    def __len__(self):
        return len(self.db_repo_list)

    def __repr__(self):
        return '<%s (%s)>' % (self.__class__.__name__, self.__len__())

    def __iter__(self):
        for dbr in self.db_repo_list:
            # check permission at this level
            has_perm = HasRepoPermissionAny(*self.perm_set)(
                dbr.repo_name, 'SimpleCachedRepoList check')
            if not has_perm:
                continue

            tmp_d = {
                'name': dbr.repo_name,
                'dbrepo': dbr.get_dict(),
                'dbrepo_fork': dbr.fork.get_dict() if dbr.fork else {}
            }
            yield tmp_d


class _PermCheckIterator(object):

    def __init__(
            self, obj_list, obj_attr, perm_set, perm_checker,
            extra_kwargs=None):
        """
        Creates iterator from given list of objects, additionally
        checking permission for them from perm_set var

        :param obj_list: list of db objects
        :param obj_attr: attribute of object to pass into perm_checker
        :param perm_set: list of permissions to check
        :param perm_checker: callable to check permissions against
        """
        self.obj_list = obj_list
        self.obj_attr = obj_attr
        self.perm_set = perm_set
        self.perm_checker = perm_checker
        self.extra_kwargs = extra_kwargs or {}

    def __len__(self):
        return len(self.obj_list)

    def __repr__(self):
        return '<%s (%s)>' % (self.__class__.__name__, self.__len__())

    def __iter__(self):
        checker = self.perm_checker(*self.perm_set)
        for db_obj in self.obj_list:
            # check permission at this level
            name = getattr(db_obj, self.obj_attr, None)
            if not checker(name, self.__class__.__name__, **self.extra_kwargs):
                continue

            yield db_obj


class RepoList(_PermCheckIterator):

    def __init__(self, db_repo_list, perm_set=None, extra_kwargs=None):
        if not perm_set:
            perm_set = [
                'repository.read', 'repository.write', 'repository.admin']

        super(RepoList, self).__init__(
            obj_list=db_repo_list,
            obj_attr='repo_name', perm_set=perm_set,
            perm_checker=HasRepoPermissionAny,
            extra_kwargs=extra_kwargs)


class RepoGroupList(_PermCheckIterator):

    def __init__(self, db_repo_group_list, perm_set=None, extra_kwargs=None):
        if not perm_set:
            perm_set = ['group.read', 'group.write', 'group.admin']

        super(RepoGroupList, self).__init__(
            obj_list=db_repo_group_list,
            obj_attr='group_name', perm_set=perm_set,
            perm_checker=HasRepoGroupPermissionAny,
            extra_kwargs=extra_kwargs)


class UserGroupList(_PermCheckIterator):

    def __init__(self, db_user_group_list, perm_set=None, extra_kwargs=None):
        if not perm_set:
            perm_set = ['usergroup.read', 'usergroup.write', 'usergroup.admin']

        super(UserGroupList, self).__init__(
            obj_list=db_user_group_list,
            obj_attr='users_group_name', perm_set=perm_set,
            perm_checker=HasUserGroupPermissionAny,
            extra_kwargs=extra_kwargs)


class ScmModel(BaseModel):
    """
    Generic Scm Model
    """

    @LazyProperty
    def repos_path(self):
        """
        Gets the repositories root path from database
        """

        settings_model = VcsSettingsModel(sa=self.sa)
        return settings_model.get_repos_location()

    def repo_scan(self, repos_path=None):
        """
        Listing of repositories in given path. This path should not be a
        repository itself. Return a dictionary of repository objects

        :param repos_path: path to directory containing repositories
        """

        if repos_path is None:
            repos_path = self.repos_path

        log.info('scanning for repositories in %s', repos_path)

        config = make_db_config()
        config.set('extensions', 'largefiles', '')
        repos = {}

        for name, path in get_filesystem_repos(repos_path, recursive=True):
            # name need to be decomposed and put back together using the /
            # since this is internal storage separator for rhodecode
            name = Repository.normalize_repo_name(name)

            try:
                if name in repos:
                    raise RepositoryError('Duplicate repository name %s '
                                          'found in %s' % (name, path))
                elif path[0] in rhodecode.BACKENDS:
                    klass = get_backend(path[0])
                    repos[name] = klass(path[1], config=config)
            except OSError:
                continue
        log.debug('found %s paths with repositories', len(repos))
        return repos

    def get_repos(self, all_repos=None, sort_key=None):
        """
        Get all repositories from db and for each repo create it's
        backend instance and fill that backed with information from database

        :param all_repos: list of repository names as strings
            give specific repositories list, good for filtering

        :param sort_key: initial sorting of repositories
        """
        if all_repos is None:
            all_repos = self.sa.query(Repository)\
                .filter(Repository.group_id == None)\
                .order_by(func.lower(Repository.repo_name)).all()
        repo_iter = SimpleCachedRepoList(
            all_repos, repos_path=self.repos_path, order_by=sort_key)
        return repo_iter

    def get_repo_groups(self, all_groups=None):
        if all_groups is None:
            all_groups = RepoGroup.query()\
                .filter(RepoGroup.group_parent_id == None).all()
        return [x for x in RepoGroupList(all_groups)]

    def mark_for_invalidation(self, repo_name, delete=False):
        """
        Mark caches of this repo invalid in the database. `delete` flag
        removes the cache entries

        :param repo_name: the repo_name for which caches should be marked
            invalid, or deleted
        :param delete: delete the entry keys instead of setting bool
            flag on them
        """
        CacheKey.set_invalidate(repo_name, delete=delete)
        repo = Repository.get_by_repo_name(repo_name)

        if repo:
            config = repo._config
            config.set('extensions', 'largefiles', '')
            repo.update_commit_cache(config=config, cs_cache=None)
            caches.clear_repo_caches(repo_name)

    def toggle_following_repo(self, follow_repo_id, user_id):

        f = self.sa.query(UserFollowing)\
            .filter(UserFollowing.follows_repo_id == follow_repo_id)\
            .filter(UserFollowing.user_id == user_id).scalar()

        if f is not None:
            try:
                self.sa.delete(f)
                action_logger(UserTemp(user_id),
                              'stopped_following_repo',
                              RepoTemp(follow_repo_id))
                return
            except Exception:
                log.error(traceback.format_exc())
                raise

        try:
            f = UserFollowing()
            f.user_id = user_id
            f.follows_repo_id = follow_repo_id
            self.sa.add(f)

            action_logger(UserTemp(user_id),
                          'started_following_repo',
                          RepoTemp(follow_repo_id))
        except Exception:
            log.error(traceback.format_exc())
            raise

    def toggle_following_user(self, follow_user_id, user_id):
        f = self.sa.query(UserFollowing)\
            .filter(UserFollowing.follows_user_id == follow_user_id)\
            .filter(UserFollowing.user_id == user_id).scalar()

        if f is not None:
            try:
                self.sa.delete(f)
                return
            except Exception:
                log.error(traceback.format_exc())
                raise

        try:
            f = UserFollowing()
            f.user_id = user_id
            f.follows_user_id = follow_user_id
            self.sa.add(f)
        except Exception:
            log.error(traceback.format_exc())
            raise

    def is_following_repo(self, repo_name, user_id, cache=False):
        r = self.sa.query(Repository)\
            .filter(Repository.repo_name == repo_name).scalar()

        f = self.sa.query(UserFollowing)\
            .filter(UserFollowing.follows_repository == r)\
            .filter(UserFollowing.user_id == user_id).scalar()

        return f is not None

    def is_following_user(self, username, user_id, cache=False):
        u = User.get_by_username(username)

        f = self.sa.query(UserFollowing)\
            .filter(UserFollowing.follows_user == u)\
            .filter(UserFollowing.user_id == user_id).scalar()

        return f is not None

    def get_followers(self, repo):
        repo = self._get_repo(repo)

        return self.sa.query(UserFollowing)\
            .filter(UserFollowing.follows_repository == repo).count()

    def get_forks(self, repo):
        repo = self._get_repo(repo)
        return self.sa.query(Repository)\
            .filter(Repository.fork == repo).count()

    def get_pull_requests(self, repo):
        repo = self._get_repo(repo)
        return self.sa.query(PullRequest)\
            .filter(PullRequest.target_repo == repo)\
            .filter(PullRequest.status != PullRequest.STATUS_CLOSED).count()

    def mark_as_fork(self, repo, fork, user):
        repo = self._get_repo(repo)
        fork = self._get_repo(fork)
        if fork and repo.repo_id == fork.repo_id:
            raise Exception("Cannot set repository as fork of itself")

        if fork and repo.repo_type != fork.repo_type:
            raise RepositoryError(
                "Cannot set repository as fork of repository with other type")

        repo.fork = fork
        self.sa.add(repo)
        return repo

    def pull_changes(self, repo, username):
        dbrepo = self._get_repo(repo)
        clone_uri = dbrepo.clone_uri
        if not clone_uri:
            raise Exception("This repository doesn't have a clone uri")

        repo = dbrepo.scm_instance(cache=False)
        # TODO: marcink fix this an re-enable since we need common logic
        # for hg/git remove hooks so we don't trigger them on fetching
        # commits from remote
        repo.config.clear_section('hooks')

        repo_name = dbrepo.repo_name
        try:
            # TODO: we need to make sure those operations call proper hooks !
            repo.pull(clone_uri)

            self.mark_for_invalidation(repo_name)
        except Exception:
            log.error(traceback.format_exc())
            raise

    def commit_change(self, repo, repo_name, commit, user, author, message,
                      content, f_path):
        """
        Commits changes

        :param repo: SCM instance

        """
        user = self._get_user(user)

        # decoding here will force that we have proper encoded values
        # in any other case this will throw exceptions and deny commit
        content = safe_str(content)
        path = safe_str(f_path)
        # message and author needs to be unicode
        # proper backend should then translate that into required type
        message = safe_unicode(message)
        author = safe_unicode(author)
        imc = repo.in_memory_commit
        imc.change(FileNode(path, content, mode=commit.get_file_mode(f_path)))
        try:
            # TODO: handle pre-push action !
            tip = imc.commit(
                message=message, author=author, parents=[commit],
                branch=commit.branch)
        except Exception as e:
            log.error(traceback.format_exc())
            raise IMCCommitError(str(e))
        finally:
            # always clear caches, if commit fails we want fresh object also
            self.mark_for_invalidation(repo_name)

        # We trigger the post-push action
        hooks_utils.trigger_post_push_hook(
            username=user.username, action='push_local', repo_name=repo_name,
            repo_alias=repo.alias, commit_ids=[tip.raw_id])
        return tip

    def _sanitize_path(self, f_path):
        if f_path.startswith('/') or f_path.startswith('./') or '../' in f_path:
            raise NonRelativePathError('%s is not an relative path' % f_path)
        if f_path:
            f_path = os.path.normpath(f_path)
        return f_path

    def get_dirnode_metadata(self, commit, dir_node):
        if not dir_node.is_dir():
            return []

        data = []
        for node in dir_node:
            if not node.is_file():
                # we skip file-nodes
                continue

            last_commit = node.last_commit
            last_commit_date = last_commit.date
            data.append({
                'name': node.name,
                'size': h.format_byte_size_binary(node.size),
                'modified_at': h.format_date(last_commit_date),
                'modified_ts': last_commit_date.isoformat(),
                'revision': last_commit.revision,
                'short_id': last_commit.short_id,
                'message': h.escape(last_commit.message),
                'author': h.escape(last_commit.author),
                'user_profile': h.gravatar_with_user(last_commit.author),
            })

        return data

    def get_nodes(self, repo_name, commit_id, root_path='/', flat=True,
                  extended_info=False, content=False):
        """
        recursive walk in root dir and return a set of all path in that dir
        based on repository walk function

        :param repo_name: name of repository
        :param commit_id: commit id for which to list nodes
        :param root_path: root path to list
        :param flat: return as a list, if False returns a dict with description

        """
        _files = list()
        _dirs = list()
        try:
            _repo = self._get_repo(repo_name)
            commit = _repo.scm_instance().get_commit(commit_id=commit_id)
            root_path = root_path.lstrip('/')
            for __, dirs, files in commit.walk(root_path):
                for f in files:
                    _content = None
                    _data = f.unicode_path

                    if not flat:
                        _data = {
                            "name": f.unicode_path,
                            "type": "file",
                            }
                        if extended_info:
                            _data.update({
                                "md5": f.md5,
                                "binary": f.is_binary,
                                "size": f.size,
                                "extension": f.extension,
                                "mimetype": f.mimetype,
                                "lines": f.lines()[0]
                            })

                        if content:
                            full_content = None
                            if not f.is_binary:
                                full_content = safe_str(f.content)

                            _data.update({
                                "content": full_content,
                            })
                    _files.append(_data)
                for d in dirs:
                    _data = d.unicode_path
                    if not flat:
                        _data = {
                            "name": d.unicode_path,
                            "type": "dir",
                            }
                    if extended_info:
                        _data.update({
                            "md5": None,
                            "binary": None,
                            "size": None,
                            "extension": None,
                        })
                    if content:
                        _data.update({
                            "content": None
                        })
                    _dirs.append(_data)
        except RepositoryError:
            log.debug("Exception in get_nodes", exc_info=True)
            raise

        return _dirs, _files

    def create_nodes(self, user, repo, message, nodes, parent_commit=None,
                     author=None, trigger_push_hook=True):
        """
        Commits given multiple nodes into repo

        :param user: RhodeCode User object or user_id, the commiter
        :param repo: RhodeCode Repository object
        :param message: commit message
        :param nodes: mapping {filename:{'content':content},...}
        :param parent_commit: parent commit, can be empty than it's
           initial commit
        :param author: author of commit, cna be different that commiter
           only for git
        :param trigger_push_hook: trigger push hooks

        :returns: new commited commit
        """

        user = self._get_user(user)
        scm_instance = repo.scm_instance(cache=False)

        processed_nodes = []
        for f_path in nodes:
            f_path = self._sanitize_path(f_path)
            content = nodes[f_path]['content']
            f_path = safe_str(f_path)
            # decoding here will force that we have proper encoded values
            # in any other case this will throw exceptions and deny commit
            if isinstance(content, (basestring,)):
                content = safe_str(content)
            elif isinstance(content, (file, cStringIO.OutputType,)):
                content = content.read()
            else:
                raise Exception('Content is of unrecognized type %s' % (
                    type(content)
                ))
            processed_nodes.append((f_path, content))

        message = safe_unicode(message)
        commiter = user.full_contact
        author = safe_unicode(author) if author else commiter

        imc = scm_instance.in_memory_commit

        if not parent_commit:
            parent_commit = EmptyCommit(alias=scm_instance.alias)

        if isinstance(parent_commit, EmptyCommit):
            # EmptyCommit means we we're editing empty repository
            parents = None
        else:
            parents = [parent_commit]
        # add multiple nodes
        for path, content in processed_nodes:
            imc.add(FileNode(path, content=content))
        # TODO: handle pre push scenario
        tip = imc.commit(message=message,
                         author=author,
                         parents=parents,
                         branch=parent_commit.branch)

        self.mark_for_invalidation(repo.repo_name)
        if trigger_push_hook:
            hooks_utils.trigger_post_push_hook(
                username=user.username, action='push_local',
                repo_name=repo.repo_name, repo_alias=scm_instance.alias,
                commit_ids=[tip.raw_id])
        return tip

    def update_nodes(self, user, repo, message, nodes, parent_commit=None,
                     author=None, trigger_push_hook=True):
        user = self._get_user(user)
        scm_instance = repo.scm_instance(cache=False)

        message = safe_unicode(message)
        commiter = user.full_contact
        author = safe_unicode(author) if author else commiter

        imc = scm_instance.in_memory_commit

        if not parent_commit:
            parent_commit = EmptyCommit(alias=scm_instance.alias)

        if isinstance(parent_commit, EmptyCommit):
            # EmptyCommit means we we're editing empty repository
            parents = None
        else:
            parents = [parent_commit]

        # add multiple nodes
        for _filename, data in nodes.items():
            # new filename, can be renamed from the old one, also sanitaze
            # the path for any hack around relative paths like ../../ etc.
            filename = self._sanitize_path(data['filename'])
            old_filename = self._sanitize_path(_filename)
            content = data['content']

            filenode = FileNode(old_filename, content=content)
            op = data['op']
            if op == 'add':
                imc.add(filenode)
            elif op == 'del':
                imc.remove(filenode)
            elif op == 'mod':
                if filename != old_filename:
                    # TODO: handle renames more efficient, needs vcs lib
                    # changes
                    imc.remove(filenode)
                    imc.add(FileNode(filename, content=content))
                else:
                    imc.change(filenode)

        try:
            # TODO: handle pre push scenario
            # commit changes
            tip = imc.commit(message=message,
                             author=author,
                             parents=parents,
                             branch=parent_commit.branch)
        except NodeNotChangedError:
            raise
        except Exception as e:
            log.exception("Unexpected exception during call to imc.commit")
            raise IMCCommitError(str(e))
        finally:
            # always clear caches, if commit fails we want fresh object also
            self.mark_for_invalidation(repo.repo_name)

        if trigger_push_hook:
            hooks_utils.trigger_post_push_hook(
                username=user.username, action='push_local',
                repo_name=repo.repo_name, repo_alias=scm_instance.alias,
                commit_ids=[tip.raw_id])

    def delete_nodes(self, user, repo, message, nodes, parent_commit=None,
                     author=None, trigger_push_hook=True):
        """
        Deletes given multiple nodes into `repo`

        :param user: RhodeCode User object or user_id, the committer
        :param repo: RhodeCode Repository object
        :param message: commit message
        :param nodes: mapping {filename:{'content':content},...}
        :param parent_commit: parent commit, can be empty than it's initial
           commit
        :param author: author of commit, cna be different that commiter only
           for git
        :param trigger_push_hook: trigger push hooks

        :returns: new commit after deletion
        """

        user = self._get_user(user)
        scm_instance = repo.scm_instance(cache=False)

        processed_nodes = []
        for f_path in nodes:
            f_path = self._sanitize_path(f_path)
            # content can be empty but for compatabilty it allows same dicts
            # structure as add_nodes
            content = nodes[f_path].get('content')
            processed_nodes.append((f_path, content))

        message = safe_unicode(message)
        commiter = user.full_contact
        author = safe_unicode(author) if author else commiter

        imc = scm_instance.in_memory_commit

        if not parent_commit:
            parent_commit = EmptyCommit(alias=scm_instance.alias)

        if isinstance(parent_commit, EmptyCommit):
            # EmptyCommit means we we're editing empty repository
            parents = None
        else:
            parents = [parent_commit]
        # add multiple nodes
        for path, content in processed_nodes:
            imc.remove(FileNode(path, content=content))

        # TODO: handle pre push scenario
        tip = imc.commit(message=message,
                         author=author,
                         parents=parents,
                         branch=parent_commit.branch)

        self.mark_for_invalidation(repo.repo_name)
        if trigger_push_hook:
            hooks_utils.trigger_post_push_hook(
                username=user.username, action='push_local',
                repo_name=repo.repo_name, repo_alias=scm_instance.alias,
                commit_ids=[tip.raw_id])
        return tip

    def strip(self, repo, commit_id, branch):
        scm_instance = repo.scm_instance(cache=False)
        scm_instance.config.clear_section('hooks')
        scm_instance.strip(commit_id, branch)
        self.mark_for_invalidation(repo.repo_name)

    def get_unread_journal(self):
        return self.sa.query(UserLog).count()

    def get_repo_landing_revs(self, repo=None):
        """
        Generates select option with tags branches and bookmarks (for hg only)
        grouped by type

        :param repo:
        """

        hist_l = []
        choices = []
        repo = self._get_repo(repo)
        hist_l.append(['rev:tip', _('latest tip')])
        choices.append('rev:tip')
        if not repo:
            return choices, hist_l

        repo = repo.scm_instance()

        branches_group = (
            [(u'branch:%s' % safe_unicode(b), safe_unicode(b))
                for b in repo.branches],
            _("Branches"))
        hist_l.append(branches_group)
        choices.extend([x[0] for x in branches_group[0]])

        if repo.alias == 'hg':
            bookmarks_group = (
                [(u'book:%s' % safe_unicode(b), safe_unicode(b))
                    for b in repo.bookmarks],
                _("Bookmarks"))
            hist_l.append(bookmarks_group)
            choices.extend([x[0] for x in bookmarks_group[0]])

        tags_group = (
            [(u'tag:%s' % safe_unicode(t), safe_unicode(t))
                for t in repo.tags],
            _("Tags"))
        hist_l.append(tags_group)
        choices.extend([x[0] for x in tags_group[0]])

        return choices, hist_l

    def install_git_hook(self, repo, force_create=False):
        """
        Creates a rhodecode hook inside a git repository

        :param repo: Instance of VCS repo
        :param force_create: Create even if same name hook exists
        """

        loc = os.path.join(repo.path, 'hooks')
        if not repo.bare:
            loc = os.path.join(repo.path, '.git', 'hooks')
        if not os.path.isdir(loc):
            os.makedirs(loc, mode=0777)

        tmpl_post = pkg_resources.resource_string(
            'rhodecode', '/'.join(
                ('config', 'hook_templates', 'git_post_receive.py.tmpl')))
        tmpl_pre = pkg_resources.resource_string(
            'rhodecode', '/'.join(
                ('config', 'hook_templates', 'git_pre_receive.py.tmpl')))

        for h_type, tmpl in [('pre', tmpl_pre), ('post', tmpl_post)]:
            _hook_file = os.path.join(loc, '%s-receive' % h_type)
            log.debug('Installing git hook in repo %s', repo)
            _rhodecode_hook = _check_rhodecode_hook(_hook_file)

            if _rhodecode_hook or force_create:
                log.debug('writing %s hook file !', h_type)
                try:
                    with open(_hook_file, 'wb') as f:
                        tmpl = tmpl.replace('_TMPL_', rhodecode.__version__)
                        tmpl = tmpl.replace('_ENV_', sys.executable)
                        f.write(tmpl)
                    os.chmod(_hook_file, 0755)
                except IOError:
                    log.exception('error writing hook file %s', _hook_file)
            else:
                log.debug('skipping writing hook file')

    def install_svn_hooks(self, repo, force_create=False):
        """
        Creates rhodecode hooks inside a svn repository

        :param repo: Instance of VCS repo
        :param force_create: Create even if same name hook exists
        """
        hooks_path = os.path.join(repo.path, 'hooks')
        if not os.path.isdir(hooks_path):
            os.makedirs(hooks_path)
        post_commit_tmpl = pkg_resources.resource_string(
            'rhodecode', '/'.join(
                ('config', 'hook_templates', 'svn_post_commit_hook.py.tmpl')))
        pre_commit_template = pkg_resources.resource_string(
            'rhodecode', '/'.join(
                ('config', 'hook_templates', 'svn_pre_commit_hook.py.tmpl')))
        templates = {
            'post-commit': post_commit_tmpl,
            'pre-commit': pre_commit_template
        }
        for filename in templates:
            _hook_file = os.path.join(hooks_path, filename)
            _rhodecode_hook = _check_rhodecode_hook(_hook_file)
            if _rhodecode_hook or force_create:
                log.debug('writing %s hook file !', filename)
                template = templates[filename]
                try:
                    with open(_hook_file, 'wb') as f:
                        template = template.replace(
                            '_TMPL_', rhodecode.__version__)
                        template = template.replace('_ENV_', sys.executable)
                        f.write(template)
                    os.chmod(_hook_file, 0755)
                except IOError:
                    log.exception('error writing hook file %s', filename)
            else:
                log.debug('skipping writing hook file')

    def install_hooks(self, repo, repo_type):
        if repo_type == 'git':
            self.install_git_hook(repo)
        elif repo_type == 'svn':
            self.install_svn_hooks(repo)

    def get_server_info(self, environ=None):
        import platform
        import rhodecode
        import pkg_resources
        from rhodecode.model.meta import Base as sql_base, Session
        from sqlalchemy.engine import url
        from rhodecode.lib.base import get_server_ip_addr, get_server_port
        from rhodecode.lib.vcs.backends.git import discover_git_version
        from rhodecode.model.gist import GIST_STORE_LOC

        try:
            # cygwin cannot have yet psutil support.
            import psutil
        except ImportError:
            psutil = None

        environ = environ or {}
        _NA = 'NOT AVAILABLE'
        _memory = _NA
        _uptime = _NA
        _boot_time = _NA
        _cpu = _NA
        _disk = dict(percent=0, used=0, total=0, error='')
        _load = {'1_min': _NA, '5_min': _NA, '15_min': _NA}

        model = VcsSettingsModel()
        storage_path = model.get_repos_location()
        gist_storage_path = os.path.join(storage_path, GIST_STORE_LOC)
        archive_storage_path = rhodecode.CONFIG.get('archive_cache_dir', '')
        search_index_storage_path = rhodecode.CONFIG.get('search.location', '')

        if psutil:
            # disk storage
            try:
                _disk = dict(psutil.disk_usage(storage_path)._asdict())
            except Exception as e:
                log.exception('Failed to fetch disk info')
                _disk = {'percent': 0, 'used': 0, 'total': 0, 'error': str(e)}

            # memory
            _memory = dict(psutil.virtual_memory()._asdict())
            _memory['percent2'] = psutil._common.usage_percent(
                (_memory['total'] - _memory['free']),
                _memory['total'], 1)

            # load averages
            if hasattr(psutil.os, 'getloadavg'):
                _load = dict(zip(
                    ['1_min', '5_min', '15_min'], psutil.os.getloadavg()))
            _uptime = time.time() - psutil.boot_time()
            _boot_time = psutil.boot_time()
            _cpu = psutil.cpu_percent(0.5)

        mods = dict([(p.project_name, p.version)
                     for p in pkg_resources.working_set])

        def get_storage_size(storage_path):
            sizes = []
            for file_ in os.listdir(storage_path):
                storage_file = os.path.join(storage_path, file_)
                if os.path.isfile(storage_file):
                    try:
                        sizes.append(os.path.getsize(storage_file))
                    except OSError:
                        log.exception('Failed to get size of storage file %s',
                                      storage_file)
                        pass

            return sum(sizes)

        # archive cache storage
        _disk_archive = {'percent': 0, 'used': 0, 'total': 0}
        try:
            archive_storage_path_exists = os.path.isdir(
                archive_storage_path)
            if archive_storage_path and archive_storage_path_exists:
                used = get_storage_size(archive_storage_path)
                _disk_archive.update({
                    'used': used,
                    'total': used,
                })
        except Exception as e:
            log.exception('failed to fetch archive cache storage')
            _disk_archive['error'] = str(e)

        # search index storage
        _disk_index = {'percent': 0, 'used': 0, 'total': 0}
        try:
            search_index_storage_path_exists = os.path.isdir(
                search_index_storage_path)
            if search_index_storage_path_exists:
                used = get_storage_size(search_index_storage_path)
                _disk_index.update({
                    'percent': 100,
                    'used': used,
                    'total': used,
                })
        except Exception as e:
            log.exception('failed to fetch search index storage')
            _disk_index['error'] = str(e)

        # gist storage
        _disk_gist = {'percent': 0, 'used': 0, 'total': 0, 'items': 0}
        try:
            items_count = 0
            used = 0
            for root, dirs, files in os.walk(safe_str(gist_storage_path)):
                if root == gist_storage_path:
                    items_count = len(dirs)

                for f in files:
                    try:
                        used += os.path.getsize(os.path.join(root, f))
                    except OSError:
                        pass
            _disk_gist.update({
                'percent': 100,
                'used': used,
                'total': used,
                'items': items_count
            })
        except Exception as e:
            log.exception('failed to fetch gist storage items')
            _disk_gist['error'] = str(e)

        # GIT info
        git_ver = discover_git_version()

        # SVN info
        # TODO: johbo: Add discover_svn_version to replace this code.
        try:
            import svn.core
            svn_ver = svn.core.SVN_VERSION
        except ImportError:
            svn_ver = None

        # DB stuff
        db_info = url.make_url(rhodecode.CONFIG['sqlalchemy.db1.url'])
        db_type = db_info.__to_string__()
        try:
            engine = sql_base.metadata.bind
            db_server_info = engine.dialect._get_server_version_info(
                Session.connection(bind=engine))
            db_version = '%s %s' % (db_info.drivername,
                                    '.'.join(map(str, db_server_info)))
        except Exception:
            log.exception('failed to fetch db version')
            db_version = '%s %s' % (db_info.drivername, '?')

        db_migrate = DbMigrateVersion.query().filter(
            DbMigrateVersion.repository_id == 'rhodecode_db_migrations').one()
        db_migrate_version = db_migrate.version

        info = {
            'py_version': ' '.join(platform._sys_version()),
            'py_path': sys.executable,
            'py_modules': sorted(mods.items(), key=lambda k: k[0].lower()),

            'platform': safe_unicode(platform.platform()),
            'storage': storage_path,
            'archive_storage': archive_storage_path,
            'index_storage': search_index_storage_path,
            'gist_storage': gist_storage_path,


            'db_type': db_type,
            'db_version': db_version,
            'db_migrate_version': db_migrate_version,

            'rhodecode_version': rhodecode.__version__,
            'rhodecode_config_ini': rhodecode.CONFIG.get('__file__'),
            'server_ip': '%s:%s' % (
                get_server_ip_addr(environ, log_errors=False),
                get_server_port(environ)
            ),
            'server_id': rhodecode.CONFIG.get('instance_id'),

            'git_version': safe_unicode(git_ver),
            'hg_version': mods.get('mercurial'),
            'svn_version': svn_ver,

            'uptime': _uptime,
            'boot_time': _boot_time,
            'load': _load,
            'cpu': _cpu,
            'memory': _memory,
            'disk': _disk,
            'disk_archive': _disk_archive,
            'disk_gist': _disk_gist,
            'disk_index': _disk_index,
        }
        return info


def _check_rhodecode_hook(hook_path):
    """
    Check if the hook was created by RhodeCode
    """
    if not os.path.exists(hook_path):
        return True

    log.debug('hook exists, checking if it is from rhodecode')
    hook_content = _read_hook(hook_path)
    matches = re.search(r'(?:RC_HOOK_VER)\s*=\s*(.*)', hook_content)
    if matches:
        try:
            version = matches.groups()[0]
            log.debug('got %s, it is rhodecode', version)
            return True
        except Exception:
            log.exception("Exception while reading the hook version.")

    return False


def _read_hook(hook_path):
    with open(hook_path, 'rb') as f:
        content = f.read()
    return content