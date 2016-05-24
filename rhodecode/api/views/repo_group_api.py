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

import colander

from rhodecode.api import jsonrpc_method, JSONRPCError, JSONRPCForbidden
from rhodecode.api.utils import (
    has_superadmin_permission, Optional, OAttr, get_user_or_error,
    store_update, get_repo_group_or_error,
    get_perm_or_error, get_user_group_or_error, get_origin)
from rhodecode.lib.auth import (
    HasPermissionAnyApi, HasRepoGroupPermissionAnyApi,
    HasUserGroupPermissionAnyApi)
from rhodecode.model.db import Session, RepoGroup
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.scm import RepoGroupList
from rhodecode.model.validation_schema import RepoGroupSchema


log = logging.getLogger(__name__)


@jsonrpc_method()
def get_repo_group(request, apiuser, repogroupid):
    """
    Return the specified |repo| group, along with permissions,
    and repositories inside the group

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repogroupid: Specify the name of ID of the repository group.
    :type repogroupid: str or int


    Example output:

    .. code-block:: bash

        {
          "error": null,
          "id": repo-group-id,
          "result": {
            "group_description": "repo group description",
            "group_id": 14,
            "group_name": "group name",
            "members": [
              {
                "name": "super-admin-username",
                "origin": "super-admin",
                "permission": "group.admin",
                "type": "user"
              },
              {
                "name": "owner-name",
                "origin": "owner",
                "permission": "group.admin",
                "type": "user"
              },
              {
                "name": "user-group-name",
                "origin": "permission",
                "permission": "group.write",
                "type": "user_group"
              }
            ],
            "owner": "owner-name",
            "parent_group": null,
            "repositories": [ repo-list ]
          }
        }
    """

    repo_group = get_repo_group_or_error(repogroupid)
    if not has_superadmin_permission(apiuser):
        # check if we have at least read permission for this repo group !
        _perms = ('group.admin', 'group.write', 'group.read',)
        if not HasRepoGroupPermissionAnyApi(*_perms)(
                user=apiuser, group_name=repo_group.group_name):
            raise JSONRPCError(
                'repository group `%s` does not exist' % (repogroupid,))

    permissions = []
    for _user in repo_group.permissions():
        user_data = {
            'name': _user.username,
            'permission': _user.permission,
            'origin': get_origin(_user),
            'type': "user",
        }
        permissions.append(user_data)

    for _user_group in repo_group.permission_user_groups():
        user_group_data = {
            'name': _user_group.users_group_name,
            'permission': _user_group.permission,
            'origin': get_origin(_user_group),
            'type': "user_group",
        }
        permissions.append(user_group_data)

    data = repo_group.get_api_data()
    data["members"] = permissions  # TODO: this should be named permissions
    return data


@jsonrpc_method()
def get_repo_groups(request, apiuser):
    """
    Returns all repository groups.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    """

    result = []
    _perms = ('group.read', 'group.write', 'group.admin',)
    extras = {'user': apiuser}
    for repo_group in RepoGroupList(RepoGroupModel().get_all(),
                                    perm_set=_perms, extra_kwargs=extras):
        result.append(repo_group.get_api_data())
    return result


