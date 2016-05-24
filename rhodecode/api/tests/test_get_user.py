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

from rhodecode.lib.auth import AuthUser
from rhodecode.model.user import UserModel
from rhodecode.tests import TEST_USER_ADMIN_LOGIN
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_ok, assert_error)


@pytest.mark.usefixtures("testuser_api", "app")
class TestGetUser(object):
    def test_api_get_user(self):
        id_, params = build_data(
            self.apikey, 'get_user', userid=TEST_USER_ADMIN_LOGIN)
        response = api_call(self.app, params)

        usr = UserModel().get_by_username(TEST_USER_ADMIN_LOGIN)
        ret = usr.get_api_data(include_secrets=True)
        ret['permissions'] = AuthUser(usr.user_id).permissions

        expected = ret
        assert_ok(id_, expected, given=response.body)

    def test_api_get_user_not_existing(self):
        id_, params = build_data(self.apikey, 'get_user', userid='trololo')
        response = api_call(self.app, params)

        expected = "user `%s` does not exist" % 'trololo'
        assert_error(id_, expected, given=response.body)

    def test_api_get_user_without_giving_userid(self):
        id_, params = build_data(self.apikey, 'get_user')
        response = api_call(self.app, params)

        usr = UserModel().get_by_username(TEST_USER_ADMIN_LOGIN)
        ret = usr.get_api_data(include_secrets=True)
        ret['permissions'] = AuthUser(usr.user_id).permissions

        expected = ret
        assert_ok(id_, expected, given=response.body)

    def test_api_get_user_without_giving_userid_non_admin(self):
        id_, params = build_data(self.apikey_regular, 'get_user')
        response = api_call(self.app, params)

        usr = UserModel().get_by_username(self.TEST_USER_LOGIN)
        ret = usr.get_api_data(include_secrets=True)
        ret['permissions'] = AuthUser(usr.user_id).permissions

        expected = ret
        assert_ok(id_, expected, given=response.body)

    def test_api_get_user_with_giving_userid_non_admin(self):
        id_, params = build_data(
            self.apikey_regular, 'get_user',
            userid=self.TEST_USER_LOGIN)
        response = api_call(self.app, params)

        expected = 'userid is not the same as your user'
        assert_error(id_, expected, given=response.body)
