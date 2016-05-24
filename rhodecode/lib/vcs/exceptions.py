# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016  RhodeCode GmbH
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
Custom vcs exceptions module.
"""

import functools
import urllib2


class VCSError(Exception):
    pass


class RepositoryError(VCSError):
    pass


class RepositoryRequirementError(RepositoryError):
    pass


class VCSBackendNotSupportedError(VCSError):
    """
    Exception raised when VCSServer does not support requested backend
    """


class EmptyRepositoryError(RepositoryError):
    pass


class TagAlreadyExistError(RepositoryError):
    pass


class TagDoesNotExistError(RepositoryError):
    pass


class BranchAlreadyExistError(RepositoryError):
    pass


class BranchDoesNotExistError(RepositoryError):
    pass


class CommitError(RepositoryError):
    """
    Exceptions related to an existing commit
    """


class CommitDoesNotExistError(CommitError):
    pass


class CommittingError(RepositoryError):
    """
    Exceptions happening while creating a new commit
    """


class NothingChangedError(CommittingError):
    pass


class NodeError(VCSError):
    pass


class RemovedFileNodeError(NodeError):
    pass


class NodeAlreadyExistsError(CommittingError):
    pass


class NodeAlreadyChangedError(CommittingError):
    pass


class NodeDoesNotExistError(CommittingError):
    pass


class NodeNotChangedError(CommittingError):
    pass


class NodeAlreadyAddedError(CommittingError):
    pass


class NodeAlreadyRemovedError(CommittingError):
    pass


class ImproperArchiveTypeError(VCSError):
    pass


class CommandError(VCSError):
    pass


class UnhandledException(VCSError):
    """
    Signals that something unexpected went wrong.

    This usually means we have a programming error on the side of the VCSServer
    and should inspect the logfile of the VCSServer to find more details.
    """


_EXCEPTION_MAP = {
    'abort': RepositoryError,
    'archive': ImproperArchiveTypeError,
    'error': RepositoryError,
    'lookup': CommitDoesNotExistError,
    'repo_locked': RepositoryError,
    'requirement': RepositoryRequirementError,
    'unhandled': UnhandledException,
    # TODO: johbo: Define our own exception for this and stop abusing
    # urllib's exception class.
    'url_error': urllib2.URLError,
}


def map_vcs_exceptions(func):
    """
    Utility to decorate functions so that plain exceptions are translated.

    The translation is based on `exc_map` which maps a `str` indicating
    the error type into an exception class representing this error inside
    of the vcs layer.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:

            # The error middleware adds information if it finds
            # __traceback_info__ in a frame object. This way the remote
            # traceback information is made available in error reports.
            remote_tb = getattr(e, '_pyroTraceback', None)
            if remote_tb:
                __traceback_info__ = (
                    'Found Pyro4 remote traceback information:\n\n' +
                    '\n'.join(remote_tb))

                # Avoid that remote_tb also appears in the frame
                del remote_tb

            # Special vcs errors had an attribute "_vcs_kind" which is used
            # to translate them to the proper exception class in the vcs
            # client layer.
            kind = getattr(e, '_vcs_kind', None)
            if kind:
                raise _EXCEPTION_MAP[kind](*e.args)
            else:
                raise

    return wrapper