@jsonrpc_method()
def create_repo_group(request, apiuser, group_name, description=Optional(''),
                      owner=Optional(OAttr('apiuser')),
                      copy_permissions=Optional(False)):
    """
    Creates a repository group.

    * If the repository group name contains "/", all the required repository
      groups will be created.

      For example "foo/bar/baz" will create |repo| groups "foo" and "bar"
      (with "foo" as parent). It will also create the "baz" repository
      with "bar" as |repo| group.

    This command can only be run using an |authtoken| with admin
    permissions.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param group_name: Set the repository group name.
    :type group_name: str
    :param description: Set the |repo| group description.
    :type description: str
    :param owner: Set the |repo| group owner.
    :type owner: str
    :param copy_permissions:
    :type copy_permissions:

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
          "msg": "Created new repo group `<repo_group_name>`"
          "repo_group": <repogroup_object>
      }
      error :  null


    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        failed to create repo group `<repogroupid>`
      }

    """

    schema = RepoGroupSchema()
    try:
        data = schema.deserialize({
            'group_name': group_name
        })
    except colander.Invalid as e:
        raise JSONRPCError("Validation failed: %s" % (e.asdict(),))
    group_name = data['group_name']

    if isinstance(owner, Optional):
        owner = apiuser.user_id

    group_description = Optional.extract(description)
    copy_permissions = Optional.extract(copy_permissions)

    # get by full name with parents, check if it already exist
    if RepoGroup.get_by_group_name(group_name):
        raise JSONRPCError("repo group `%s` already exist" % (group_name,))

    (group_name_cleaned,
     parent_group_name) = RepoGroupModel()._get_group_name_and_parent(
        group_name)

    parent_group = None
    if parent_group_name:
        parent_group = get_repo_group_or_error(parent_group_name)

    if not HasPermissionAnyApi(
            'hg.admin', 'hg.repogroup.create.true')(user=apiuser):
        # check if we have admin permission for this parent repo group !
        # users without admin or hg.repogroup.create can only create other
        # groups in groups they own so this is a required, but can be empty
        parent_group = getattr(parent_group, 'group_name', '')
        _perms = ('group.admin',)
        if not HasRepoGroupPermissionAnyApi(*_perms)(
                user=apiuser, group_name=parent_group):
            raise JSONRPCForbidden()

    try:
        repo_group = RepoGroupModel().create(
            group_name=group_name,
            group_description=group_description,
            owner=owner,
            copy_permissions=copy_permissions)
        Session().commit()
        return {
            'msg': 'Created new repo group `%s`' % group_name,
            'repo_group': repo_group.get_api_data()
        }
    except Exception:
        log.exception("Exception occurred while trying create repo group")
        raise JSONRPCError(
            'failed to create repo group `%s`' % (group_name,))


@jsonrpc_method()
def update_repo_group(
        request, apiuser, repogroupid, group_name=Optional(''),
        description=Optional(''), owner=Optional(OAttr('apiuser')),
        parent=Optional(None), enable_locking=Optional(False)):
    """
    Updates repository group with the details given.

    This command can only be run using an |authtoken| with admin
    permissions.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repogroupid: Set the ID of repository group.
    :type repogroupid: str or int
    :param group_name: Set the name of the |repo| group.
    :type group_name: str
    :param description: Set a description for the group.
    :type description: str
    :param owner: Set the |repo| group owner.
    :type owner: str
    :param parent: Set the |repo| group parent.
    :type parent: str or int
    :param enable_locking: Enable |repo| locking. The default is false.
    :type enable_locking: bool
    """

    repo_group = get_repo_group_or_error(repogroupid)
    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this repo group !
        _perms = ('group.admin',)
        if not HasRepoGroupPermissionAnyApi(*_perms)(
                user=apiuser, group_name=repo_group.group_name):
            raise JSONRPCError(
                'repository group `%s` does not exist' % (repogroupid,))

    updates = {}
    try:
        store_update(updates, group_name, 'group_name')
        store_update(updates, description, 'group_description')
        store_update(updates, owner, 'user')
        store_update(updates, parent, 'group_parent_id')
        store_update(updates, enable_locking, 'enable_locking')
        repo_group = RepoGroupModel().update(repo_group, updates)
        Session().commit()
        return {
            'msg': 'updated repository group ID:%s %s' % (
                repo_group.group_id, repo_group.group_name),
            'repo_group': repo_group.get_api_data()
        }
    except Exception:
        log.exception("Exception occurred while trying update repo group")
        raise JSONRPCError('failed to update repository group `%s`'
                           % (repogroupid,))


@jsonrpc_method()
def delete_repo_group(request, apiuser, repogroupid):
    """
    Deletes a |repo| group.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repogroupid: Set the name or ID of repository group to be
        deleted.
    :type repogroupid: str or int

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        'msg': 'deleted repo group ID:<repogroupid> <repogroupname>
        'repo_group': null
      }
      error :  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "failed to delete repo group ID:<repogroupid> <repogroupname>"
      }

    """

    repo_group = get_repo_group_or_error(repogroupid)
    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this repo group !
        _perms = ('group.admin',)
        if not HasRepoGroupPermissionAnyApi(*_perms)(
                user=apiuser, group_name=repo_group.group_name):
            raise JSONRPCError(
                'repository group `%s` does not exist' % (repogroupid,))
    try:
        RepoGroupModel().delete(repo_group)
        Session().commit()
        return {
            'msg': 'deleted repo group ID:%s %s' %
                   (repo_group.group_id, repo_group.group_name),
            'repo_group': None
        }
    except Exception:
        log.exception("Exception occurred while trying to delete repo group")
        raise JSONRPCError('failed to delete repo group ID:%s %s' %
                           (repo_group.group_id, repo_group.group_name))


