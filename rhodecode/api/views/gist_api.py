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
import time

from rhodecode.api import jsonrpc_method, JSONRPCError
from rhodecode.api.utils import (
    Optional, OAttr, get_gist_or_error, get_user_or_error,
    has_superadmin_permission)
from rhodecode.model.db import Session, or_
from rhodecode.model.gist import Gist, GistModel

log = logging.getLogger(__name__)


@jsonrpc_method()
def get_gist(request, apiuser, gistid, content=Optional(False)):
    """
    Get the specified gist, based on the gist ID.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param gistid: Set the id of the private or public gist
    :type gistid: str
    :param content: Return the gist content. Default is false.
    :type content: Optional(bool)
    """

    gist = get_gist_or_error(gistid)
    content = Optional.extract(content)
    if not has_superadmin_permission(apiuser):
        if gist.gist_owner != apiuser.user_id:
            raise JSONRPCError('gist `%s` does not exist' % (gistid,))
    data = gist.get_api_data()
    if content:
        from rhodecode.model.gist import GistModel
        rev, gist_files = GistModel().get_gist_files(gistid)
        data['content'] = dict([(x.path, x.content) for x in gist_files])
    return data


@jsonrpc_method()
def get_gists(request, apiuser, userid=Optional(OAttr('apiuser'))):
    """
    Get all gists for given user. If userid is empty returned gists
    are for user who called the api

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param userid: user to get gists for
    :type userid: Optional(str or int)
    """

    if not has_superadmin_permission(apiuser):
        # make sure normal user does not pass someone else userid,
        # he is not allowed to do that
        if not isinstance(userid, Optional) and userid != apiuser.user_id:
            raise JSONRPCError(
                'userid is not the same as your user'
            )

    if isinstance(userid, Optional):
        user_id = apiuser.user_id
    else:
        user_id = get_user_or_error(userid).user_id

    gists = []
    _gists = Gist().query() \
        .filter(or_(
        Gist.gist_expires == -1, Gist.gist_expires >= time.time())) \
        .filter(Gist.gist_owner == user_id) \
        .order_by(Gist.created_on.desc())
    for gist in _gists:
        gists.append(gist.get_api_data())
    return gists


@jsonrpc_method()
def create_gist(
        request, apiuser, files, owner=Optional(OAttr('apiuser')),
        gist_type=Optional(Gist.GIST_PUBLIC), lifetime=Optional(-1),
        acl_level=Optional(Gist.ACL_LEVEL_PUBLIC),
        description=Optional('')):
    """
    Creates a new Gist.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param files: files to be added to the gist. The data structure has
        to match the following example::

          {'filename': {'content':'...', 'lexer': null},
           'filename2': {'content':'...', 'lexer': null}}

    :type files: dict
    :param owner: Set the gist owner, defaults to api method caller
    :type owner: Optional(str or int)
    :param gist_type: type of gist ``public`` or ``private``
    :type gist_type: Optional(str)
    :param lifetime: time in minutes of gist lifetime
    :type lifetime: Optional(int)
    :param acl_level: acl level for this gist, can be
        ``acl_public`` or ``acl_private`` If the value is set to
        ``acl_private`` only logged in users are able to access this gist.
        If not set it defaults to ``acl_public``.
    :type acl_level: Optional(str)
    :param description: gist description
    :type description: Optional(str)

    Example  output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        "msg": "created new gist",
        "gist": {}
      }
      error :  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "failed to create gist"
      }

    """

    try:
        if isinstance(owner, Optional):
            owner = apiuser.user_id

        owner = get_user_or_error(owner)
        description = Optional.extract(description)
        gist_type = Optional.extract(gist_type)
        lifetime = Optional.extract(lifetime)
        acl_level = Optional.extract(acl_level)

        gist = GistModel().create(description=description,
                                  owner=owner,
                                  gist_mapping=files,
                                  gist_type=gist_type,
                                  lifetime=lifetime,
                                  gist_acl_level=acl_level)
        Session().commit()
        return {
            'msg': 'created new gist',
            'gist': gist.get_api_data()
        }
    except Exception:
        log.exception('Error occurred during creation of gist')
        raise JSONRPCError('failed to create gist')


@jsonrpc_method()
def delete_gist(request, apiuser, gistid):
    """
    Deletes existing gist

    :param apiuser: filled automatically from apikey
    :type apiuser: AuthUser
    :param gistid: id of gist to delete
    :type gistid: str

    Example output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : {
        "deleted gist ID: <gist_id>",
        "gist": null
      }
      error :  null

    Example error output:

    .. code-block:: bash

      id : <id_given_in_input>
      result : null
      error :  {
        "failed to delete gist ID:<gist_id>"
      }

    """

    gist = get_gist_or_error(gistid)
    if not has_superadmin_permission(apiuser):
        if gist.gist_owner != apiuser.user_id:
            raise JSONRPCError('gist `%s` does not exist' % (gistid,))

    try:
        GistModel().delete(gist)
        Session().commit()
        return {
            'msg': 'deleted gist ID:%s' % (gist.gist_access_id,),
            'gist': None
        }
    except Exception:
        log.exception('Error occured during gist deletion')
        raise JSONRPCError('failed to delete gist ID:%s'
                           % (gist.gist_access_id,))