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
    Optional, OAttr, has_superadmin_permission, get_user_or_error, store_update)
from rhodecode.lib.auth import AuthUser, PasswordGenerator
from rhodecode.lib.exceptions import DefaultUserException
from rhodecode.lib.utils2 import safe_int
from rhodecode.model.db import Session, User, Repository
from rhodecode.model.user import UserModel


log = logging.getLogger(__name__)


@jsonrpc_method()
def get_user(request, apiuser, userid=Optional(OAttr('apiuser'))):
    """
    Returns the information associated with a username or userid.

    * If the ``userid`` is not set, this command returns the information
      for the ``userid`` calling the method.

    .. note::

       Normal users may only run this command against their ``userid``. For
       full privileges you must run this command using an |authtoken| with
       admin rights.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param userid: Sets the userid for which data will be returned.
    :type userid: Optional(str or int)

    Example output:

    .. code-block:: bash

        {
          "error": null,
          "id": <id>,
          "result": {
            "active": true,
            "admin": false,
            "api_key": "api-key",
            "api_keys": [ list of keys ],
            "email": "user@example.com",
            "emails": [
              "user@example.com"
            ],
            "extern_name": "rhodecode",
            "extern_type": "rhodecode",
            "firstname": "username",
            "ip_addresses": [],
            "language": null,
            "last_login": "Timestamp",
            "lastname": "surnae",
            "permissions": {
              "global": [
                "hg.inherit_default_perms.true",
                "usergroup.read",
                "hg.repogroup.create.false",
                "hg.create.none",
                "hg.extern_activate.manual",
                "hg.create.write_on_repogroup.false",
                "hg.usergroup.create.false",
                "group.none",
                "repository.none",
                "hg.register.none",
                "hg.fork.repository"
              ],
              "repositories": { "username/example": "repository.write"},
              "repositories_groups": { "user-group/repo": "group.none" },
              "user_groups": { "user_group_name": "usergroup.read" }
            },
            "user_id": 32,
            "username": "username"
          }
        }
    """

    if not has_superadmin_permission(apiuser):
        # make sure normal user does not pass someone else userid,
        # he is not allowed to do that
        if not isinstance(userid, Optional) and userid != apiuser.user_id:
            raise JSONRPCError('userid is not the same as your user')

    userid = Optional.extract(userid, evaluate_locals=locals())
    userid = getattr(userid, 'user_id', userid)

    user = get_user_or_error(userid)
    data = user.get_api_data(include_secrets=True)
    data['permissions'] = AuthUser(user_id=user.user_id).permissions
    return data


@jsonrpc_method()
def get_users(request, apiuser):
    """
    Lists all users in the |RCE| user database.

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    This command takes the following options:

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
            result: [<user_object>, ...]
        error:  null
    """

    if not has_superadmin_permission(apiuser):
        raise JSONRPCForbidden()

    result = []
    users_list = User.query().order_by(User.username) \
        .filter(User.username != User.DEFAULT_USER) \
        .all()
    for user in users_list:
        result.append(user.get_api_data(include_secrets=True))
    return result


@jsonrpc_method()
def create_user(request, apiuser, username, email, password=Optional(''),
                firstname=Optional(''), lastname=Optional(''),
                active=Optional(True), admin=Optional(False),
                extern_name=Optional('rhodecode'),
                extern_type=Optional('rhodecode'),
                force_password_change=Optional(False)):
    """
    Creates a new user and returns the new user object.

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    This command takes the following options:

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param username: Set the new username.
    :type username: str or int
    :param email: Set the user email address.
    :type email: str
    :param password: Set the new user password.
    :type password: Optional(str)
    :param firstname: Set the new user firstname.
    :type firstname: Optional(str)
    :param lastname: Set the new user surname.
    :type lastname: Optional(str)
    :param active: Set the user as active.
    :type active: Optional(``True`` | ``False``)
    :param admin: Give the new user admin rights.
    :type admin: Optional(``True`` | ``False``)
    :param extern_name: Set the authentication plugin name.
        Using LDAP this is filled with LDAP UID.
    :type extern_name: Optional(str)
    :param extern_type: Set the new user authentication plugin.
    :type extern_type: Optional(str)
    :param force_password_change: Force the new user to change password
        on next login.
    :type force_password_change: Optional(``True`` | ``False``)

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "msg" : "created new user `<username>`",
                  "user": <user_obj>
                }
        error:  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "user `<username>` already exist"
        or
        "email `<email>` already exist"
        or
        "failed to create user `<username>`"
      }

    """
    if not has_superadmin_permission(apiuser):
        raise JSONRPCForbidden()

    if UserModel().get_by_username(username):
        raise JSONRPCError("user `%s` already exist" % (username,))

    if UserModel().get_by_email(email, case_insensitive=True):
        raise JSONRPCError("email `%s` already exist" % (email,))

    # generate random password if we actually given the
    # extern_name and it's not rhodecode
    if (not isinstance(extern_name, Optional) and
                Optional.extract(extern_name) != 'rhodecode'):
        # generate temporary password if user is external
        password = PasswordGenerator().gen_password(length=16)

    try:
        user = UserModel().create_or_update(
            username=Optional.extract(username),
            password=Optional.extract(password),
            email=Optional.extract(email),
            firstname=Optional.extract(firstname),
            lastname=Optional.extract(lastname),
            active=Optional.extract(active),
            admin=Optional.extract(admin),
            extern_type=Optional.extract(extern_type),
            extern_name=Optional.extract(extern_name),
            force_password_change=Optional.extract(force_password_change),
        )
        Session().commit()
        return {
            'msg': 'created new user `%s`' % username,
            'user': user.get_api_data(include_secrets=True)
        }
    except Exception:
        log.exception('Error occurred during creation of user')
        raise JSONRPCError('failed to create user `%s`' % (username,))


