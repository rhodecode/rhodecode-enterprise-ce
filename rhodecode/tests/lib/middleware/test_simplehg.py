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

import urlparse

import mock
import pytest
import simplejson as json

from rhodecode.lib.vcs.backends.base import Config
from rhodecode.tests.lib.middleware import mock_scm_app
import rhodecode.lib.middleware.simplehg as simplehg


def get_environ(url):
    """Construct a minimum WSGI environ based on the URL."""
    parsed_url = urlparse.urlparse(url)
    environ = {
        'PATH_INFO': parsed_url.path,
        'QUERY_STRING': parsed_url.query,
    }

    return environ


@pytest.mark.parametrize(
    'url, expected_action',
    [
        ('/foo/bar?cmd=unbundle&key=tip', 'push'),
        ('/foo/bar?cmd=pushkey&key=tip', 'push'),
        ('/foo/bar?cmd=listkeys&key=tip', 'pull'),
        ('/foo/bar?cmd=changegroup&key=tip', 'pull'),
        # Edge case: unknown argument: assume pull
        ('/foo/bar?cmd=unknown&key=tip', 'pull'),
        ('/foo/bar?cmd=&key=tip', 'pull'),
        # Edge case: not cmd argument
        ('/foo/bar?key=tip', 'pull'),
    ])
def test_get_action(url, expected_action):
    app = simplehg.SimpleHg(application=None,
                            config={'auth_ret_code': '', 'base_path': ''})
    assert expected_action == app._get_action(get_environ(url))


@pytest.mark.parametrize(
    'url, expected_repo_name',
    [
        ('/foo?cmd=unbundle&key=tip', 'foo'),
        ('/foo/bar?cmd=pushkey&key=tip', 'foo/bar'),
        ('/foo/bar/baz?cmd=listkeys&key=tip', 'foo/bar/baz'),
        # Repos with trailing slashes.
        ('/foo/?cmd=unbundle&key=tip', 'foo'),
        ('/foo/bar/?cmd=pushkey&key=tip', 'foo/bar'),
        ('/foo/bar/baz/?cmd=listkeys&key=tip', 'foo/bar/baz'),
    ])
def test_get_repository_name(url, expected_repo_name):
    app = simplehg.SimpleHg(application=None,
                            config={'auth_ret_code': '', 'base_path': ''})
    assert expected_repo_name == app._get_repository_name(get_environ(url))


def test_get_config():
    app = simplehg.SimpleHg(application=None,
                            config={'auth_ret_code': '', 'base_path': ''})
    extras = {'foo': 'FOO', 'bar': 'BAR'}

    mock_config = Config()
    mock_config.set('a1', 'b1', 'c1')
    mock_config.set('a2', 'b2', 'c2')
    # We mock the call to make_db_config, otherwise we need to wait for the
    # pylonsaspp
    with mock.patch('rhodecode.lib.utils.make_db_config',
                    return_value=mock_config) as make_db_config_mock:
        hg_config = app._create_config(extras, repo_name='test-repo')

    make_db_config_mock.assert_called_once_with(repo='test-repo')
    assert isinstance(hg_config, list)

    # Remove the entries from the mock_config so to get only the extras
    hg_config.remove(('a1', 'b1', 'c1'))
    hg_config.remove(('a2', 'b2', 'c2'))

    assert hg_config[0][:2] == ('rhodecode', 'RC_SCM_DATA')
    assert json.loads(hg_config[0][-1]) == extras


def test_create_wsgi_app_uses_scm_app_from_simplevcs():
    config = {
        'auth_ret_code': '',
        'base_path': '',
        'vcs.scm_app_implementation':
            'rhodecode.tests.lib.middleware.mock_scm_app',
    }
    app = simplehg.SimpleHg(application=None, config=config)
    wsgi_app = app._create_wsgi_app('/tmp/test', 'test_repo', {})
    assert wsgi_app is mock_scm_app.mock_hg_wsgi
