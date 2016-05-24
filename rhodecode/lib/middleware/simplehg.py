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
SimpleHG middleware for handling mercurial protocol request
(push/clone etc.). It's implemented with basic auth function
"""

import urlparse

from rhodecode.lib import utils
from rhodecode.lib.ext_json import json
from rhodecode.lib.middleware import simplevcs


class SimpleHg(simplevcs.SimpleVCS):

    SCM = 'hg'

    def _get_repository_name(self, environ):
        """
        Gets repository name out of PATH_INFO header

        :param environ: environ where PATH_INFO is stored
        """
        return environ['PATH_INFO'].strip('/')

    _ACTION_MAPPING = {
        'changegroup': 'pull',
        'changegroupsubset': 'pull',
        'getbundle': 'pull',
        'stream_out': 'pull',
        'listkeys': 'pull',
        'unbundle': 'push',
        'pushkey': 'push',
    }

    def _get_action(self, environ):
        """
        Maps mercurial request commands into a pull or push command.
        In case of unknown/unexpected data, it returns 'pull' to be safe.

        :param environ:
        """
        query = urlparse.parse_qs(environ['QUERY_STRING'],
                                  keep_blank_values=True)
        if 'cmd' in query:
            cmd = query['cmd'][0]
            return self._ACTION_MAPPING.get(cmd, 'pull')

        return 'pull'

    def _create_wsgi_app(self, repo_path, repo_name, config):
        return self.scm_app.create_hg_wsgi_app(repo_path, repo_name, config)

    def _create_config(self, extras, repo_name):
        config = utils.make_db_config(repo=repo_name)
        config.set('rhodecode', 'RC_SCM_DATA', json.dumps(extras))

        return config.serialize()
