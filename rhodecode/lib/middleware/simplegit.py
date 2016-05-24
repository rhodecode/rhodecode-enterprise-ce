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
SimpleGit middleware for handling git protocol request (push/clone etc.)
It's implemented with basic auth function
"""
import re
import urlparse

import rhodecode
from rhodecode.lib import utils2
from rhodecode.lib.middleware import simplevcs


GIT_PROTO_PAT = re.compile(
    r'^/(.+)/(info/refs|git-upload-pack|git-receive-pack)')


class SimpleGit(simplevcs.SimpleVCS):

    SCM = 'git'

    def _get_repository_name(self, environ):
        """
        Gets repository name out of PATH_INFO header

        :param environ: environ where PATH_INFO is stored
        """
        repo_name = GIT_PROTO_PAT.match(environ['PATH_INFO']).group(1)
        return repo_name

    _ACTION_MAPPING = {
        'git-receive-pack': 'push',
        'git-upload-pack': 'pull',
    }

    def _get_action(self, environ):
        """
        Maps git request commands into a pull or push command.
        In case of unknown/unexpected data, it returns 'pull' to be safe.

        :param environ:
        """
        path = environ['PATH_INFO']

        if path.endswith('/info/refs'):
            query = urlparse.parse_qs(environ['QUERY_STRING'])
            service_cmd = query.get('service', [''])[0]
            return self._ACTION_MAPPING.get(service_cmd, 'pull')
        elif path.endswith('/git-receive-pack'):
            return 'push'
        elif path.endswith('/git-upload-pack'):
            return 'pull'

        return 'pull'

    def _create_wsgi_app(self, repo_path, repo_name, config):
        return self.scm_app.create_git_wsgi_app(repo_path, repo_name, config)

    def _create_config(self, extras, repo_name):
        extras['git_update_server_info'] = utils2.str2bool(
            rhodecode.CONFIG.get('git_update_server_info'))
        return extras
