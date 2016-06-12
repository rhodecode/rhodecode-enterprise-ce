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
user group model for RhodeCode
"""


import logging
import traceback

from rhodecode.lib.utils2 import safe_str
from rhodecode.model import BaseModel
from rhodecode.model.db import UserGroupMember, UserGroup,\
    UserGroupRepoToPerm, Permission, UserGroupToPerm, User, UserUserGroupToPerm,\
    UserGroupUserGroupToPerm, UserGroupRepoGroupToPerm
from rhodecode.lib.exceptions import UserGroupAssignedException,\
    RepoGroupAssignmentError
from rhodecode.lib.utils2 import get_current_rhodecode_user, action_logger_generic

log = logging.getLogger(__name__)


class UserGroupModel(BaseModel):

    cls = UserGroup

    def _get_user_group(self, user_group):
        return self._get_instance(UserGroup, user_group,
                                  callback=UserGroup.get_by_group_name)

    def _create_default_perms(self, user_group):
        # create default permission
        default_perm = 'usergroup.read'
        def_user = User.get_default_user()
        for p in def_user.user_perms:
            if p.permission.permission_name.startswith('usergroup.'):
                default_perm = p.permission.permission_name
                break

        user_group_to_perm = UserUserGroupToPerm()
        user_group_to_perm.permission = Permission.get_by_key(default_perm)

        user_group_to_perm.user_group = user_group
        user_group_to_perm.user_id = def_user.user_id
        return user_group_to_perm

    def update_permissions(self, user_group, perm_additions=None, perm_updates=None,
                           perm_deletions=None, check_perms=True, cur_user=None):
        from rhodecode.lib.auth import HasUserGroupPermissionAny
        if not perm_additions:
            perm_additions = []
        if not perm_updates:
            perm_updates = []
        if not perm_deletions:
            perm_deletions = []

        req_perms = ('usergroup.read', 'usergroup.write', 'usergroup.admin')

        # update permissions
        for member_id, perm, member_type in perm_updates:
            member_id = int(member_id)
            if member_type == 'user':
                # this updates existing one
                self.grant_user_permission(
                    user_group=user_group, user=member_id, perm=perm
                )
            else:
                # check if we have permissions to alter this usergroup
                member_name = UserGroup.get(member_id).users_group_name
                if not check_perms or HasUserGroupPermissionAny(*req_perms)(member_name, user=cur_user):
                    self.grant_user_group_permission(
                        target_user_group=user_group, user_group=member_id, perm=perm
                    )

        # set new permissions
        for member_id, perm, member_type in perm_additions:
            member_id = int(member_id)
            if member_type == 'user':
                self.grant_user_permission(
                    user_group=user_group, user=member_id, perm=perm
                )
            else:
                # check if we have permissions to alter this usergroup
                member_name = UserGroup.get(member_id).users_group_name
                if not check_perms or HasUserGroupPermissionAny(*req_perms)(member_name, user=cur_user):
                    self.grant_user_group_permission(
                        target_user_group=user_group, user_group=member_id, perm=perm
                    )

        # delete permissions
        for member_id, perm, member_type in perm_deletions:
            member_id = int(member_id)
            if member_type == 'user':
                self.revoke_user_permission(user_group=user_group, user=member_id)
            else:
                #check if we have permissions to alter this usergroup
                member_name = UserGroup.get(member_id).users_group_name
                if not check_perms or HasUserGroupPermissionAny(*req_perms)(member_name, user=cur_user):
                    self.revoke_user_group_permission(
                        target_user_group=user_group, user_group=member_id
                    )

    def get(self, user_group_id, cache=False):
        return UserGroup.get(user_group_id)

    def get_group(self, user_group):
        return self._get_user_group(user_group)

    def get_by_name(self, name, cache=False, case_insensitive=False):
        return UserGroup.get_by_group_name(name, cache, case_insensitive)

    def create(self, name, description, owner, active=True, group_data=None):
        try:
            new_user_group = UserGroup()
            new_user_group.user = self._get_user(owner)
            new_user_group.users_group_name = name
            new_user_group.user_group_description = description
            new_user_group.users_group_active = active
            if group_data:
                new_user_group.group_data = group_data
            self.sa.add(new_user_group)
            perm_obj = self._create_default_perms(new_user_group)
            self.sa.add(perm_obj)

            self.grant_user_permission(user_group=new_user_group,
                                       user=owner, perm='usergroup.admin')

            return new_user_group
        except Exception:
            log.error(traceback.format_exc())
            raise

    def _get_memberships_for_user_ids(self, user_group, user_id_list):
        members = []
        for user_id in user_id_list:
            member = self._get_membership(user_group.users_group_id, user_id)
            members.append(member)
        return members

    def _get_added_and_removed_user_ids(self, user_group, user_id_list):
        current_members = user_group.members or []
        current_members_ids = [m.user.user_id for m in current_members]

        added_members = [
            user_id for user_id in user_id_list
            if user_id not in current_members_ids]
        if user_id_list == []:
            # all members were deleted
            deleted_members = current_members_ids
        else:
            deleted_members = [
                user_id for user_id in current_members_ids
                if user_id not in user_id_list]

        return (added_members, deleted_members)

    def _set_users_as_members(self, user_group, user_ids):
        user_group.members = []
        self.sa.flush()
        members = self._get_memberships_for_user_ids(
            user_group, user_ids)
        user_group.members = members
        self.sa.add(user_group)

    def _update_members_from_user_ids(self, user_group, user_ids):
        added, removed = self._get_added_and_removed_user_ids(
            user_group, user_ids)
        self._set_users_as_members(user_group, user_ids)
        self._log_user_changes('added to', user_group, added)
        self._log_user_changes('removed from', user_group, removed)

    def _clean_members_data(self, members_data):
        # TODO: anderson: this should be in the form validation but I couldn't
        # make it work there as it conflicts with the other validator
        if not members_data:
            members_data = []

        if isinstance(members_data, basestring):
            new_members = [members_data]
        else:
            new_members = members_data

        new_members = [int(uid) for uid in new_members]
        return new_members

    def update(self, user_group, form_data):
        user_group = self._get_user_group(user_group)
        if 'users_group_name' in form_data:
            user_group.users_group_name = form_data['users_group_name']
        if 'users_group_active' in form_data:
            user_group.users_group_active = form_data['users_group_active']
        if 'user_group_description' in form_data:
            user_group.user_group_description = form_data[
                'user_group_description']

        # handle owner change
        if 'user' in form_data:
            owner = form_data['user']
            if isinstance(owner, basestring):
                owner = User.get_by_username(form_data['user'])

            if not isinstance(owner, User):
                raise ValueError(
                    'invalid owner for user group: %s' % form_data['user'])

            user_group.user = owner

        if 'users_group_members' in form_data:
            members_id_list = self._clean_members_data(
                form_data['users_group_members'])
            self._update_members_from_user_ids(user_group, members_id_list)

        self.sa.add(user_group)

    def delete(self, user_group, force=False):
        """
        Deletes repository group, unless force flag is used
        raises exception if there are members in that group, else deletes
        group and users

        :param user_group:
        :param force:
        """
        user_group = self._get_user_group(user_group)
        try:
            # check if this group is not assigned to repo
            assigned_to_repo = [x.repository for x in UserGroupRepoToPerm.query()\
                .filter(UserGroupRepoToPerm.users_group == user_group).all()]
            # check if this group is not assigned to repo
            assigned_to_repo_group = [x.group for x in UserGroupRepoGroupToPerm.query()\
                .filter(UserGroupRepoGroupToPerm.users_group == user_group).all()]

            if (assigned_to_repo or assigned_to_repo_group) and not force:
                assigned = ','.join(map(safe_str,
                                    assigned_to_repo+assigned_to_repo_group))

                raise UserGroupAssignedException(
                    'UserGroup assigned to %s' % (assigned,))
            self.sa.delete(user_group)
        except Exception:
            log.error(traceback.format_exc())
            raise

    def _log_user_changes(self, action, user_group, user_or_users):
        users = user_or_users
        if not isinstance(users, (list, tuple)):
            users = [users]
        rhodecode_user = get_current_rhodecode_user()
        ipaddr = getattr(rhodecode_user, 'ip_addr', '')
        group_name = user_group.users_group_name

        for user_or_user_id in users:
            user = self._get_user(user_or_user_id)
            log_text = 'User {user} {action} {group}'.format(
                action=action, user=user.username, group=group_name)
            log.info('Logging action: {0} by {1} ip:{2}'.format(
                     log_text, rhodecode_user, ipaddr))

    def _find_user_in_group(self, user, user_group):
        user_group_member = None
        for m in user_group.members:
            if m.user_id == user.user_id:
                # Found this user's membership row
                user_group_member = m
                break

        return user_group_member

    def _get_membership(self, user_group_id, user_id):
        user_group_member = UserGroupMember(user_group_id, user_id)
        return user_group_member

    def add_user_to_group(self, user_group, user):
        user_group = self._get_user_group(user_group)
        user = self._get_user(user)
        user_member = self._find_user_in_group(user, user_group)
        if user_member:
            # user already in the group, skip
            return True

        member = self._get_membership(
            user_group.users_group_id, user.user_id)
        user_group.members.append(member)

        try:
            self.sa.add(member)
        except Exception:
            # what could go wrong here?
            log.error(traceback.format_exc())
            raise

        self._log_user_changes('added to', user_group, user)
        return member

    def remove_user_from_group(self, user_group, user):
        user_group = self._get_user_group(user_group)
        user = self._get_user(user)
        user_group_member = self._find_user_in_group(user, user_group)

        if not user_group_member:
            # User isn't in that group
            return False

        try:
            self.sa.delete(user_group_member)
        except Exception:
            log.error(traceback.format_exc())
            raise

        self._log_user_changes('removed from', user_group, user)
        return True

    def has_perm(self, user_group, perm):
        user_group = self._get_user_group(user_group)
        perm = self._get_perm(perm)

        return UserGroupToPerm.query()\
            .filter(UserGroupToPerm.users_group == user_group)\
            .filter(UserGroupToPerm.permission == perm).scalar() is not None

    def grant_perm(self, user_group, perm):
        user_group = self._get_user_group(user_group)
        perm = self._get_perm(perm)

        # if this permission is already granted skip it
        _perm = UserGroupToPerm.query()\
            .filter(UserGroupToPerm.users_group == user_group)\
            .filter(UserGroupToPerm.permission == perm)\
            .scalar()
        if _perm:
            return

        new = UserGroupToPerm()
        new.users_group = user_group
        new.permission = perm
        self.sa.add(new)
        return new

    def revoke_perm(self, user_group, perm):
        user_group = self._get_user_group(user_group)
        perm = self._get_perm(perm)

        obj = UserGroupToPerm.query()\
            .filter(UserGroupToPerm.users_group == user_group)\
            .filter(UserGroupToPerm.permission == perm).scalar()
        if obj:
            self.sa.delete(obj)

    def grant_user_permission(self, user_group, user, perm):
        """
        Grant permission for user on given user group, or update
        existing one if found

        :param user_group: Instance of UserGroup, users_group_id,
            or users_group_name
        :param user: Instance of User, user_id or username
        :param perm: Instance of Permission, or permission_name
        """

        user_group = self._get_user_group(user_group)
        user = self._get_user(user)
        permission = self._get_perm(perm)

        # check if we have that permission already
        obj = self.sa.query(UserUserGroupToPerm)\
            .filter(UserUserGroupToPerm.user == user)\
            .filter(UserUserGroupToPerm.user_group == user_group)\
            .scalar()
        if obj is None:
            # create new !
            obj = UserUserGroupToPerm()
        obj.user_group = user_group
        obj.user = user
        obj.permission = permission
        self.sa.add(obj)
        log.debug('Granted perm %s to %s on %s', perm, user, user_group)
        action_logger_generic(
            'granted permission: {} to user: {} on usergroup: {}'.format(
                perm, user, user_group), namespace='security.usergroup')

        return obj

    def revoke_user_permission(self, user_group, user):
        """
        Revoke permission for user on given user group

        :param user_group: Instance of UserGroup, users_group_id,
            or users_group name
        :param user: Instance of User, user_id or username
        """

        user_group = self._get_user_group(user_group)
        user = self._get_user(user)

        obj = self.sa.query(UserUserGroupToPerm)\
            .filter(UserUserGroupToPerm.user == user)\
            .filter(UserUserGroupToPerm.user_group == user_group)\
            .scalar()
        if obj:
            self.sa.delete(obj)
            log.debug('Revoked perm on %s on %s', user_group, user)
            action_logger_generic(
                'revoked permission from user: {} on usergroup: {}'.format(
                    user, user_group), namespace='security.usergroup')

    def grant_user_group_permission(self, target_user_group, user_group, perm):
        """
        Grant user group permission for given target_user_group

        :param target_user_group:
        :param user_group:
        :param perm:
        """
        target_user_group = self._get_user_group(target_user_group)
        user_group = self._get_user_group(user_group)
        permission = self._get_perm(perm)
        # forbid assigning same user group to itself
        if target_user_group == user_group:
            raise RepoGroupAssignmentError('target repo:%s cannot be '
                                           'assigned to itself' % target_user_group)

        # check if we have that permission already
        obj = self.sa.query(UserGroupUserGroupToPerm)\
            .filter(UserGroupUserGroupToPerm.target_user_group == target_user_group)\
            .filter(UserGroupUserGroupToPerm.user_group == user_group)\
            .scalar()
        if obj is None:
            # create new !
            obj = UserGroupUserGroupToPerm()
        obj.user_group = user_group
        obj.target_user_group = target_user_group
        obj.permission = permission
        self.sa.add(obj)
        log.debug(
            'Granted perm %s to %s on %s', perm, target_user_group, user_group)
        action_logger_generic(
            'granted permission: {} to usergroup: {} on usergroup: {}'.format(
                perm, user_group, target_user_group),
            namespace='security.usergroup')

        return obj

    def revoke_user_group_permission(self, target_user_group, user_group):
        """
        Revoke user group permission for given target_user_group

        :param target_user_group:
        :param user_group:
        """
        target_user_group = self._get_user_group(target_user_group)
        user_group = self._get_user_group(user_group)

        obj = self.sa.query(UserGroupUserGroupToPerm)\
            .filter(UserGroupUserGroupToPerm.target_user_group == target_user_group)\
            .filter(UserGroupUserGroupToPerm.user_group == user_group)\
            .scalar()
        if obj:
            self.sa.delete(obj)
            log.debug(
                'Revoked perm on %s on %s', target_user_group, user_group)
            action_logger_generic(
                'revoked permission from usergroup: {} on usergroup: {}'.format(
                    user_group, target_user_group),
                namespace='security.repogroup')

    def enforce_groups(self, user, groups, extern_type=None):
        user = self._get_user(user)
        log.debug('Enforcing groups %s on user %s', groups, user)
        current_groups = user.group_member
        # find the external created groups
        externals = [x.users_group for x in current_groups
                     if 'extern_type' in x.users_group.group_data]

        # calculate from what groups user should be removed
        # externals that are not in groups
        for gr in externals:
            if gr.users_group_name not in groups:
                log.debug('Removing user %s from user group %s', user, gr)
                self.remove_user_from_group(gr, user)

        # now we calculate in which groups user should be == groups params
        owner = User.get_first_admin().username
        for gr in set(groups):
            existing_group = UserGroup.get_by_group_name(gr)
            if not existing_group:
                desc = 'Automatically created from plugin:%s' % extern_type
                # we use first admin account to set the owner of the group
                existing_group = UserGroupModel().create(gr, desc, owner,
                                        group_data={'extern_type': extern_type})

            # we can only add users to special groups created via plugins
            managed = 'extern_type' in existing_group.group_data
            if managed:
                log.debug('Adding user %s to user group %s', user, gr)
                UserGroupModel().add_user_to_group(existing_group, user)
            else:
                log.debug('Skipping addition to group %s since it is '
                          'not managed by auth plugins' % gr)
