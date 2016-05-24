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

from StringIO import StringIO

import pytest
from mock import patch, Mock

import rhodecode
from rhodecode.lib.middleware.simplesvn import SimpleSvn, SimpleSvnApp


class TestSimpleSvn(object):
    @pytest.fixture(autouse=True)
    def simple_svn(self, pylonsapp):
        self.app = SimpleSvn(
            application='None',
            config={'auth_ret_code': '',
                    'base_path': rhodecode.CONFIG['base_path']})

    def test_get_config(self):
        extras = {'foo': 'FOO', 'bar': 'BAR'}
        config = self.app._create_config(extras, repo_name='test-repo')
        assert config == extras

    @pytest.mark.parametrize(
        'method', ['OPTIONS', 'PROPFIND', 'GET', 'REPORT'])
    def test_get_action_returns_pull(self, method):
        environment = {'REQUEST_METHOD': method}
        action = self.app._get_action(environment)
        assert action == 'pull'

    @pytest.mark.parametrize(
        'method', [
            'MKACTIVITY', 'PROPPATCH', 'PUT', 'CHECKOUT', 'MKCOL', 'MOVE',
            'COPY', 'DELETE', 'LOCK', 'UNLOCK', 'MERGE'
        ])
    def test_get_action_returns_push(self, method):
        environment = {'REQUEST_METHOD': method}
        action = self.app._get_action(environment)
        assert action == 'push'

    @pytest.mark.parametrize(
        'path, expected_name', [
            ('/hello-svn', 'hello-svn'),
            ('/hello-svn/', 'hello-svn'),
            ('/group/hello-svn/', 'group/hello-svn'),
            ('/group/hello-svn/!svn/vcc/default', 'group/hello-svn'),
        ])
    def test_get_repository_name(self, path, expected_name):
        environment = {'PATH_INFO': path}
        name = self.app._get_repository_name(environment)
        assert name == expected_name

    def test_get_repository_name_subfolder(self, backend_svn):
        repo = backend_svn.repo
        environment = {
            'PATH_INFO': '/{}/path/with/subfolders'.format(repo.repo_name)}
        name = self.app._get_repository_name(environment)
        assert name == repo.repo_name

    def test_create_wsgi_app(self):
        with patch('rhodecode.lib.middleware.simplesvn.SimpleSvnApp') as (
                wsgi_app_mock):
            config = Mock()
            wsgi_app = self.app._create_wsgi_app(
                repo_path='', repo_name='', config=config)

        wsgi_app_mock.assert_called_once_with(config)
        assert wsgi_app == wsgi_app_mock()


class TestSimpleSvnApp(object):
    data = '<xml></xml>'
    path = '/group/my-repo'
    wsgi_input = StringIO(data)
    environment = {
        'HTTP_DAV': (
            'http://subversion.tigris.org/xmlns/dav/svn/depth,'
            ' http://subversion.tigris.org/xmlns/dav/svn/mergeinfo'),
        'HTTP_USER_AGENT': 'SVN/1.8.11 (x86_64-linux) serf/1.3.8',
        'REQUEST_METHOD': 'OPTIONS',
        'PATH_INFO': path,
        'wsgi.input': wsgi_input,
        'CONTENT_TYPE': 'text/xml',
        'CONTENT_LENGTH': '130'
    }

    def setup_method(self, method):
        self.host = 'http://localhost/'
        self.app = SimpleSvnApp(
            config={'subversion_http_server_url': self.host})

    def test_get_request_headers_with_content_type(self):
        expected_headers = {
            'Dav': self.environment['HTTP_DAV'],
            'User-Agent': self.environment['HTTP_USER_AGENT'],
            'Content-Type': self.environment['CONTENT_TYPE'],
            'Content-Length': self.environment['CONTENT_LENGTH']
        }
        headers = self.app._get_request_headers(self.environment)
        assert headers == expected_headers

    def test_get_request_headers_without_content_type(self):
        environment = self.environment.copy()
        environment.pop('CONTENT_TYPE')
        expected_headers = {
            'Dav': environment['HTTP_DAV'],
            'Content-Length': self.environment['CONTENT_LENGTH'],
            'User-Agent': environment['HTTP_USER_AGENT'],
        }
        request_headers = self.app._get_request_headers(environment)
        assert request_headers == expected_headers

    def test_get_response_headers(self):
        headers = {
            'Connection': 'keep-alive',
            'Keep-Alive': 'timeout=5, max=100',
            'Transfer-Encoding': 'chunked',
            'Content-Encoding': 'gzip',
            'MS-Author-Via': 'DAV',
            'SVN-Supported-Posts': 'create-txn-with-props'
        }
        expected_headers = [
            ('MS-Author-Via', 'DAV'),
            ('SVN-Supported-Posts', 'create-txn-with-props')
        ]
        response_headers = self.app._get_response_headers(headers)
        assert sorted(response_headers) == sorted(expected_headers)

    def test_get_url(self):
        url = self.app._get_url(self.path)
        expected_url = '{}{}'.format(self.host.strip('/'), self.path)
        assert url == expected_url

    def test_call(self):
        start_response = Mock()
        response_mock = Mock()
        response_mock.headers = {
            'Content-Encoding': 'gzip',
            'MS-Author-Via': 'DAV',
            'SVN-Supported-Posts': 'create-txn-with-props'
        }
        response_mock.status_code = 200
        response_mock.reason = 'OK'
        with patch('rhodecode.lib.middleware.simplesvn.requests.request') as (
                request_mock):
            request_mock.return_value = response_mock
            self.app(self.environment, start_response)

        expected_url = '{}{}'.format(self.host.strip('/'), self.path)
        expected_request_headers = {
            'Dav': self.environment['HTTP_DAV'],
            'User-Agent': self.environment['HTTP_USER_AGENT'],
            'Content-Type': self.environment['CONTENT_TYPE'],
            'Content-Length': self.environment['CONTENT_LENGTH']
        }
        expected_response_headers = [
            ('SVN-Supported-Posts', 'create-txn-with-props'),
            ('MS-Author-Via', 'DAV')
        ]
        request_mock.assert_called_once_with(
            self.environment['REQUEST_METHOD'], expected_url,
            data=self.wsgi_input, headers=expected_request_headers)
        response_mock.iter_content.assert_called_once_with(chunk_size=1024)
        args, _ = start_response.call_args
        assert args[0] == '200 OK'
        assert sorted(args[1]) == sorted(expected_response_headers)
