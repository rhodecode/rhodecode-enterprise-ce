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


import pytest

from rhodecode.authentication.tests.conftest import (
    EnabledAuthPlugin, DisabledAuthPlugin)
from rhodecode.config.routing import ADMIN_PREFIX


@pytest.mark.usefixtures('autologin_user', 'app')
class TestAuthenticationSettings:

    def test_auth_settings_global_view_get(self, app):
        url = '{prefix}/auth/'.format(prefix=ADMIN_PREFIX)
        response = app.get(url)
        assert response.status_code == 200

    def test_plugin_settings_view_get(self, app, auth_plugin):
        url = '{prefix}/auth/{name}'.format(
            prefix=ADMIN_PREFIX,
            name=auth_plugin.name)
        with EnabledAuthPlugin(auth_plugin):
            response = app.get(url)
            assert response.status_code == 200

    def test_plugin_settings_view_get_404(self, app, auth_plugin):
        url = '{prefix}/auth/{name}'.format(
            prefix=ADMIN_PREFIX,
            name=auth_plugin.name)
        with DisabledAuthPlugin(auth_plugin):
            response = app.get(url, status=404)
            assert response.status_code == 404
