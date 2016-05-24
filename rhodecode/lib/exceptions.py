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
Set of custom exceptions used in RhodeCode
"""

from webob.exc import HTTPClientError


class LdapUsernameError(Exception):
    pass


class LdapPasswordError(Exception):
    pass


class LdapConnectionError(Exception):
    pass


class LdapImportError(Exception):
    pass


class DefaultUserException(Exception):
    pass


class UserOwnsReposException(Exception):
    pass


class UserOwnsRepoGroupsException(Exception):
    pass


class UserOwnsUserGroupsException(Exception):
    pass


class UserGroupAssignedException(Exception):
    pass


class StatusChangeOnClosedPullRequestError(Exception):
    pass


class AttachedForksError(Exception):
    pass


class RepoGroupAssignmentError(Exception):
    pass


class NonRelativePathError(Exception):
    pass


class HTTPRequirementError(HTTPClientError):
    title = explanation = 'Repository Requirement Missing'
    reason = None

    def __init__(self, message, *args, **kwargs):
        self.title = self.explanation = message
        super(HTTPRequirementError, self).__init__(*args, **kwargs)
        self.args = (message, )


class HTTPLockedRC(HTTPClientError):
    """
    Special Exception For locked Repos in RhodeCode, the return code can
    be overwritten by _code keyword argument passed into constructors
    """
    code = 423
    title = explanation = 'Repository Locked'
    reason = None

    def __init__(self, message, *args, **kwargs):
        from rhodecode import CONFIG
        from rhodecode.lib.utils2 import safe_int
        _code = CONFIG.get('lock_ret_code')
        self.code = safe_int(_code, self.code)
        self.title = self.explanation = message
        super(HTTPLockedRC, self).__init__(*args, **kwargs)
        self.args = (message, )


class IMCCommitError(Exception):
    pass


class UserCreationError(Exception):
    pass


class NotAllowedToCreateUserError(Exception):
    pass


class RepositoryCreationError(Exception):
    pass