@jsonrpc_method()
def grant_user_permission_to_repo_group(
        request, apiuser, repogroupid, userid, perm,
        apply_to_children=Optional('none')):
    """
    Grant permission for a user on the given repository group, or update
    existing permissions if found.

    This command can only be run using an |authtoken| with admin
    permissions.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repogroupid: Set the name or ID of repository group.
    :type repogroupid: str or int
    :param userid: Set the user name.
    :type userid: str
    :param perm: (group.(none|read|write|admin))
    :type perm: str
    :param apply_to_children: 'none', 'repos', 'groups', 'all'
    :type apply_to_children: str

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "msg" : "Granted perm: `<perm>` (recursive:<apply_to_children>) for user: `<username>` in repo group: `<repo_group_name>`",
                  "success": true
                }
        error:  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "failed to edit permission for user: `<userid>` in repo group: `<repo_group_name>`"
      }

    """

    repo_group = get_repo_group_or_error(repogroupid)

    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this repo group !
        _perms = ('group.admin',)
        if not HasRepoGroupPermissionAnyApi(*_perms)(
                user=apiuser, group_name=repo_group.group_name):
            raise JSONRPCError(
                'repository group `%s` does not exist' % (repogroupid,))

    user = get_user_or_error(userid)
    perm = get_perm_or_error(perm, prefix='group.')
    apply_to_children = Optional.extract(apply_to_children)

    perm_additions = [[user.user_id, perm, "user"]]
    try:
        RepoGroupModel().update_permissions(repo_group=repo_group,
                                            perm_additions=perm_additions,
                                            recursive=apply_to_children,
                                            cur_user=apiuser)
        Session().commit()
        return {
            'msg': 'Granted perm: `%s` (recursive:%s) for user: '
                   '`%s` in repo group: `%s`' % (
                       perm.permission_name, apply_to_children, user.username,
                       repo_group.name
                   ),
            'success': True
        }
    except Exception:
        log.exception("Exception occurred while trying to grant "
                      "user permissions to repo group")
        raise JSONRPCError(
            'failed to edit permission for user: '
            '`%s` in repo group: `%s`' % (userid, repo_group.name))


@jsonrpc_method()
def revoke_user_permission_from_repo_group(
        request, apiuser, repogroupid, userid,
        apply_to_children=Optional('none')):
    """
    Revoke permission for a user in a given repository group.

    This command can only be run using an |authtoken| with admin
    permissions on the |repo| group.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repogroupid: Set the name or ID of the repository group.
    :type repogroupid: str or int
    :param userid: Set the user name to revoke.
    :type userid: str
    :param apply_to_children: 'none', 'repos', 'groups', 'all'
    :type apply_to_children: str

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "msg" : "Revoked perm (recursive:<apply_to_children>) for user: `<username>` in repo group: `<repo_group_name>`",
                  "success": true
                }
        error:  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "failed to edit permission for user: `<userid>` in repo group: `<repo_group_name>`"
      }

    """

    repo_group = get_repo_group_or_error(repogroupid)

    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this repo group !
        _perms = ('group.admin',)
        if not HasRepoGroupPermissionAnyApi(*_perms)(
                user=apiuser, group_name=repo_group.group_name):
            raise JSONRPCError(
                'repository group `%s` does not exist' % (repogroupid,))

    user = get_user_or_error(userid)
    apply_to_children = Optional.extract(apply_to_children)

    perm_deletions = [[user.user_id, None, "user"]]
    try:
        RepoGroupModel().update_permissions(repo_group=repo_group,
                                            perm_deletions=perm_deletions,
                                            recursive=apply_to_children,
                                            cur_user=apiuser)
        Session().commit()
        return {
            'msg': 'Revoked perm (recursive:%s) for user: '
                   '`%s` in repo group: `%s`' % (
                       apply_to_children, user.username, repo_group.name
                   ),
            'success': True
        }
    except Exception:
        log.exception("Exception occurred while trying revoke user "
                      "permission from repo group")
        raise JSONRPCError(
            'failed to edit permission for user: '
            '`%s` in repo group: `%s`' % (userid, repo_group.name))


