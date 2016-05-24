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
permissions model for RhodeCode
"""


import logging
import traceback

from sqlalchemy.exc import DatabaseError

from rhodecode.model import BaseModel
from rhodecode.model.db import (
    User, Permission, UserToPerm, UserRepoToPerm, UserRepoGroupToPerm,
    UserUserGroupToPerm, UserGroup, UserGroupToPerm)
from rhodecode.lib.utils2 import str2bool, safe_int

log = logging.getLogger(__name__)


class PermissionModel(BaseModel):
    """
    Permissions model for RhodeCode
    """

    cls = Permission
    global_perms = {
        'default_repo_create': None,
        # special case for create repos on write access to group
        'default_repo_create_on_write': None,
        'default_repo_group_create': None,
        'default_user_group_create': None,
        'default_fork_create': None,
        'default_inherit_default_permissions': None,

        'default_register': None,
        'default_extern_activate': None,

        # object permissions below
        'default_repo_perm': None,
        'default_group_perm': None,
        'default_user_group_perm': None,
    }

    def set_global_permission_choices(self, c_obj, translator):
        c_obj.repo_perms_choices = [
            ('repository.none', translator('None'),),
            ('repository.read', translator('Read'),),
            ('repository.write', translator('Write'),),
            ('repository.admin', translator('Admin'),)]

        c_obj.group_perms_choices = [
            ('group.none', translator('None'),),
            ('group.read', translator('Read'),),
            ('group.write', translator('Write'),),
            ('group.admin', translator('Admin'),)]

        c_obj.user_group_perms_choices = [
            ('usergroup.none', translator('None'),),
            ('usergroup.read', translator('Read'),),
            ('usergroup.write', translator('Write'),),
            ('usergroup.admin', translator('Admin'),)]

        c_obj.register_choices = [
            ('hg.register.none', translator('Disabled')),
            ('hg.register.manual_activate', translator('Allowed with manual account activation')),
            ('hg.register.auto_activate', translator('Allowed with automatic account activation')),]

        c_obj.extern_activate_choices = [
            ('hg.extern_activate.manual', translator('Manual activation of external account')),
            ('hg.extern_activate.auto', translator('Automatic activation of external account')),]

        c_obj.repo_create_choices = [
            ('hg.create.none', translator('Disabled')),
            ('hg.create.repository', translator('Enabled'))]

        c_obj.repo_create_on_write_choices = [
            ('hg.create.write_on_repogroup.false', translator('Disabled')),
            ('hg.create.write_on_repogroup.true', translator('Enabled'))]

        c_obj.user_group_create_choices = [
            ('hg.usergroup.create.false', translator('Disabled')),
            ('hg.usergroup.create.true', translator('Enabled'))]

        c_obj.repo_group_create_choices = [
            ('hg.repogroup.create.false', translator('Disabled')),
            ('hg.repogroup.create.true', translator('Enabled'))]

        c_obj.fork_choices = [
            ('hg.fork.none', translator('Disabled')),
            ('hg.fork.repository', translator('Enabled'))]

        c_obj.inherit_default_permission_choices = [
            ('hg.inherit_default_perms.false', translator('Disabled')),
            ('hg.inherit_default_perms.true', translator('Enabled'))]

    def get_default_perms(self, object_perms, suffix):
        defaults = {}
        for perm in object_perms:
            # perms
            if perm.permission.permission_name.startswith('repository.'):
                defaults['default_repo_perm' + suffix] = perm.permission.permission_name

            if perm.permission.permission_name.startswith('group.'):
                defaults['default_group_perm' + suffix] = perm.permission.permission_name

            if perm.permission.permission_name.startswith('usergroup.'):
                defaults['default_user_group_perm' + suffix] = perm.permission.permission_name

            # creation of objects
            if perm.permission.permission_name.startswith('hg.create.write_on_repogroup'):
                defaults['default_repo_create_on_write' + suffix] = perm.permission.permission_name

            elif perm.permission.permission_name.startswith('hg.create.'):
                defaults['default_repo_create' + suffix] = perm.permission.permission_name

            if perm.permission.permission_name.startswith('hg.fork.'):
                defaults['default_fork_create' + suffix] = perm.permission.permission_name

            if perm.permission.permission_name.startswith('hg.inherit_default_perms.'):
                defaults['default_inherit_default_permissions' + suffix] = perm.permission.permission_name

            if perm.permission.permission_name.startswith('hg.repogroup.'):
                defaults['default_repo_group_create' + suffix] = perm.permission.permission_name

            if perm.permission.permission_name.startswith('hg.usergroup.'):
                defaults['default_user_group_create' + suffix] = perm.permission.permission_name

            # registration and external account activation
            if perm.permission.permission_name.startswith('hg.register.'):
                defaults['default_register' + suffix] = perm.permission.permission_name

            if perm.permission.permission_name.startswith('hg.extern_activate.'):
                defaults['default_extern_activate' + suffix] = perm.permission.permission_name

        return defaults

    def _make_new_user_perm(self, user, perm_name):
        log.debug('Creating new user permission:%s', perm_name)
        new = UserToPerm()
        new.user = user
        new.permission = Permission.get_by_key(perm_name)
        return new

    def _make_new_user_group_perm(self, user_group, perm_name):
        log.debug('Creating new user group permission:%s', perm_name)
        new = UserGroupToPerm()
        new.users_group = user_group
        new.permission = Permission.get_by_key(perm_name)
        return new

    def _keep_perm(self, perm_name, keep_fields):
        def get_pat(field_name):
            return {
                # global perms
                'default_repo_create': 'hg.create.',
                # special case for create repos on write access to group
                'default_repo_create_on_write': 'hg.create.write_on_repogroup.',
                'default_repo_group_create': 'hg.repogroup.create.',
                'default_user_group_create': 'hg.usergroup.create.',
                'default_fork_create': 'hg.fork.',
                'default_inherit_default_permissions': 'hg.inherit_default_perms.',

                # application perms
                'default_register': 'hg.register.',
                'default_extern_activate': 'hg.extern_activate.',

                # object permissions below
                'default_repo_perm': 'repository.',
                'default_group_perm': 'group.',
                'default_user_group_perm': 'usergroup.',
            }[field_name]
        for field in keep_fields:
            pat = get_pat(field)
            if perm_name.startswith(pat):
                return True
        return False

    def _clear_object_perm(self, object_perms, preserve=None):
        preserve = preserve or []
        _deleted = []
        for perm in object_perms:
            perm_name = perm.permission.permission_name
            if not self._keep_perm(perm_name, keep_fields=preserve):
                _deleted.append(perm_name)
                self.sa.delete(perm)
        return _deleted

    def _clear_user_perms(self, user_id, preserve=None):
        perms = self.sa.query(UserToPerm)\
            .filter(UserToPerm.user_id == user_id)\
            .all()
        return self._clear_object_perm(perms, preserve=preserve)

    def _clear_user_group_perms(self, user_group_id, preserve=None):
        perms = self.sa.query(UserGroupToPerm)\
            .filter(UserGroupToPerm.users_group_id == user_group_id)\
            .all()
        return self._clear_object_perm(perms, preserve=preserve)

    def _set_new_object_perms(self, obj_type, object, form_result, preserve=None):
        # clear current entries, to make this function idempotent
        # it will fix even if we define more permissions or permissions
        # are somehow missing
        preserve = preserve or []
        _global_perms = self.global_perms.copy()
        if obj_type not in ['user', 'user_group']:
            raise ValueError("obj_type must be on of 'user' or 'user_group'")
        if len(_global_perms) != len(Permission.DEFAULT_USER_PERMISSIONS):
            raise Exception('Inconsistent permissions definition')

        if obj_type == 'user':
            self._clear_user_perms(object.user_id, preserve)
        if obj_type == 'user_group':
            self._clear_user_group_perms(object.users_group_id, preserve)

        # now kill the keys that we want to preserve from the form.
        for key in preserve:
            del _global_perms[key]

        for k in _global_perms.copy():
            _global_perms[k] = form_result[k]

        # at that stage we validate all are passed inside form_result
        for _perm_key, perm_value in _global_perms.items():
            if perm_value is None:
                raise ValueError('Missing permission for %s' % (_perm_key,))

            if obj_type == 'user':
                p = self._make_new_user_perm(object, perm_value)
                self.sa.add(p)
            if obj_type == 'user_group':
                p = self._make_new_user_group_perm(object, perm_value)
                self.sa.add(p)

    def _set_new_user_perms(self, user, form_result, preserve=None):
        return self._set_new_object_perms(
            'user', user, form_result, preserve)

    def _set_new_user_group_perms(self, user_group, form_result, preserve=None):
        return self._set_new_object_perms(
            'user_group', user_group, form_result, preserve)

    def set_new_user_perms(self, user, form_result):
        # calculate what to preserve from what is given in form_result
        preserve = set(self.global_perms.keys()).difference(set(form_result.keys()))
        return self._set_new_user_perms(user, form_result, preserve)

    def set_new_user_group_perms(self, user_group, form_result):
        # calculate what to preserve from what is given in form_result
        preserve = set(self.global_perms.keys()).difference(set(form_result.keys()))
        return self._set_new_user_group_perms(user_group, form_result, preserve)

    def create_permissions(self):
        """
        Create permissions for whole system
        """
        for p in Permission.PERMS:
            if not Permission.get_by_key(p[0]):
                new_perm = Permission()
                new_perm.permission_name = p[0]
                new_perm.permission_longname = p[0]  # translation err with p[1]
                self.sa.add(new_perm)

    def _create_default_object_permission(self, obj_type, obj, obj_perms,
                                          force=False):
        if obj_type not in ['user', 'user_group']:
            raise ValueError("obj_type must be on of 'user' or 'user_group'")

        def _get_group(perm_name):
            return '.'.join(perm_name.split('.')[:1])

        defined_perms_groups = map(
            _get_group, (x.permission.permission_name for x in obj_perms))
        log.debug('GOT ALREADY DEFINED:%s', obj_perms)

        if force:
            self._clear_object_perm(obj_perms)
            self.sa.commit()
            defined_perms_groups = []
        # for every default permission that needs to be created, we check if
        # it's group is already defined, if it's not we create default perm
        for perm_name in Permission.DEFAULT_USER_PERMISSIONS:
            gr = _get_group(perm_name)
            if gr not in defined_perms_groups:
                log.debug('GR:%s not found, creating permission %s',
                          gr, perm_name)
                if obj_type == 'user':
                    new_perm = self._make_new_user_perm(obj, perm_name)
                    self.sa.add(new_perm)
                if obj_type == 'user_group':
                    new_perm = self._make_new_user_group_perm(obj, perm_name)
                    self.sa.add(new_perm)

    def create_default_user_permissions(self, user, force=False):
        """
        Creates only missing default permissions for user, if force is set it
        resets the default permissions for that user

        :param user:
        :param force:
        """
        user = self._get_user(user)
        obj_perms = UserToPerm.query().filter(UserToPerm.user == user).all()
        return self._create_default_object_permission(
            'user', user, obj_perms, force)

    def create_default_user_group_permissions(self, user_group, force=False):
        """
        Creates only missing default permissions for user group, if force is set it
        resets the default permissions for that user group

        :param user_group:
        :param force:
        """
        user_group = self._get_user_group(user_group)
        obj_perms = UserToPerm.query().filter(UserGroupToPerm.users_group == user_group).all()
        return self._create_default_object_permission(
            'user_group', user_group, obj_perms, force)

    def update_application_permissions(self, form_result):
        if 'perm_user_id' in form_result:
            perm_user = User.get(safe_int(form_result['perm_user_id']))
        else:
            # used mostly to do lookup for default user
            perm_user = User.get_by_username(form_result['perm_user_name'])

        try:
            # stage 1 set anonymous access
            if perm_user.username == User.DEFAULT_USER:
                perm_user.active = str2bool(form_result['anonymous'])
                self.sa.add(perm_user)

            # stage 2 reset defaults and set them from form data
            self._set_new_user_perms(perm_user, form_result, preserve=[
                'default_repo_perm',
                'default_group_perm',
                'default_user_group_perm',

                'default_repo_group_create',
                'default_user_group_create',
                'default_repo_create_on_write',
                'default_repo_create',
                'default_fork_create',
                'default_inherit_default_permissions',])

            self.sa.commit()
        except (DatabaseError,):
            log.error(traceback.format_exc())
            self.sa.rollback()
            raise

    def update_user_permissions(self, form_result):
        if 'perm_user_id' in form_result:
            perm_user = User.get(safe_int(form_result['perm_user_id']))
        else:
            # used mostly to do lookup for default user
            perm_user = User.get_by_username(form_result['perm_user_name'])
        try:
            # stage 2 reset defaults and set them from form data
            self._set_new_user_perms(perm_user, form_result, preserve=[
                'default_repo_perm',
                'default_group_perm',
                'default_user_group_perm',

                'default_register',
                'default_extern_activate'])
            self.sa.commit()
        except (DatabaseError,):
            log.error(traceback.format_exc())
            self.sa.rollback()
            raise

    def update_user_group_permissions(self, form_result):
        if 'perm_user_group_id' in form_result:
            perm_user_group = UserGroup.get(safe_int(form_result['perm_user_group_id']))
        else:
            # used mostly to do lookup for default user
            perm_user_group = UserGroup.get_by_group_name(form_result['perm_user_group_name'])
        try:
            # stage 2 reset defaults and set them from form data
            self._set_new_user_group_perms(perm_user_group, form_result, preserve=[
                'default_repo_perm',
                'default_group_perm',
                'default_user_group_perm',

                'default_register',
                'default_extern_activate'])
            self.sa.commit()
        except (DatabaseError,):
            log.error(traceback.format_exc())
            self.sa.rollback()
            raise

    def update_object_permissions(self, form_result):
        if 'perm_user_id' in form_result:
            perm_user = User.get(safe_int(form_result['perm_user_id']))
        else:
            # used mostly to do lookup for default user
            perm_user = User.get_by_username(form_result['perm_user_name'])
        try:

            # stage 2 reset defaults and set them from form data
            self._set_new_user_perms(perm_user, form_result, preserve=[
                'default_repo_group_create',
                'default_user_group_create',
                'default_repo_create_on_write',
                'default_repo_create',
                'default_fork_create',
                'default_inherit_default_permissions',

                'default_register',
                'default_extern_activate'])

            # overwrite default repo permissions
            if form_result['overwrite_default_repo']:
                _def_name = form_result['default_repo_perm'].split('repository.')[-1]
                _def = Permission.get_by_key('repository.' + _def_name)
                for r2p in self.sa.query(UserRepoToPerm)\
                               .filter(UserRepoToPerm.user == perm_user)\
                               .all():
                    # don't reset PRIVATE repositories
                    if not r2p.repository.private:
                        r2p.permission = _def
                        self.sa.add(r2p)

            # overwrite default repo group permissions
            if form_result['overwrite_default_group']:
                _def_name = form_result['default_group_perm'].split('group.')[-1]
                _def = Permission.get_by_key('group.' + _def_name)
                for g2p in self.sa.query(UserRepoGroupToPerm)\
                               .filter(UserRepoGroupToPerm.user == perm_user)\
                               .all():
                    g2p.permission = _def
                    self.sa.add(g2p)

            # overwrite default user group permissions
            if form_result['overwrite_default_user_group']:
                _def_name = form_result['default_user_group_perm'].split('usergroup.')[-1]
                # user groups
                _def = Permission.get_by_key('usergroup.' + _def_name)
                for g2p in self.sa.query(UserUserGroupToPerm)\
                               .filter(UserUserGroupToPerm.user == perm_user)\
                               .all():
                    g2p.permission = _def
                    self.sa.add(g2p)
            self.sa.commit()
        except (DatabaseError,):
            log.exception('Failed to set default object permissions')
            self.sa.rollback()
            raise
