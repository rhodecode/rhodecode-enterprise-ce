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

from urlparse import urljoin

import requests

import rhodecode
from rhodecode.lib.middleware import simplevcs
from rhodecode.lib.utils import is_valid_repo


class SimpleSvnApp(object):
    IGNORED_HEADERS = [
        'connection', 'keep-alive', 'content-encoding',
        'transfer-encoding']

    def __init__(self, config):
        self.config = config

    def __call__(self, environ, start_response):
        request_headers = self._get_request_headers(environ)

        data = environ['wsgi.input']
        # johbo: On Gunicorn, we end up with a 415 response if we pass data
        # to requests. I think the request is usually without payload, still
        # reading the data to be on the safe side.
        if environ['REQUEST_METHOD'] == 'MKCOL':
            data = data.read()

        response = requests.request(
            environ['REQUEST_METHOD'], self._get_url(environ['PATH_INFO']),
            data=data, headers=request_headers)

        response_headers = self._get_response_headers(response.headers)
        start_response(
            '{} {}'.format(response.status_code, response.reason),
            response_headers)
        return response.iter_content(chunk_size=1024)

    def _get_url(self, path):
        return urljoin(
            self.config.get('subversion_http_server_url', ''), path)

    def _get_request_headers(self, environ):
        headers = {}

        for key in environ:
            if not key.startswith('HTTP_'):
                continue
            new_key = key.split('_')
            new_key = [k.capitalize() for k in new_key[1:]]
            new_key = '-'.join(new_key)
            headers[new_key] = environ[key]

        if 'CONTENT_TYPE' in environ:
            headers['Content-Type'] = environ['CONTENT_TYPE']

        if 'CONTENT_LENGTH' in environ:
            headers['Content-Length'] = environ['CONTENT_LENGTH']

        return headers

    def _get_response_headers(self, headers):
        return [
            (h, headers[h])
            for h in headers
            if h.lower() not in self.IGNORED_HEADERS
        ]


class SimpleSvn(simplevcs.SimpleVCS):

    SCM = 'svn'
    READ_ONLY_COMMANDS = ('OPTIONS', 'PROPFIND', 'GET', 'REPORT')

    def _get_repository_name(self, environ):
        """
        Gets repository name out of PATH_INFO header

        :param environ: environ where PATH_INFO is stored
        """
        path = environ['PATH_INFO'].split('!')
        repo_name = path[0].strip('/')

        # SVN includes the whole path in it's requests, including
        # subdirectories inside the repo. Therefore we have to search for
        # the repo root directory.
        if not is_valid_repo(repo_name, self.basepath, self.SCM):
            current_path = ''
            for component in repo_name.split('/'):
                current_path += component
                if is_valid_repo(current_path, self.basepath, self.SCM):
                    return current_path
                current_path += '/'

        return repo_name

    def _get_action(self, environ):
        return (
            'pull'
            if environ['REQUEST_METHOD'] in self.READ_ONLY_COMMANDS
            else 'push')

    def _create_wsgi_app(self, repo_path, repo_name, config):
        return SimpleSvnApp(config)

    def _create_config(self, extras, repo_name):
        server_url = rhodecode.CONFIG.get(
            'rhodecode_subversion_http_server_url', '')
        extras['subversion_http_server_url'] = (
            server_url or 'http://localhost/')
        return extras
