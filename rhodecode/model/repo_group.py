# -*- coding: utf-8 -*-

# Copyright (C) 2011-2016  RhodeCode GmbH
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
repo group model for RhodeCode
"""


import datetime
import itertools
import logging
import os
import shutil
import traceback

from zope.cachedescriptors.property import Lazy as LazyProperty

from rhodecode.model import BaseModel
from rhodecode.model.db import (
    RepoGroup, UserRepoGroupToPerm, User, Permission, UserGroupRepoGroupToPerm,
    UserGroup, Repository)
from rhodecode.model.settings import VcsSettingsModel
from rhodecode.lib.caching_query import FromCache
from rhodecode.lib.utils2 import action_logger_generic

log = logging.getLogger(__name__)


class RepoGroupModel(BaseModel):

    cls = RepoGroup
    PERSONAL_GROUP_DESC = '[personal] repo group: owner `%(username)s`'

    def _get_user_group(self, users_group):
        return self._get_instance(UserGroup, users_group,
                                  callback=UserGroup.get_by_group_name)

    def _get_repo_group(self, repo_group):
        return self._get_instance(RepoGroup, repo_group,
                                  callback=RepoGroup.get_by_group_name)

    @LazyProperty
    def repos_path(self):
        """
        Gets the repositories root path from database
        """

        settings_model = VcsSettingsModel(sa=self.sa)
        return settings_model.get_repos_location()

    def get_by_group_name(self, repo_group_name, cache=None):
        repo = self.sa.query(RepoGroup) \
            .filter(RepoGroup.group_name == repo_group_name)

        if cache:
            repo = repo.options(FromCache(
                "sql_cache_short", "get_repo_group_%s" % repo_group_name))
        return repo.scalar()

    def _create_default_perms(self, new_group):
        # create default permission
        default_perm = 'group.read'
        def_user = User.get_default_user()
        for p in def_user.user_perms:
            if p.permission.permission_name.startswith('group.'):
                default_perm = p.permission.permission_name
                break

        repo_group_to_perm = UserRepoGroupToPerm()
        repo_group_to_perm.permission = Permission.get_by_key(default_perm)

        repo_group_to_perm.group = new_group
        repo_group_to_perm.user_id = def_user.user_id
        return repo_group_to_perm

    def _get_group_name_and_parent(self, group_name_full, repo_in_path=False):
        """
        Get's the group name and a parent group name from given group name.
        If repo_in_path is set to truth, we asume the full path also includes
        repo name, in such case we clean the last element.

        :param group_name_full:
        """
        split_paths = 1
        if repo_in_path:
            split_paths = 2
        _parts = group_name_full.rsplit(RepoGroup.url_sep(), split_paths)

        if repo_in_path and len(_parts) > 1:
            # such case last element is the repo_name
            _parts.pop(-1)
        group_name_cleaned = _parts[-1]  # just the group name
        parent_repo_group_name = None

        if len(_parts) > 1:
            parent_repo_group_name = _parts[0]

        if parent_repo_group_name:
            parent_group = RepoGroup.get_by_group_name(parent_repo_group_name)

        return group_name_cleaned, parent_repo_group_name

    def check_exist_filesystem(self, group_name, exc_on_failure=True):
        create_path = os.path.join(self.repos_path, group_name)
        log.debug('creating new group in %s', create_path)

        if os.path.isdir(create_path):
            if exc_on_failure:
                raise Exception('That directory already exists !')
            return False
        return True

    def _create_group(self, group_name):
        """
        makes repository group on filesystem

        :param repo_name:
        :param parent_id:
        """

        self.check_exist_filesystem(group_name)
        create_path = os.path.join(self.repos_path, group_name)
        log.debug('creating new group in %s', create_path)
        os.makedirs(create_path, mode=0755)
        log.debug('created group in %s', create_path)

    def _rename_group(self, old, new):
        """
        Renames a group on filesystem

        :param group_name:
        """

        if old == new:
            log.debug('skipping group rename')
            return

        log.debug('renaming repository group from %s to %s', old, new)

        old_path = os.path.join(self.repos_path, old)
        new_path = os.path.join(self.repos_path, new)

        log.debug('renaming repos paths from %s to %s', old_path, new_path)

        if os.path.isdir(new_path):
            raise Exception('Was trying to rename to already '
                            'existing dir %s' % new_path)
        shutil.move(old_path, new_path)

    def _delete_filesystem_group(self, group, force_delete=False):
        """
        Deletes a group from a filesystem

        :param group: instance of group from database
        :param force_delete: use shutil rmtree to remove all objects
        """
        paths = group.full_path.split(RepoGroup.url_sep())
        paths = os.sep.join(paths)

        rm_path = os.path.join(self.repos_path, paths)
        log.info("Removing group %s", rm_path)
        # delete only if that path really exists
        if os.path.isdir(rm_path):
            if force_delete:
                shutil.rmtree(rm_path)
            else:
                # archive that group`
                _now = datetime.datetime.now()
                _ms = str(_now.microsecond).rjust(6, '0')
                _d = 'rm__%s_GROUP_%s' % (
                    _now.strftime('%Y%m%d_%H%M%S_' + _ms), group.name)
                shutil.move(rm_path, os.path.join(self.repos_path, _d))

    def create(self, group_name, group_description, owner, just_db=False,
               copy_permissions=False, commit_early=True):

        (group_name_cleaned,
         parent_group_name) = RepoGroupModel()._get_group_name_and_parent(group_name)

        parent_group = None
        if parent_group_name:
            parent_group = self._get_repo_group(parent_group_name)

        # becase we are doing a cleanup, we need to check if such directory
        # already exists. If we don't do that we can accidentally delete existing
        # directory via cleanup that can cause data issues, since delete does a
        # folder rename to special syntax later cleanup functions can delete this
        cleanup_group = self.check_exist_filesystem(group_name,
                                                    exc_on_failure=False)
        try:
            user = self._get_user(owner)
            new_repo_group = RepoGroup()
            new_repo_group.user = user
            new_repo_group.group_description = group_description or group_name
            new_repo_group.parent_group = parent_group
            new_repo_group.group_name = group_name

            self.sa.add(new_repo_group)

            # create an ADMIN permission for owner except if we're super admin,
            # later owner should go into the owner field of groups
            if not user.is_admin:
                self.grant_user_permission(repo_group=new_repo_group,
                                           user=owner, perm='group.admin')

            if parent_group and copy_permissions:
                # copy permissions from parent
                user_perms = UserRepoGroupToPerm.query() \
                    .filter(UserRepoGroupToPerm.group == parent_group).all()

                group_perms = UserGroupRepoGroupToPerm.query() \
                    .filter(UserGroupRepoGroupToPerm.group == parent_group).all()

                for perm in user_perms:
                    # don't copy over the permission for user who is creating
                    # this group, if he is not super admin he get's admin
                    # permission set above
                    if perm.user != user or user.is_admin:
                        UserRepoGroupToPerm.create(
                            perm.user, new_repo_group, perm.permission)

                for perm in group_perms:
                    UserGroupRepoGroupToPerm.create(
                        perm.users_group, new_repo_group, perm.permission)
            else:
                perm_obj = self._create_default_perms(new_repo_group)
                self.sa.add(perm_obj)

            # now commit the changes, earlier so we are sure everything is in
            # the database.
            if commit_early:
                self.sa.commit()
            if not just_db:
                self._create_group(new_repo_group.group_name)

            # trigger the post hook
            from rhodecode.lib.hooks_base import log_create_repository_group
            repo_group = RepoGroup.get_by_group_name(group_name)
            log_create_repository_group(
                created_by=user.username, **repo_group.get_dict())

            return new_repo_group
        except Exception:
            self.sa.rollback()
            log.exception('Exception occurred when creating repository group, '
                          'doing cleanup...')
            # rollback things manually !
            repo_group = RepoGroup.get_by_group_name(group_name)
            if repo_group:
                RepoGroup.delete(repo_group.group_id)
                self.sa.commit()
                if cleanup_group:
                    RepoGroupModel()._delete_filesystem_group(repo_group)
            raise

    def update_permissions(
            self, repo_group, perm_additions=None, perm_updates=None,
            perm_deletions=None, recursive=None, check_perms=True,
            cur_user=None):
        from rhodecode.model.repo import RepoModel
        from rhodecode.lib.auth import HasUserGroupPermissionAny

        if not perm_additions:
            perm_additions = []
        if not perm_updates:
            perm_updates = []
        if not perm_deletions:
            perm_deletions = []

        req_perms = ('usergroup.read', 'usergroup.write', 'usergroup.admin')

        def _set_perm_user(obj, user, perm):
            if isinstance(obj, RepoGroup):
                self.grant_user_permission(
                    repo_group=obj, user=user, perm=perm)
            elif isinstance(obj, Repository):
                # private repos will not allow to change the default
                # permissions using recursive mode
                if obj.private and user == User.DEFAULT_USER:
                    return

                # we set group permission but we have to switch to repo
                # permission
                perm = perm.replace('group.', 'repository.')
                RepoModel().grant_user_permission(
                    repo=obj, user=user, perm=perm)

        def _set_perm_group(obj, users_group, perm):
            if isinstance(obj, RepoGroup):
                self.grant_user_group_permission(
                    repo_group=obj, group_name=users_group, perm=perm)
            elif isinstance(obj, Repository):
                # we set group permission but we have to switch to repo
                # permission
                perm = perm.replace('group.', 'repository.')
                RepoModel().grant_user_group_permission(
                    repo=obj, group_name=users_group, perm=perm)

        def _revoke_perm_user(obj, user):
            if isinstance(obj, RepoGroup):
                self.revoke_user_permission(repo_group=obj, user=user)
            elif isinstance(obj, Repository):
                RepoModel().revoke_user_permission(repo=obj, user=user)

        def _revoke_perm_group(obj, user_group):
            if isinstance(obj, RepoGroup):
                self.revoke_user_group_permission(
                    repo_group=obj, group_name=user_group)
            elif isinstance(obj, Repository):
                RepoModel().revoke_user_group_permission(
                    repo=obj, group_name=user_group)

        # start updates
        updates = []
        log.debug('Now updating permissions for %s in recursive mode:%s',
                  repo_group, recursive)

        # initialize check function, we'll call that multiple times
        has_group_perm = HasUserGroupPermissionAny(*req_perms)

        for obj in repo_group.recursive_groups_and_repos():
            # iterated obj is an instance of a repos group or repository in
            # that group, recursive option can be: none, repos, groups, all
            if recursive == 'all':
                obj = obj
            elif recursive == 'repos':
                # skip groups, other than this one
                if isinstance(obj, RepoGroup) and not obj == repo_group:
                    continue
            elif recursive == 'groups':
                # skip repos
                if isinstance(obj, Repository):
                    continue
            else:  # recursive == 'none':
                #  DEFAULT option - don't apply to iterated objects
                # also we do a break at the end of this loop. if we are not
                # in recursive mode
                obj = repo_group

            # update permissions
            for member_id, perm, member_type in perm_updates:
                member_id = int(member_id)
                if member_type == 'user':
                    # this updates also current one if found
                    _set_perm_user(obj, user=member_id, perm=perm)
                else:  # set for user group
                    member_name = UserGroup.get(member_id).users_group_name
                    if not check_perms or has_group_perm(member_name,
                                                         user=cur_user):
                        _set_perm_group(obj, users_group=member_id, perm=perm)

            # set new permissions
            for member_id, perm, member_type in perm_additions:
                member_id = int(member_id)
                if member_type == 'user':
                    _set_perm_user(obj, user=member_id, perm=perm)
                else:  # set for user group
                    # check if we have permissions to alter this usergroup
                    member_name = UserGroup.get(member_id).users_group_name
                    if not check_perms or has_group_perm(member_name,
                                                         user=cur_user):
                        _set_perm_group(obj, users_group=member_id, perm=perm)

            # delete permissions
            for member_id, perm, member_type in perm_deletions:
                member_id = int(member_id)
                if member_type == 'user':
                    _revoke_perm_user(obj, user=member_id)
                else:  # set for user group
                    # check if we have permissions to alter this usergroup
                    member_name = UserGroup.get(member_id).users_group_name
                    if not check_perms or has_group_perm(member_name,
                                                         user=cur_user):
                        _revoke_perm_group(obj, user_group=member_id)

            updates.append(obj)
            # if it's not recursive call for all,repos,groups
            # break the loop and don't proceed with other changes
            if recursive not in ['all', 'repos', 'groups']:
                break

        return updates

    def update(self, repo_group, form_data):
        try:
            repo_group = self._get_repo_group(repo_group)
            old_path = repo_group.full_path

            # change properties
            if 'group_description' in form_data:
                repo_group.group_description = form_data['group_description']

            if 'enable_locking' in form_data:
                repo_group.enable_locking = form_data['enable_locking']

            if 'group_parent_id' in form_data:
                parent_group = (
                    self._get_repo_group(form_data['group_parent_id']))
                repo_group.group_parent_id = (
                    parent_group.group_id if parent_group else None)
                repo_group.parent_group = parent_group

            # mikhail: to update the full_path, we have to explicitly
            # update group_name
            group_name = form_data.get('group_name', repo_group.name)
            repo_group.group_name = repo_group.get_new_name(group_name)

            new_path = repo_group.full_path

            if 'user' in form_data:
                repo_group.user = User.get_by_username(form_data['user'])

            self.sa.add(repo_group)

            # iterate over all members of this groups and do fixes
            # set locking if given
            # if obj is a repoGroup also fix the name of the group according
            # to the parent
            # if obj is a Repo fix it's name
            # this can be potentially heavy operation
            for obj in repo_group.recursive_groups_and_repos():
                # set the value from it's parent
                obj.enable_locking = repo_group.enable_locking
                if isinstance(obj, RepoGroup):
                    new_name = obj.get_new_name(obj.name)
                    log.debug('Fixing group %s to new name %s',
                              obj.group_name, new_name)
                    obj.group_name = new_name
                elif isinstance(obj, Repository):
                    # we need to get all repositories from this new group and
                    # rename them accordingly to new group path
                    new_name = obj.get_new_name(obj.just_name)
                    log.debug('Fixing repo %s to new name %s',
                              obj.repo_name, new_name)
                    obj.repo_name = new_name
                self.sa.add(obj)

            self._rename_group(old_path, new_path)

            return repo_group
        except Exception:
            log.error(traceback.format_exc())
            raise

    def delete(self, repo_group, force_delete=False, fs_remove=True):
        repo_group = self._get_repo_group(repo_group)
        try:
            self.sa.delete(repo_group)
            if fs_remove:
                self._delete_filesystem_group(repo_group, force_delete)
            else:
                log.debug('skipping removal from filesystem')

        except Exception:
            log.error('Error removing repo_group %s', repo_group)
            raise

    def grant_user_permission(self, repo_group, user, perm):
        """
        Grant permission for user on given repository group, or update
        existing one if found

        :param repo_group: Instance of RepoGroup, repositories_group_id,
            or repositories_group name
        :param user: Instance of User, user_id or username
        :param perm: Instance of Permission, or permission_name
        """

        repo_group = self._get_repo_group(repo_group)
        user = self._get_user(user)
        permission = self._get_perm(perm)

        # check if we have that permission already
        obj = self.sa.query(UserRepoGroupToPerm)\
            .filter(UserRepoGroupToPerm.user == user)\
            .filter(UserRepoGroupToPerm.group == repo_group)\
            .scalar()
        if obj is None:
            # create new !
            obj = UserRepoGroupToPerm()
        obj.group = repo_group
        obj.user = user
        obj.permission = permission
        self.sa.add(obj)
        log.debug('Granted perm %s to %s on %s', perm, user, repo_group)
        action_logger_generic(
            'granted permission: {} to user: {} on repogroup: {}'.format(
                perm, user, repo_group), namespace='security.repogroup')
        return obj

    def revoke_user_permission(self, repo_group, user):
        """
        Revoke permission for user on given repository group

        :param repo_group: Instance of RepoGroup, repositories_group_id,
            or repositories_group name
        :param user: Instance of User, user_id or username
        """

        repo_group = self._get_repo_group(repo_group)
        user = self._get_user(user)

        obj = self.sa.query(UserRepoGroupToPerm)\
            .filter(UserRepoGroupToPerm.user == user)\
            .filter(UserRepoGroupToPerm.group == repo_group)\
            .scalar()
        if obj:
            self.sa.delete(obj)
            log.debug('Revoked perm on %s on %s', repo_group, user)
            action_logger_generic(
                'revoked permission from user: {} on repogroup: {}'.format(
                    user, repo_group), namespace='security.repogroup')

    def grant_user_group_permission(self, repo_group, group_name, perm):
        """
        Grant permission for user group on given repository group, or update
        existing one if found

        :param repo_group: Instance of RepoGroup, repositories_group_id,
            or repositories_group name
        :param group_name: Instance of UserGroup, users_group_id,
            or user group name
        :param perm: Instance of Permission, or permission_name
        """
        repo_group = self._get_repo_group(repo_group)
        group_name = self._get_user_group(group_name)
        permission = self._get_perm(perm)

        # check if we have that permission already
        obj = self.sa.query(UserGroupRepoGroupToPerm)\
            .filter(UserGroupRepoGroupToPerm.group == repo_group)\
            .filter(UserGroupRepoGroupToPerm.users_group == group_name)\
            .scalar()

        if obj is None:
            # create new
            obj = UserGroupRepoGroupToPerm()

        obj.group = repo_group
        obj.users_group = group_name
        obj.permission = permission
        self.sa.add(obj)
        log.debug('Granted perm %s to %s on %s', perm, group_name, repo_group)
        action_logger_generic(
            'granted permission: {} to usergroup: {} on repogroup: {}'.format(
                perm, group_name, repo_group), namespace='security.repogroup')
        return obj

    def revoke_user_group_permission(self, repo_group, group_name):
        """
        Revoke permission for user group on given repository group

        :param repo_group: Instance of RepoGroup, repositories_group_id,
            or repositories_group name
        :param group_name: Instance of UserGroup, users_group_id,
            or user group name
        """
        repo_group = self._get_repo_group(repo_group)
        group_name = self._get_user_group(group_name)

        obj = self.sa.query(UserGroupRepoGroupToPerm)\
            .filter(UserGroupRepoGroupToPerm.group == repo_group)\
            .filter(UserGroupRepoGroupToPerm.users_group == group_name)\
            .scalar()
        if obj:
            self.sa.delete(obj)
            log.debug('Revoked perm to %s on %s', repo_group, group_name)
            action_logger_generic(
                'revoked permission from usergroup: {} on repogroup: {}'.format(
                    group_name, repo_group), namespace='security.repogroup')

    def get_repo_groups_as_dict(self, repo_group_list=None, admin=False,
                                super_user_actions=False):

        from rhodecode.lib.utils import PartialRenderer
        _render = PartialRenderer('data_table/_dt_elements.html')
        c = _render.c
        h = _render.h

        def quick_menu(repo_group_name):
            return _render('quick_repo_group_menu', repo_group_name)

        def repo_group_lnk(repo_group_name):
            return _render('repo_group_name', repo_group_name)

        def desc(desc):
            if c.visual.stylify_metatags:
                return h.urlify_text(h.escaped_stylize(h.truncate(desc, 60)))
            else:
                return h.urlify_text(h.html_escape(h.truncate(desc, 60)))

        def repo_group_actions(repo_group_id, repo_group_name, gr_count):
            return _render(
                'repo_group_actions', repo_group_id, repo_group_name, gr_count)

        def repo_group_name(repo_group_name, children_groups):
            return _render("repo_group_name", repo_group_name, children_groups)

        def user_profile(username):
            return _render('user_profile', username)

        repo_group_data = []
        for group in repo_group_list:

            row = {
                "menu": quick_menu(group.group_name),
                "name": repo_group_lnk(group.group_name),
                "name_raw": group.group_name,
                "desc": desc(group.group_description),
                "top_level_repos": 0,
                "owner": user_profile(group.user.username)
            }
            if admin:
                repo_count = group.repositories.count()
                children_groups = map(
                    h.safe_unicode,
                    itertools.chain((g.name for g in group.parents),
                                    (x.name for x in [group])))
                row.update({
                    "action": repo_group_actions(
                        group.group_id, group.group_name, repo_count),
                    "top_level_repos": repo_count,
                    "name": repo_group_name(group.group_name, children_groups),

                })
            repo_group_data.append(row)

        return repo_group_data
