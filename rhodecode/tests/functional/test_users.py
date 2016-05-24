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

from rhodecode.model.meta import Session
from rhodecode.model.db import User
from rhodecode.tests import (
    TestController, url, TEST_USER_ADMIN_LOGIN, TEST_USER_ADMIN_PASS,
    TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
from rhodecode.tests.fixture import Fixture
from rhodecode.tests.utils import AssertResponse

fixture = Fixture()


class TestUsersController(TestController):
    test_user_1 = 'testme'
    destroy_users = set()

    @classmethod
    def teardown_class(cls):
        fixture.destroy_users(cls.destroy_users)

    def test_user_profile(self):
        edit_link_css = '.user-profile .panel-edit'
        self.log_user(TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        user = fixture.create_user(
            self.test_user_1, password='qweqwe', email='testme@rhodecode.org')
        Session().commit()
        self.destroy_users.add(self.test_user_1)

        response = self.app.get(url('user_profile', username=user.username))
        response.mustcontain('testme')
        response.mustcontain('testme@rhodecode.org')
        assert_response = AssertResponse(response)
        assert_response.no_element_exists(edit_link_css)

        # edit should be available to superadmin users
        self.logout_user()
        self.log_user(TEST_USER_ADMIN_LOGIN, TEST_USER_ADMIN_PASS)
        response = self.app.get(url('user_profile', username=user.username))
        assert_response = AssertResponse(response)
        assert_response.element_contains(edit_link_css, 'Edit')

    def test_user_profile_not_available(self):
        user = fixture.create_user(
            self.test_user_1, password='qweqwe', email='testme@rhodecode.org')
        Session().commit()
        self.destroy_users.add(self.test_user_1)

        self.app.get(url('user_profile', username=user.username), status=302)

        self.log_user()
        # default user
        self.app.get(
            url('user_profile', username=User.DEFAULT_USER), status=404)
        # actual 404
        self.app.get(url('user_profile', username='unknown'), status=404)
