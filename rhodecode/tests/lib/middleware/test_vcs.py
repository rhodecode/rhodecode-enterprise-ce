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

from mock import patch, Mock

import rhodecode
from rhodecode.lib.middleware import vcs


def test_is_hg():
    environ = {
        'PATH_INFO': '/rhodecode-dev',
        'QUERY_STRING': 'cmd=changegroup',
        'HTTP_ACCEPT': 'application/mercurial'
    }
    assert vcs.is_hg(environ)


def test_is_hg_no_cmd():
    environ = {
        'PATH_INFO': '/rhodecode-dev',
        'QUERY_STRING': '',
        'HTTP_ACCEPT': 'application/mercurial'
    }
    assert not vcs.is_hg(environ)


def test_is_hg_empty_cmd():
    environ = {
        'PATH_INFO': '/rhodecode-dev',
        'QUERY_STRING': 'cmd=',
        'HTTP_ACCEPT': 'application/mercurial'
    }
    assert not vcs.is_hg(environ)


def test_is_svn_returns_true_if_subversion_is_in_a_dav_header():
    environ = {
        'PATH_INFO': '/rhodecode-dev',
        'HTTP_DAV': 'http://subversion.tigris.org/xmlns/dav/svn/log-revprops'
    }
    assert vcs.is_svn(environ) is True


def test_is_svn_returns_false_if_subversion_is_not_in_a_dav_header():
    environ = {
        'PATH_INFO': '/rhodecode-dev',
        'HTTP_DAV': 'http://stuff.tigris.org/xmlns/dav/svn/log-revprops'
    }
    assert vcs.is_svn(environ) is False


def test_is_svn_returns_false_if_no_dav_header():
    environ = {
        'PATH_INFO': '/rhodecode-dev',
    }
    assert vcs.is_svn(environ) is False


def test_is_svn_returns_true_if_magic_path_segment():
    environ = {
        'PATH_INFO': '/stub-repository/!svn/rev/4',
    }
    assert vcs.is_svn(environ)


def test_is_svn_allows_to_configure_the_magic_path(monkeypatch):
    """
    This is intended as a fallback in case someone has configured his
    Subversion server with a different magic path segment.
    """
    monkeypatch.setitem(
        rhodecode.CONFIG, 'rhodecode_subversion_magic_path', '/!my-magic')
    environ = {
        'PATH_INFO': '/stub-repository/!my-magic/rev/4',
    }
    assert vcs.is_svn(environ)


class TestVCSMiddleware(object):
    def test_get_handler_app_retuns_svn_app_when_proxy_enabled(self):
        environ = {
            'PATH_INFO': 'rhodecode-dev',
            'HTTP_DAV': 'http://subversion.tigris.org/xmlns/dav/svn/log'
        }
        app = Mock()
        config = Mock()
        middleware = vcs.VCSMiddleware(
            app, config=config, appenlight_client=None)
        snv_patch = patch('rhodecode.lib.middleware.vcs.SimpleSvn')
        settings_patch = patch.dict(
            rhodecode.CONFIG,
            {'rhodecode_proxy_subversion_http_requests': True})
        with snv_patch as svn_mock, settings_patch:
            svn_mock.return_value = None
            middleware._get_handler_app(environ)

        svn_mock.assert_called_once_with(app, config)

    def test_get_handler_app_retuns_no_svn_app_when_proxy_disabled(self):
        environ = {
            'PATH_INFO': 'rhodecode-dev',
            'HTTP_DAV': 'http://subversion.tigris.org/xmlns/dav/svn/log'
        }
        app = Mock()
        config = Mock()
        middleware = vcs.VCSMiddleware(
            app, config=config, appenlight_client=None)
        snv_patch = patch('rhodecode.lib.middleware.vcs.SimpleSvn')
        settings_patch = patch.dict(
            rhodecode.CONFIG,
            {'rhodecode_proxy_subversion_http_requests': False})
        with snv_patch as svn_mock, settings_patch:
            app = middleware._get_handler_app(environ)

        assert svn_mock.call_count == 0
        assert app is None
