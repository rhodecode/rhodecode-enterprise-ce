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
NOTE:
    Place for deprecated APIs here, if a call needs to be deprecated, please
    put it here, and point to a new version
"""
import logging

from rhodecode.api import jsonrpc_method, jsonrpc_deprecated_method
from rhodecode.api.utils import Optional, OAttr


log = logging.getLogger(__name__)


# permission check inside
@jsonrpc_method()
@jsonrpc_deprecated_method(
    use_method='comment_commit', deprecated_at_version='3.4.0')
def changeset_comment(request, apiuser, repoid, revision, message,
                      userid=Optional(OAttr('apiuser')),
                      status=Optional(None)):
    """
    Set a changeset comment, and optionally change the status of the
    changeset.

    This command can only be run using an |authtoken| with admin
    permissions on the |repo|.

    :param apiuser: This is filled automatically from the |authtoken|.
    :type apiuser: AuthUser
    :param repoid: Set the repository name or repository ID.
    :type repoid: str or int
    :param revision: Specify the revision for which to set a comment.
    :type revision: str
    :param message: The comment text.
    :type message: str
    :param userid: Set the user name of the comment creator.
    :type userid: Optional(str or int)
    :param status: Set the comment status. The following are valid options:
        * not_reviewed
        * approved
        * rejected
        * under_review
    :type status: str

    Example error output:

    .. code-block:: json

        {
            "id" : <id_given_in_input>,
            "result" : {
                "msg": "Commented on commit `<revision>` for repository `<repoid>`",
                "status_change": null or <status>,
                "success": true
            },
            "error" : null
        }

    """
    from .repo_api import comment_commit

    return comment_commit(request=request,
        apiuser=apiuser, repoid=repoid, commit_id=revision,
        message=message, userid=userid, status=status)


@jsonrpc_method()
@jsonrpc_deprecated_method(
    use_method='get_ip', deprecated_at_version='4.0.0')
def show_ip(request, apiuser, userid=Optional(OAttr('apiuser'))):
    from .server_api import get_ip
    return get_ip(request=request, apiuser=apiuser, userid=userid)


@jsonrpc_method()
@jsonrpc_deprecated_method(
    use_method='get_user_locks', deprecated_at_version='4.0.0')
def get_locks(request, apiuser, userid=Optional(OAttr('apiuser'))):
    from .user_api import get_user_locks
    return get_user_locks(request=request, apiuser=apiuser, userid=userid)