@jsonrpc_method()
def update_user(request, apiuser, userid, username=Optional(None),
                email=Optional(None), password=Optional(None),
                firstname=Optional(None), lastname=Optional(None),
                active=Optional(None), admin=Optional(None),
                extern_type=Optional(None), extern_name=Optional(None), ):
    """
    Updates the details for the specified user, if that user exists.

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    This command takes the following options:

    :param apiuser: This is filled automatically from |authtoken|.
    :type apiuser: AuthUser
    :param userid: Set the ``userid`` to update.
    :type userid: str or int
    :param username: Set the new username.
    :type username: str or int
    :param email: Set the new email.
    :type email: str
    :param password: Set the new password.
    :type password: Optional(str)
    :param firstname: Set the new first name.
    :type firstname: Optional(str)
    :param lastname: Set the new surname.
    :type lastname: Optional(str)
    :param active: Set the new user as active.
    :type active: Optional(``True`` | ``False``)
    :param admin: Give the user admin rights.
    :type admin: Optional(``True`` | ``False``)
    :param extern_name: Set the authentication plugin user name.
        Using LDAP this is filled with LDAP UID.
    :type extern_name: Optional(str)
    :param extern_type: Set the authentication plugin type.
    :type extern_type: Optional(str)


    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "msg" : "updated user ID:<userid> <username>",
                  "user": <user_object>,
                }
        error:  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "failed to update user `<username>`"
      }

    """
    if not has_superadmin_permission(apiuser):
        raise JSONRPCForbidden()

    user = get_user_or_error(userid)

    # only non optional arguments will be stored in updates
    updates = {}

    try:

        store_update(updates, username, 'username')
        store_update(updates, password, 'password')
        store_update(updates, email, 'email')
        store_update(updates, firstname, 'name')
        store_update(updates, lastname, 'lastname')
        store_update(updates, active, 'active')
        store_update(updates, admin, 'admin')
        store_update(updates, extern_name, 'extern_name')
        store_update(updates, extern_type, 'extern_type')

        user = UserModel().update_user(user, **updates)
        Session().commit()
        return {
            'msg': 'updated user ID:%s %s' % (user.user_id, user.username),
            'user': user.get_api_data(include_secrets=True)
        }
    except DefaultUserException:
        log.exception("Default user edit exception")
        raise JSONRPCError('editing default user is forbidden')
    except Exception:
        log.exception("Error occurred during update of user")
        raise JSONRPCError('failed to update user `%s`' % (userid,))


@jsonrpc_method()
def delete_user(request, apiuser, userid):
    """
    Deletes the specified user from the |RCE| user database.

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    .. important::

       Ensure all open pull requests and open code review
       requests to this user are close.

       Also ensure all repositories, or repository groups owned by this
       user are reassigned before deletion.

    This command takes the following options:

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param userid: Set the user to delete.
    :type userid: str or int

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result: {
                  "msg" : "deleted user ID:<userid> <username>",
                  "user": null
                }
        error:  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "failed to delete user ID:<userid> <username>"
      }

    """
    if not has_superadmin_permission(apiuser):
        raise JSONRPCForbidden()

    user = get_user_or_error(userid)

    try:
        UserModel().delete(userid)
        Session().commit()
        return {
            'msg': 'deleted user ID:%s %s' % (user.user_id, user.username),
            'user': None
        }
    except Exception:
        log.exception("Error occurred during deleting of user")
        raise JSONRPCError(
            'failed to delete user ID:%s %s' % (user.user_id, user.username))


@jsonrpc_method()
def get_user_locks(request, apiuser, userid=Optional(OAttr('apiuser'))):
    """
    Displays all repositories locked by the specified user.

    * If this command is run by a non-admin user, it returns
      a list of |repos| locked by that user.

    This command takes the following options:

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param userid: Sets the userid whose list of locked |repos| will be
        displayed.
    :type userid: Optional(str or int)

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result : {
            [repo_object, repo_object,...]
        }
        error :  null
    """

    include_secrets = False
    if not has_superadmin_permission(apiuser):
        # make sure normal user does not pass someone else userid,
        # he is not allowed to do that
        if not isinstance(userid, Optional) and userid != apiuser.user_id:
            raise JSONRPCError('userid is not the same as your user')
    else:
        include_secrets = True

    userid = Optional.extract(userid, evaluate_locals=locals())
    userid = getattr(userid, 'user_id', userid)
    user = get_user_or_error(userid)

    ret = []

    # show all locks
    for r in Repository.getAll():
        _user_id, _time, _reason = r.locked
        if _user_id and _time:
            _api_data = r.get_api_data(include_secrets=include_secrets)
            # if we use user filter just show the locks for this user
            if safe_int(_user_id) == user.user_id:
                ret.append(_api_data)

    return ret
