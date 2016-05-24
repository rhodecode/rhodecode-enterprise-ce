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

import logging

from rhodecode.api import jsonrpc_method, JSONRPCError, JSONRPCForbidden
from rhodecode.api.utils import (
    Optional, OAttr, store_update, has_superadmin_permission, get_origin,
    get_user_or_error, get_user_group_or_error, get_perm_or_error)
from rhodecode.lib.auth import HasUserGroupPermissionAnyApi, HasPermissionAnyApi
from rhodecode.lib.exceptions import UserGroupAssignedException
from rhodecode.model.db import Session
from rhodecode.model.scm import UserGroupList
from rhodecode.model.user_group import UserGroupModel

log = logging.getLogger(__name__)


@jsonrpc_method()
def get_user_group(request, apiuser, usergroupid):
    """
    Returns the data of an existing user group.

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param usergroupid: Set the user group from which to return data.
    :type usergroupid: str or int

    Example error output:

    .. code-block:: bash

        {
          "error": null,
          "id": <id>,
          "result": {
            "active": true,
            "group_description": "group description",
            "group_name": "group name",
            "members": [
              {
                "name": "owner-name",
                "origin": "owner",
                "permission": "usergroup.admin",
                "type": "user"
              },
              {
              {
                "name": "user name",
                "origin": "permission",
                "permission": "usergroup.admin",
                "type": "user"
              },
              {
                "name": "user group name",
                "origin": "permission",
                "permission": "usergroup.write",
                "type": "user_group"
              }
            ],
            "owner": "owner name",
            "users": [],
            "users_group_id": 2
          }
        }

    """

    user_group = get_user_group_or_error(usergroupid)
    if not has_superadmin_permission(apiuser):
        # check if we have at least read permission for this user group !
        _perms = ('usergroup.read', 'usergroup.write', 'usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser, user_group_name=user_group.users_group_name):
            raise JSONRPCError('user group `%s` does not exist' % (
                usergroupid,))

    permissions = []
    for _user in user_group.permissions():
        user_data = {
            'name': _user.username,
            'permission': _user.permission,
            'origin': get_origin(_user),
            'type': "user",
        }
        permissions.append(user_data)

    for _user_group in user_group.permission_user_groups():
        user_group_data = {
            'name': _user_group.users_group_name,
            'permission': _user_group.permission,
            'origin': get_origin(_user_group),
            'type': "user_group",
        }
        permissions.append(user_group_data)

    data = user_group.get_api_data()
    data['members'] = permissions

    return data


@jsonrpc_method()
def get_user_groups(request, apiuser):
    """
    Lists all the existing user groups within RhodeCode.

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    This command takes the following options:

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser

    Example error output:

    .. code-block:: bash

        id : <id_given_in_input>
        result : [<user_group_obj>,...]
        error : null
    """

    include_secrets = has_superadmin_permission(apiuser)

    result = []
    _perms = ('usergroup.read', 'usergroup.write', 'usergroup.admin',)
    extras = {'user': apiuser}
    for user_group in UserGroupList(UserGroupModel().get_all(),
                                    perm_set=_perms, extra_kwargs=extras):
        result.append(
            user_group.get_api_data(include_secrets=include_secrets))
    return result


@jsonrpc_method()
def create_user_group(
        request, apiuser, group_name, description=Optional(''),
        owner=Optional(OAttr('apiuser')), active=Optional(True)):
    """
    Creates a new user group.

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    This command takes the following options:

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param group_name: Set the name of the new user group.
    :type group_name: str
    :param description: Give a description of the new user group.
    :type description: str
    :param owner: Set the owner of the new user group.
        If not set, the owner is the |authtoken| user.
    :type owner: Optional(str or int)
    :param active: Set this group as active.
    :type active: Optional(``True`` | ``False``)

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "msg": "created new user group `<groupname>`",
                  "user_group": <user_group_object>
                }
        error:  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "user group `<group name>` already exist"
        or
        "failed to create group `<group name>`"
      }

    """

    if not has_superadmin_permission(apiuser):
        if not HasPermissionAnyApi('hg.usergroup.create.true')(user=apiuser):
            raise JSONRPCForbidden()

    if UserGroupModel().get_by_name(group_name):
        raise JSONRPCError("user group `%s` already exist" % (group_name,))

    try:
        if isinstance(owner, Optional):
            owner = apiuser.user_id

        owner = get_user_or_error(owner)
        active = Optional.extract(active)
        description = Optional.extract(description)
        ug = UserGroupModel().create(
            name=group_name, description=description, owner=owner,
            active=active)
        Session().commit()
        return {
            'msg': 'created new user group `%s`' % group_name,
            'user_group': ug.get_api_data()
        }
    except Exception:
        log.exception("Error occurred during creation of user group")
        raise JSONRPCError('failed to create group `%s`' % (group_name,))


@jsonrpc_method()
def update_user_group(request, apiuser, usergroupid, group_name=Optional(''),
                      description=Optional(''), owner=Optional(None),
                      active=Optional(True)):
    """
    Updates the specified `user group` with the details provided.

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param usergroupid: Set the id of the `user group` to update.
    :type usergroupid: str or int
    :param group_name: Set the new name the `user group`
    :type group_name: str
    :param description: Give a description for the `user group`
    :type description: str
    :param owner: Set the owner of the `user group`.
    :type owner: Optional(str or int)
    :param active: Set the group as active.
    :type active: Optional(``True`` | ``False``)

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        "msg": 'updated user group ID:<user group id> <user group name>',
        "user_group": <user_group_object>
      }
      error :  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "failed to update user group `<user group name>`"
      }

    """

    user_group = get_user_group_or_error(usergroupid)
    include_secrets = False
    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this user group !
        _perms = ('usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser, user_group_name=user_group.users_group_name):
            raise JSONRPCError(
                'user group `%s` does not exist' % (usergroupid,))
    else:
        include_secrets = True

    if not isinstance(owner, Optional):
        owner = get_user_or_error(owner)

    updates = {}
    store_update(updates, group_name, 'users_group_name')
    store_update(updates, description, 'user_group_description')
    store_update(updates, owner, 'user')
    store_update(updates, active, 'users_group_active')
    try:
        UserGroupModel().update(user_group, updates)
        Session().commit()
        return {
            'msg': 'updated user group ID:%s %s' % (
                user_group.users_group_id, user_group.users_group_name),
            'user_group': user_group.get_api_data(
                include_secrets=include_secrets)
        }
    except Exception:
        log.exception("Error occurred during update of user group")
        raise JSONRPCError(
            'failed to update user group `%s`' % (usergroupid,))


@jsonrpc_method()
def delete_user_group(request, apiuser, usergroupid):
    """
    Deletes the specified `user group`.

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    This command takes the following options:

    :param apiuser: filled automatically from apikey
    :type apiuser: AuthUser
    :param usergroupid:
    :type usergroupid: int

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        "msg": "deleted user group ID:<user_group_id> <user_group_name>"
      }
      error :  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "failed to delete user group ID:<user_group_id> <user_group_name>"
        or
        "RepoGroup assigned to <repo_groups_list>"
      }

    """

    user_group = get_user_group_or_error(usergroupid)
    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this user group !
        _perms = ('usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser, user_group_name=user_group.users_group_name):
            raise JSONRPCError(
                'user group `%s` does not exist' % (usergroupid,))

    try:
        UserGroupModel().delete(user_group)
        Session().commit()
        return {
            'msg': 'deleted user group ID:%s %s' % (
                user_group.users_group_id, user_group.users_group_name),
            'user_group': None
        }
    except UserGroupAssignedException as e:
        log.exception("UserGroupAssigned error")
        raise JSONRPCError(str(e))
    except Exception:
        log.exception("Error occurred during deletion of user group")
        raise JSONRPCError(
            'failed to delete user group ID:%s %s' %(
                user_group.users_group_id, user_group.users_group_name))


@jsonrpc_method()
def add_user_to_user_group(request, apiuser, usergroupid, userid):
    """
    Adds a user to a `user group`. If the user already exists in the group
    this command will return false.

    This command can only be run using an |authtoken| with admin rights to
    the specified user group.

    This command takes the following options:

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param usergroupid: Set the name of the `user group` to which a
        user will be added.
    :type usergroupid: int
    :param userid: Set the `user_id` of the user to add to the group.
    :type userid: int

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
          "success": True|False # depends on if member is in group
          "msg": "added member `<username>` to user group `<groupname>` |
                  User is already in that group"

      }
      error :  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "failed to add member to user group `<user_group_name>`"
      }

    """

    user = get_user_or_error(userid)
    user_group = get_user_group_or_error(usergroupid)
    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this user group !
        _perms = ('usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser, user_group_name=user_group.users_group_name):
            raise JSONRPCError('user group `%s` does not exist' % (
                usergroupid,))

    try:
        ugm = UserGroupModel().add_user_to_group(user_group, user)
        success = True if ugm is not True else False
        msg = 'added member `%s` to user group `%s`' % (
            user.username, user_group.users_group_name
        )
        msg = msg if success else 'User is already in that group'
        Session().commit()

        return {
            'success': success,
            'msg': msg
        }
    except Exception:
        log.exception("Error occurred during adding a member to user group")
        raise JSONRPCError(
            'failed to add member to user group `%s`' % (
                user_group.users_group_name,
            )
        )


@jsonrpc_method()
def remove_user_from_user_group(request, apiuser, usergroupid, userid):
    """
    Removes a user from a user group.

    * If the specified user is not in the group, this command will return
      `false`.

    This command can only be run using an |authtoken| with admin rights to
    the specified user group.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param usergroupid: Sets the user group name.
    :type usergroupid: str or int
    :param userid: The user you wish to remove from |RCE|.
    :type userid: str or int

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "success":  True|False,  # depends on if member is in group
                  "msg": "removed member <username> from user group <groupname> |
                          User wasn't in group"
                }
        error:  null

    """

    user = get_user_or_error(userid)
    user_group = get_user_group_or_error(usergroupid)
    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this user group !
        _perms = ('usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser, user_group_name=user_group.users_group_name):
            raise JSONRPCError(
                'user group `%s` does not exist' % (usergroupid,))

    try:
        success = UserGroupModel().remove_user_from_group(user_group, user)
        msg = 'removed member `%s` from user group `%s`' % (
            user.username, user_group.users_group_name
        )
        msg = msg if success else "User wasn't in group"
        Session().commit()
        return {'success': success, 'msg': msg}
    except Exception:
        log.exception("Error occurred during removing an member from user group")
        raise JSONRPCError(
            'failed to remove member from user group `%s`' % (
                user_group.users_group_name,
            )
        )


@jsonrpc_method()
def grant_user_permission_to_user_group(
        request, apiuser, usergroupid, userid, perm):
    """
    Set permissions for a user in a user group.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param usergroupid: Set the user group to edit permissions on.
    :type usergroupid: str or int
    :param userid: Set the user from whom you wish to set permissions.
    :type userid: str
    :param perm: (usergroup.(none|read|write|admin))
    :type perm: str

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        "msg": "Granted perm: `<perm_name>` for user: `<username>` in user group: `<user_group_name>`",
        "success": true
      }
      error :  null
    """

    user_group = get_user_group_or_error(usergroupid)

    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this user group !
        _perms = ('usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser, user_group_name=user_group.users_group_name):
            raise JSONRPCError(
                'user group `%s` does not exist' % (usergroupid,))

    user = get_user_or_error(userid)
    perm = get_perm_or_error(perm, prefix='usergroup.')

    try:
        UserGroupModel().grant_user_permission(
            user_group=user_group, user=user, perm=perm)
        Session().commit()
        return {
            'msg':
                'Granted perm: `%s` for user: `%s` in user group: `%s`' % (
                    perm.permission_name, user.username,
                    user_group.users_group_name
                ),
            'success': True
        }
    except Exception:
        log.exception("Error occurred during editing permissions "
                      "for user in user group")
        raise JSONRPCError(
            'failed to edit permission for user: '
            '`%s` in user group: `%s`' % (
                userid, user_group.users_group_name))


@jsonrpc_method()
def revoke_user_permission_from_user_group(
        request, apiuser, usergroupid, userid):
    """
    Revoke a users permissions in a user group.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param usergroupid: Set the user group from which to revoke the user
        permissions.
    :type: usergroupid: str or int
    :param userid: Set the userid of the user whose permissions will be
        revoked.
    :type userid: str

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        "msg": "Revoked perm for user: `<username>` in user group: `<user_group_name>`",
        "success": true
      }
      error :  null
    """

    user_group = get_user_group_or_error(usergroupid)

    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this user group !
        _perms = ('usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser, user_group_name=user_group.users_group_name):
            raise JSONRPCError(
                'user group `%s` does not exist' % (usergroupid,))

    user = get_user_or_error(userid)

    try:
        UserGroupModel().revoke_user_permission(
            user_group=user_group, user=user)
        Session().commit()
        return {
            'msg': 'Revoked perm for user: `%s` in user group: `%s`' % (
                user.username, user_group.users_group_name
            ),
            'success': True
        }
    except Exception:
        log.exception("Error occurred during editing permissions "
                      "for user in user group")
        raise JSONRPCError(
            'failed to edit permission for user: `%s` in user group: `%s`'
            % (userid, user_group.users_group_name))


@jsonrpc_method()
def grant_user_group_permission_to_user_group(
        request, apiuser, usergroupid, sourceusergroupid, perm):
    """
    Give one user group permissions to another user group.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param usergroupid: Set the user group on which to edit permissions.
    :type usergroupid: str or int
    :param sourceusergroupid: Set the source user group to which
        access/permissions will be granted.
    :type sourceusergroupid: str or int
    :param perm: (usergroup.(none|read|write|admin))
    :type perm: str

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        "msg": "Granted perm: `<perm_name>` for user group: `<source_user_group_name>` in user group: `<user_group_name>`",
        "success": true
      }
      error :  null
    """

    user_group = get_user_group_or_error(sourceusergroupid)
    target_user_group = get_user_group_or_error(usergroupid)
    perm = get_perm_or_error(perm, prefix='usergroup.')

    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this user group !
        _perms = ('usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser,
                user_group_name=target_user_group.users_group_name):
            raise JSONRPCError(
                'to user group `%s` does not exist' % (usergroupid,))

        # check if we have at least read permission for source user group !
        _perms = ('usergroup.read', 'usergroup.write', 'usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser, user_group_name=user_group.users_group_name):
            raise JSONRPCError(
                'user group `%s` does not exist' % (sourceusergroupid,))

    try:
        UserGroupModel().grant_user_group_permission(
            target_user_group=target_user_group,
            user_group=user_group, perm=perm)
        Session().commit()

        return {
            'msg': 'Granted perm: `%s` for user group: `%s` '
                   'in user group: `%s`' % (
                       perm.permission_name, user_group.users_group_name,
                       target_user_group.users_group_name
                   ),
            'success': True
        }
    except Exception:
        log.exception("Error occurred during editing permissions "
                      "for user group in user group")
        raise JSONRPCError(
            'failed to edit permission for user group: `%s` in '
            'user group: `%s`' % (
                sourceusergroupid, target_user_group.users_group_name
            )
        )


@jsonrpc_method()
def revoke_user_group_permission_from_user_group(
        request, apiuser, usergroupid, sourceusergroupid):
    """
    Revoke the permissions that one user group has to another.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param usergroupid: Set the user group on which to edit permissions.
    :type usergroupid: str or int
    :param sourceusergroupid: Set the user group from which permissions
        are revoked.
    :type sourceusergroupid: str or int

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        "msg": "Revoked perm for user group: `<user_group_name>` in user group: `<target_user_group_name>`",
        "success": true
      }
      error :  null
    """

    user_group = get_user_group_or_error(sourceusergroupid)
    target_user_group = get_user_group_or_error(usergroupid)

    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this user group !
        _perms = ('usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser,
                user_group_name=target_user_group.users_group_name):
            raise JSONRPCError(
                'to user group `%s` does not exist' % (usergroupid,))

        # check if we have at least read permission
        # for the source user group !
        _perms = ('usergroup.read', 'usergroup.write', 'usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser, user_group_name=user_group.users_group_name):
            raise JSONRPCError(
                'user group `%s` does not exist' % (sourceusergroupid,))

    try:
        UserGroupModel().revoke_user_group_permission(
            target_user_group=target_user_group, user_group=user_group)
        Session().commit()

        return {
            'msg': 'Revoked perm for user group: '
                   '`%s` in user group: `%s`' % (
                       user_group.users_group_name,
                       target_user_group.users_group_name
                   ),
            'success': True
        }
    except Exception:
        log.exception("Error occurred during editing permissions "
                      "for user group in user group")
        raise JSONRPCError(
            'failed to edit permission for user group: '
            '`%s` in user group: `%s`' % (
                sourceusergroupid, target_user_group.users_group_name
            )
        )
