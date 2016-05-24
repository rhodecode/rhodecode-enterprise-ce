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
from rhodecode.lib.middleware.disable_vcs import DisableVCSPagesWrapper


@pytest.mark.parametrize('url, expected_url', [
    ('/', '/'),
    ('/_admin/settings', '/_admin/settings'),
    ('/_admin/i_am_fine', '/_admin/i_am_fine'),
    ('/_admin/settings/mappings', '/error/vcs_unavailable'),
    ('/_admin/my_account/repos', '/error/vcs_unavailable'),
    ('/_admin/create_repository', '/error/vcs_unavailable'),
    ('/_admin/gists/1', '/error/vcs_unavailable'),
    ('/_admin/notifications/1', '/error/vcs_unavailable'),
])
def test_vcs_disabled(url, expected_url):
    app = DisableVCSPagesWrapper(app=SimpleApp())
    assert expected_url == app(get_environ(url), None)


def get_environ(url):
    """Construct a minimum WSGI environ based on the URL."""
    environ = {
        'PATH_INFO': url,
    }
    return environ


class SimpleApp(object):
    """
    A mock app to be used in the wrapper that returns the modified URL
    from the middleware
    """
    def __call__(self, environ, start_response):
        return environ['PATH_INFO']
