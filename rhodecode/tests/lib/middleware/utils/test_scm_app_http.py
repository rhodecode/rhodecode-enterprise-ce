# -*- coding: utf-8 -*-

# Copyright (C) 2016-2016  RhodeCode GmbH
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

import mock
import Pyro4
import pytest
import webtest

from rhodecode.lib.middleware.utils import scm_app_http, scm_app
from rhodecode.lib.vcs.conf import settings


def vcs_http_app(vcsserver_http_echo_app):
    """
    VcsHttpProxy wrapped in WebTest.
    """
    git_url = vcsserver_http_echo_app.http_url + 'stream/git/'
    vcs_http_proxy = scm_app_http.VcsHttpProxy(
        git_url, 'stub_path', 'stub_name', None)
    app = webtest.TestApp(vcs_http_proxy)
    return app


@pytest.fixture(scope='module')
def vcsserver_http_echo_app(request, vcsserver_factory):
    """
    A running VCSServer with the EchoApp activated via HTTP.
    """
    vcsserver = vcsserver_factory(
        request=request,
        use_http=True,
        overrides=[{'app:main': {'dev.use_echo_app': 'true'}}])
    return vcsserver


@pytest.fixture(scope='session')
def data():
    one_kb = "x" * 1024
    return one_kb * 1024 * 10


def test_reuse_app_no_data(repeat, vcsserver_http_echo_app):
    app = vcs_http_app(vcsserver_http_echo_app)
    for x in xrange(repeat / 10):
        response = app.post('/')
        assert response.status_code == 200


def test_reuse_app_with_data(data, repeat, vcsserver_http_echo_app):
    app = vcs_http_app(vcsserver_http_echo_app)
    for x in xrange(repeat / 10):
        response = app.post('/', params=data)
        assert response.status_code == 200


def test_create_app_per_request_no_data(repeat, vcsserver_http_echo_app):
    for x in xrange(repeat / 10):
        app = vcs_http_app(vcsserver_http_echo_app)
        response = app.post('/')
        assert response.status_code == 200


def test_create_app_per_request_with_data(
        data, repeat, vcsserver_http_echo_app):
    for x in xrange(repeat / 10):
        app = vcs_http_app(vcsserver_http_echo_app)
        response = app.post('/', params=data)
        assert response.status_code == 200


@pytest.fixture(scope='module')
def vcsserver_pyro_echo_app(request, vcsserver_factory):
    """
    A running VCSServer with the EchoApp activated via Pyro4.
    """
    vcsserver = vcsserver_factory(
        request=request,
        use_http=False,
        overrides=[{'DEFAULT': {'dev.use_echo_app': 'true'}}])
    return vcsserver


def vcs_pyro4_app(vcsserver_pyro_echo_app):
    """
    Pyro4 based Vcs proxy wrapped in WebTest
    """
    stub_config = {
        'git_update_server_info': 'stub',
    }
    server_and_port = vcsserver_pyro_echo_app.server_and_port
    GIT_REMOTE_WSGI = Pyro4.Proxy(
        settings.pyro_remote(
            settings.PYRO_GIT_REMOTE_WSGI, server_and_port))
    with mock.patch('rhodecode.lib.middleware.utils.scm_app.GIT_REMOTE_WSGI',
                    GIT_REMOTE_WSGI):
        pyro4_app = scm_app.create_git_wsgi_app(
            'stub_path', 'stub_name', stub_config)
    app = webtest.TestApp(pyro4_app)
    return app


def test_pyro4_no_data(repeat, pylonsapp, vcsserver_pyro_echo_app):
    for x in xrange(repeat / 10):
        app = vcs_pyro4_app(vcsserver_pyro_echo_app)
        response = app.post('/')
        assert response.status_code == 200


def test_pyro4_with_data(repeat, pylonsapp, vcsserver_pyro_echo_app, data):
    for x in xrange(repeat / 10):
        app = vcs_pyro4_app(vcsserver_pyro_echo_app)
        response = app.post('/', params=data)
        assert response.status_code == 200
