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
Internal settings for vcs-lib
"""

# list of default encoding used in safe_unicode/safe_str methods
DEFAULT_ENCODINGS = ['utf8']

# Optional arguments to rev-filter, it has to be a list
# It can also be ['--branches', '--tags']
GIT_REV_FILTER = ['--all']

# Compatibility version when creating SVN repositories. None means newest.
# Other available options are: pre-1.4-compatible, pre-1.5-compatible,
# pre-1.6-compatible, pre-1.8-compatible
SVN_COMPATIBLE_VERSION = None

ALIASES = ['hg', 'git', 'svn']

BACKENDS = {
    'hg': 'rhodecode.lib.vcs.backends.hg.MercurialRepository',
    'git': 'rhodecode.lib.vcs.backends.git.GitRepository',
    'svn': 'rhodecode.lib.vcs.backends.svn.SubversionRepository',
}

# TODO: Remove once controllers/files.py is adjusted
ARCHIVE_SPECS = {
    'tbz2': ('application/x-bzip2', '.tar.bz2'),
    'tgz': ('application/x-gzip', '.tar.gz'),
    'zip': ('application/zip', '.zip'),
}

PYRO_PORT = 9900

PYRO_GIT = 'git_remote'
PYRO_HG = 'hg_remote'
PYRO_SVN = 'svn_remote'
PYRO_VCSSERVER = 'vcs_server'
PYRO_GIT_REMOTE_WSGI = 'git_remote_wsgi'
PYRO_HG_REMOTE_WSGI = 'hg_remote_wsgi'

PYRO_RECONNECT_TRIES = 15
"""
How many retries to reconnect will be performed if the connection was lost.

Each try takes 2s. Doing 15 means that we will give it up to 30s for a
connection to be re-established.
"""


def pyro_remote(object_id, server_and_port):
    return "PYRO:%s@%s" % (object_id, server_and_port)


def available_aliases():
    """
    Mercurial is required for the system to work, so in case vcs.backends does
    not include it, we make sure it will be available internally
    TODO: anderson: refactor vcs.backends so it won't be necessary, VCS server
    should be responsible to dictate available backends.
    """
    aliases = ALIASES[:]
    if 'hg' not in aliases:
        aliases += ['hg']
    return aliases
