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
GIT module
"""

import logging

from rhodecode.lib.vcs import connection
from rhodecode.lib.vcs.backends.git.repository import GitRepository
from rhodecode.lib.vcs.backends.git.commit import GitCommit
from rhodecode.lib.vcs.backends.git.inmemory import GitInMemoryCommit


log = logging.getLogger(__name__)


def discover_git_version():
    """
    Returns the string as it was returned by running 'git --version'

    It will return an empty string in case the connection is not initialized
    or no vcsserver is available.
    """
    try:
        return connection.Git.discover_git_version()
    except Exception:
        log.warning("Failed to discover the Git version", exc_info=True)
        return ''
