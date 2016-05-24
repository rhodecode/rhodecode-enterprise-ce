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
    Optional, OAttr, has_superadmin_permission, get_user_or_error)
from rhodecode.lib.utils import repo2db_mapper
from rhodecode.model.db import UserIpMap
from rhodecode.model.scm import ScmModel

log = logging.getLogger(__name__)


@jsonrpc_method()
def get_server_info(request, apiuser):
    """
    Returns the |RCE| server information.

    This includes the running version of |RCE| and all installed
    packages. This command takes the following options:

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        'modules': [<module name>,...]
        'py_version': <python version>,
        'platform': <platform type>,
        'rhodecode_version': <rhodecode version>
      }
      error :  null
    """

    if not has_superadmin_permission(apiuser):
        raise JSONRPCForbidden()

    return ScmModel().get_server_info(request.environ)


@jsonrpc_method()
def get_ip(request, apiuser, userid=Optional(OAttr('apiuser'))):
    """
    Displays the IP Address as seen from the |RCE| server.

    * This command displays the IP Address, as well as all the defined IP
      addresses for the specified user. If the ``userid`` is not set, the
      data returned is for the user calling the method.

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    This command takes the following options:

    :param apiuser: This is filled automatically from |authtoken|.
    :type apiuser: AuthUser
    :param userid: Sets the userid for which associated IP Address data
        is returned.
    :type userid: Optional(str or int)

    Example output:

    .. code-block:: bash

        id : <id_given_in_input>
        result : {
                     "server_ip_addr": "<ip_from_clien>",
                     "user_ips": [
                                    {
                                       "ip_addr": "<ip_with_mask>",
                                       "ip_range": ["<start_ip>", "<end_ip>"],
                                    },
                                    ...
                                 ]
        }

    """
    if not has_superadmin_permission(apiuser):
        raise JSONRPCForbidden()

    userid = Optional.extract(userid, evaluate_locals=locals())
    userid = getattr(userid, 'user_id', userid)

    user = get_user_or_error(userid)
    ips = UserIpMap.query().filter(UserIpMap.user == user).all()
    return {
        'server_ip_addr': request.rpc_ip_addr,
        'user_ips': ips
    }


@jsonrpc_method()
def rescan_repos(request, apiuser, remove_obsolete=Optional(False)):
    """
    Triggers a rescan of the specified repositories.

    * If the ``remove_obsolete`` option is set, it also deletes repositories
      that are found in the database but not on the file system, so called
      "clean zombies".

    This command can only be run using an |authtoken| with admin rights to
    the specified repository.

    This command takes the following options:

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param remove_obsolete: Deletes repositories from the database that
        are not found on the filesystem.
    :type remove_obsolete: Optional(``True`` | ``False``)

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        'added': [<added repository name>,...]
        'removed': [<removed repository name>,...]
      }
      error :  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        'Error occurred during rescan repositories action'
      }

    """
    if not has_superadmin_permission(apiuser):
        raise JSONRPCForbidden()

    try:
        rm_obsolete = Optional.extract(remove_obsolete)
        added, removed = repo2db_mapper(ScmModel().repo_scan(),
                                        remove_obsolete=rm_obsolete)
        return {'added': added, 'removed': removed}
    except Exception:
        log.exception('Failed to run repo rescann')
        raise JSONRPCError(
            'Error occurred during rescan repositories action'
        )

