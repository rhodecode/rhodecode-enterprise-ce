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

from rhodecode.lib.auth import check_password
from rhodecode.model.user import UserModel
from rhodecode.tests import (
    TEST_USER_ADMIN_LOGIN, TEST_USER_REGULAR_EMAIL)
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_ok, assert_error, jsonify, crash)
from rhodecode.tests.fixture import Fixture


# TODO: mikhail: remove fixture from here
fixture = Fixture()


@pytest.mark.usefixtures("testuser_api", "app")
class TestCreateUser(object):
    def test_api_create_existing_user(self):
        id_, params = build_data(
            self.apikey, 'create_user',
            username=TEST_USER_ADMIN_LOGIN,
            email='test@foo.com',
            password='trololo')
        response = api_call(self.app, params)

        expected = "user `%s` already exist" % (TEST_USER_ADMIN_LOGIN,)
        assert_error(id_, expected, given=response.body)

    def test_api_create_user_with_existing_email(self):
        id_, params = build_data(
            self.apikey, 'create_user',
            username=TEST_USER_ADMIN_LOGIN + 'new',
            email=TEST_USER_REGULAR_EMAIL,
            password='trololo')
        response = api_call(self.app, params)

        expected = "email `%s` already exist" % (TEST_USER_REGULAR_EMAIL,)
        assert_error(id_, expected, given=response.body)

    def test_api_create_user(self):
        username = 'test_new_api_user'
        email = username + "@foo.com"

        id_, params = build_data(
            self.apikey, 'create_user',
            username=username,
            email=email,
            password='example')
        response = api_call(self.app, params)

        usr = UserModel().get_by_username(username)
        ret = {
            'msg': 'created new user `%s`' % (username,),
            'user': jsonify(usr.get_api_data(include_secrets=True)),
        }
        try:
            expected = ret
            assert check_password('example', usr.password)
            assert_ok(id_, expected, given=response.body)
        finally:
            fixture.destroy_user(usr.user_id)

    def test_api_create_user_without_password(self):
        username = 'test_new_api_user_passwordless'
        email = username + "@foo.com"

        id_, params = build_data(
            self.apikey, 'create_user',
            username=username,
            email=email)
        response = api_call(self.app, params)

        usr = UserModel().get_by_username(username)
        ret = {
            'msg': 'created new user `%s`' % (username,),
            'user': jsonify(usr.get_api_data(include_secrets=True)),
        }
        try:
            expected = ret
            assert_ok(id_, expected, given=response.body)
        finally:
            fixture.destroy_user(usr.user_id)

    def test_api_create_user_with_extern_name(self):
        username = 'test_new_api_user_passwordless'
        email = username + "@foo.com"

        id_, params = build_data(
            self.apikey, 'create_user',
            username=username,
            email=email, extern_name='rhodecode')
        response = api_call(self.app, params)

        usr = UserModel().get_by_username(username)
        ret = {
            'msg': 'created new user `%s`' % (username,),
            'user': jsonify(usr.get_api_data(include_secrets=True)),
        }
        try:
            expected = ret
            assert_ok(id_, expected, given=response.body)
        finally:
            fixture.destroy_user(usr.user_id)

    def test_api_create_user_with_password_change(self):
        username = 'test_new_api_user_password_change'
        email = username + "@foo.com"

        id_, params = build_data(
            self.apikey, 'create_user',
            username=username,
            email=email, extern_name='rhodecode',
            force_password_change=True)
        response = api_call(self.app, params)

        usr = UserModel().get_by_username(username)
        ret = {
            'msg': 'created new user `%s`' % (username,),
            'user': jsonify(usr.get_api_data(include_secrets=True)),
        }
        try:
            expected = ret
            assert_ok(id_, expected, given=response.body)
        finally:
            fixture.destroy_user(usr.user_id)

    @mock.patch.object(UserModel, 'create_or_update', crash)
    def test_api_create_user_when_exception_happened(self):

        username = 'test_new_api_user'
        email = username + "@foo.com"

        id_, params = build_data(
            self.apikey, 'create_user',
            username=username,
            email=email,
            password='trololo')
        response = api_call(self.app, params)
        expected = 'failed to create user `%s`' % (username,)
        assert_error(id_, expected, given=response.body)
