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

from rhodecode.model.db import User
from rhodecode.model.user import UserModel
from rhodecode.tests import TEST_USER_ADMIN_LOGIN
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_ok, assert_error, crash, jsonify)


@pytest.mark.usefixtures("testuser_api", "app")
class TestUpdateUser(object):
    @pytest.mark.parametrize("name, expected", [
        ('firstname', 'new_username'),
        ('lastname', 'new_username'),
        ('email', 'new_username'),
        ('admin', True),
        ('admin', False),
        ('extern_type', 'ldap'),
        ('extern_type', None),
        ('extern_name', 'test'),
        ('extern_name', None),
        ('active', False),
        ('active', True),
        ('password', 'newpass')
    ])
    def test_api_update_user(self, name, expected, user_util):
        usr = user_util.create_user()

        kw = {name: expected, 'userid': usr.user_id}
        id_, params = build_data(self.apikey, 'update_user', **kw)
        response = api_call(self.app, params)

        ret = {
            'msg': 'updated user ID:%s %s' % (usr.user_id, usr.username),
            'user': jsonify(
                UserModel()
                .get_by_username(usr.username)
                .get_api_data(include_secrets=True)
            )
        }

        expected = ret
        assert_ok(id_, expected, given=response.body)

    def test_api_update_user_no_changed_params(self):
        usr = UserModel().get_by_username(TEST_USER_ADMIN_LOGIN)
        ret = jsonify(usr.get_api_data(include_secrets=True))
        id_, params = build_data(
            self.apikey, 'update_user', userid=TEST_USER_ADMIN_LOGIN)

        response = api_call(self.app, params)
        ret = {
            'msg': 'updated user ID:%s %s' % (
                usr.user_id, TEST_USER_ADMIN_LOGIN),
            'user': ret
        }
        expected = ret
        assert_ok(id_, expected, given=response.body)

    def test_api_update_user_by_user_id(self):
        usr = UserModel().get_by_username(TEST_USER_ADMIN_LOGIN)
        ret = jsonify(usr.get_api_data(include_secrets=True))
        id_, params = build_data(
            self.apikey, 'update_user', userid=usr.user_id)

        response = api_call(self.app, params)
        ret = {
            'msg': 'updated user ID:%s %s' % (
                usr.user_id, TEST_USER_ADMIN_LOGIN),
            'user': ret
        }
        expected = ret
        assert_ok(id_, expected, given=response.body)

    def test_api_update_user_default_user(self):
        usr = User.get_default_user()
        id_, params = build_data(
            self.apikey, 'update_user', userid=usr.user_id)

        response = api_call(self.app, params)
        expected = 'editing default user is forbidden'
        assert_error(id_, expected, given=response.body)

    @mock.patch.object(UserModel, 'update_user', crash)
    def test_api_update_user_when_exception_happens(self):
        usr = UserModel().get_by_username(TEST_USER_ADMIN_LOGIN)
        ret = jsonify(usr.get_api_data(include_secrets=True))
        id_, params = build_data(
            self.apikey, 'update_user', userid=usr.user_id)

        response = api_call(self.app, params)
        ret = 'failed to update user `%s`' % (usr.user_id,)

        expected = ret
        assert_error(id_, expected, given=response.body)
