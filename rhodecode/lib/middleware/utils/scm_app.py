# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016  RhodeCode GmbH
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
Equivalent of rhodecode.lib.middleware.scm_app but using remote apps.
"""

import logging

from rhodecode.lib.middleware.utils import wsgi_app_caller_client


log = logging.getLogger(__name__)


HG_REMOTE_WSGI = None
GIT_REMOTE_WSGI = None


def create_git_wsgi_app(repo_path, repo_name, config):
    """
    Return a WSGI app backed by a remote app to handle Git.

    config is a dictionary holding the extras.
    """
    factory = GIT_REMOTE_WSGI
    if not factory:
        log.error('Pyro server has not been initialized yet')

    return wsgi_app_caller_client.RemoteAppCaller(
        factory, repo_path, repo_name, config)


def create_hg_wsgi_app(repo_path, repo_name, config):
    """
    Return a WSGI app backed by a remote app to handle Mercurial.

    config is a list of 3-item tuples representing a ConfigObject (it is the
    serialized version of the config object).
    """
    factory = HG_REMOTE_WSGI
    if not factory:
        log.error('Pyro server has not been initialized yet')

    return wsgi_app_caller_client.RemoteAppCaller(
        factory, repo_path, repo_name, config)
