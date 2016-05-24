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

import pytest
import urlparse

from rhodecode.tests.lib.middleware import mock_scm_app
import rhodecode.lib.middleware.simplegit as simplegit


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
        ('/foo/bar/info/refs?service=git-upload-pack', 'pull'),
        ('/foo/bar/info/refs?service=git-receive-pack', 'push'),
        ('/foo/bar/git-upload-pack', 'pull'),
        ('/foo/bar/git-receive-pack', 'push'),
        # Edge case: missing data for info/refs
        ('/foo/info/refs?service=', 'pull'),
        ('/foo/info/refs', 'pull'),
        # Edge case: git command comes with service argument
        ('/foo/git-upload-pack?service=git-receive-pack', 'pull'),
        ('/foo/git-receive-pack?service=git-upload-pack', 'push'),
        # Edge case: repo name conflicts with git commands
        ('/git-receive-pack/git-upload-pack', 'pull'),
        ('/git-receive-pack/git-receive-pack', 'push'),
        ('/git-upload-pack/git-upload-pack', 'pull'),
        ('/git-upload-pack/git-receive-pack', 'push'),
        ('/foo/git-receive-pack', 'push'),
        # Edge case: not a smart protocol url
        ('/foo/bar', 'pull'),
    ])
def test_get_action(url, expected_action):
    app = simplegit.SimpleGit(application=None,
                              config={'auth_ret_code': '', 'base_path': ''})
    assert expected_action == app._get_action(get_environ(url))


@pytest.mark.parametrize(
    'url, expected_repo_name',
    [
        ('/foo/info/refs?service=git-upload-pack', 'foo'),
        ('/foo/bar/info/refs?service=git-receive-pack', 'foo/bar'),
        ('/foo/git-upload-pack', 'foo'),
        ('/foo/git-receive-pack', 'foo'),
        ('/foo/bar/git-upload-pack', 'foo/bar'),
        ('/foo/bar/git-receive-pack', 'foo/bar'),
    ])
def test_get_repository_name(url, expected_repo_name):
    app = simplegit.SimpleGit(application=None,
                              config={'auth_ret_code': '', 'base_path': ''})
    assert expected_repo_name == app._get_repository_name(get_environ(url))


def test_get_config():
    app = simplegit.SimpleGit(application=None,
                              config={'auth_ret_code': '', 'base_path': ''})
    extras = {'foo': 'FOO', 'bar': 'BAR'}

    # We copy the extras as the method below will change the contents.
    config = app._create_config(dict(extras), repo_name='test-repo')
    expected_config = dict(extras)
    expected_config.update({
        'git_update_server_info': False,
    })

    assert config == expected_config


def test_create_wsgi_app_uses_scm_app_from_simplevcs():
    config = {
        'auth_ret_code': '',
        'base_path': '',
        'vcs.scm_app_implementation':
            'rhodecode.tests.lib.middleware.mock_scm_app',
    }
    app = simplegit.SimpleGit(application=None, config=config)
    wsgi_app = app._create_wsgi_app('/tmp/test', 'test_repo', {})
    assert wsgi_app is mock_scm_app.mock_git_wsgi