@jsonrpc_method()
def grant_user_group_permission_to_repo_group(
        request, apiuser, repogroupid, usergroupid, perm,
        apply_to_children=Optional('none'), ):
    """
    Grant permission for a user group on given repository group, or update
    existing permissions if found.

    This command can only be run using an |authtoken| with admin
    permissions on the |repo| group.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repogroupid: Set the name or id of repository group
    :type repogroupid: str or int
    :param usergroupid: id of usergroup
    :type usergroupid: str or int
    :param perm: (group.(none|read|write|admin))
    :type perm: str
    :param apply_to_children: 'none', 'repos', 'groups', 'all'
    :type apply_to_children: str

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        "msg" : "Granted perm: `<perm>` (recursive:<apply_to_children>) for user group: `<usersgroupname>` in repo group: `<repo_group_name>`",
        "success": true

      }
      error :  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "failed to edit permission for user group: `<usergroup>` in repo group: `<repo_group_name>`"
      }

    """

    repo_group = get_repo_group_or_error(repogroupid)
    perm = get_perm_or_error(perm, prefix='group.')
    user_group = get_user_group_or_error(usergroupid)
    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this repo group !
        _perms = ('group.admin',)
        if not HasRepoGroupPermissionAnyApi(*_perms)(
                user=apiuser, group_name=repo_group.group_name):
            raise JSONRPCError(
                'repository group `%s` does not exist' % (repogroupid,))

        # check if we have at least read permission for this user group !
        _perms = ('usergroup.read', 'usergroup.write', 'usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser, user_group_name=user_group.users_group_name):
            raise JSONRPCError(
                'user group `%s` does not exist' % (usergroupid,))

    apply_to_children = Optional.extract(apply_to_children)

    perm_additions = [[user_group.users_group_id, perm, "user_group"]]
    try:
        RepoGroupModel().update_permissions(repo_group=repo_group,
                                            perm_additions=perm_additions,
                                            recursive=apply_to_children,
                                            cur_user=apiuser)
        Session().commit()
        return {
            'msg': 'Granted perm: `%s` (recursive:%s) '
                   'for user group: `%s` in repo group: `%s`' % (
                       perm.permission_name, apply_to_children,
                       user_group.users_group_name, repo_group.name
                   ),
            'success': True
        }
    except Exception:
        log.exception("Exception occurred while trying to grant user "
                      "group permissions to repo group")
        raise JSONRPCError(
            'failed to edit permission for user group: `%s` in '
            'repo group: `%s`' % (
                usergroupid, repo_group.name
            )
        )


@jsonrpc_method()
def revoke_user_group_permission_from_repo_group(
        request, apiuser, repogroupid, usergroupid,
        apply_to_children=Optional('none')):
    """
    Revoke permission for user group on given repository.

    This command can only be run using an |authtoken| with admin
    permissions on the |repo| group.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repogroupid: name or id of repository group
    :type repogroupid: str or int
    :param usergroupid:
    :param apply_to_children: 'none', 'repos', 'groups', 'all'
    :type apply_to_children: str

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "msg" : "Revoked perm (recursive:<apply_to_children>) for user group: `<usersgroupname>` in repo group: `<repo_group_name>`",
                  "success": true
                }
        error:  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "failed to edit permission for user group: `<usergroup>` in repo group: `<repo_group_name>`"
      }


    """

    repo_group = get_repo_group_or_error(repogroupid)
    user_group = get_user_group_or_error(usergroupid)
    if not has_superadmin_permission(apiuser):
        # check if we have admin permission for this repo group !
        _perms = ('group.admin',)
        if not HasRepoGroupPermissionAnyApi(*_perms)(
                user=apiuser, group_name=repo_group.group_name):
            raise JSONRPCError(
                'repository group `%s` does not exist' % (repogroupid,))

        # check if we have at least read permission for this user group !
        _perms = ('usergroup.read', 'usergroup.write', 'usergroup.admin',)
        if not HasUserGroupPermissionAnyApi(*_perms)(
                user=apiuser, user_group_name=user_group.users_group_name):
            raise JSONRPCError(
                'user group `%s` does not exist' % (usergroupid,))

    apply_to_children = Optional.extract(apply_to_children)

    perm_deletions = [[user_group.users_group_id, None, "user_group"]]
    try:
        RepoGroupModel().update_permissions(repo_group=repo_group,
                                            perm_deletions=perm_deletions,
                                            recursive=apply_to_children,
                                            cur_user=apiuser)
        Session().commit()
        return {
            'msg': 'Revoked perm (recursive:%s) for user group: '
                   '`%s` in repo group: `%s`' % (
                       apply_to_children, user_group.users_group_name,
                       repo_group.name
                   ),
            'success': True
        }
    except Exception:
        log.exception("Exception occurred while trying revoke user group "
                      "permissions from repo group")
        raise JSONRPCError(
            'failed to edit permission for user group: '
            '`%s` in repo group: `%s`' % (
                user_group.users_group_name, repo_group.name
            )
        )

