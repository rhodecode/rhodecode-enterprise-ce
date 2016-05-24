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

import mock
import pytest

from rhodecode.tests import TEST_USER_ADMIN_LOGIN, url
from rhodecode.tests.utils import AssertResponse


class TestSessionBehaviorOnPasswordChange(object):
    @pytest.fixture(autouse=True)
    def patch_password_changed(self, request):
        password_changed_patcher = mock.patch(
            'rhodecode.lib.base.password_changed')
        self.password_changed_mock = password_changed_patcher.start()
        self.password_changed_mock.return_value = False

        @request.addfinalizer
        def cleanup():
            password_changed_patcher.stop()

    def test_sessions_are_ok_when_password_is_not_changed(
            self, app, autologin_user):
        response = app.get(url('home'))
        assert_response = AssertResponse(response)
        assert_response.element_contains(
            '#quick_login_link .menu_link_user', TEST_USER_ADMIN_LOGIN)
        assert 'rhodecode_user' in response.session
        assert response.session.was_invalidated is False

    def test_sessions_invalidated_when_password_is_changed(
            self, app, autologin_user):
        self.password_changed_mock.return_value = True
        response = app.get(url('home'))
        assert_response = AssertResponse(response)
        assert_response.element_contains('#quick_login_link .user', 'Sign in')
        assert 'rhodecode_user' not in response.session
        assert response.session.was_invalidated is True
