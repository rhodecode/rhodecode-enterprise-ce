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

from rhodecode.model.meta import Session
from rhodecode.model.user import UserModel
from rhodecode.model.user_group import UserGroupModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok, crash, jsonify)
from rhodecode.tests.fixture import Fixture


@pytest.mark.usefixtures("testuser_api", "app")
class TestCreateUserGroup(object):
    fixture = Fixture()

    def test_api_create_user_group(self):
        group_name = 'some_new_group'
        id_, params = build_data(
            self.apikey, 'create_user_group', group_name=group_name)
        response = api_call(self.app, params)

        ret = {
            'msg': 'created new user group `%s`' % (group_name,),
            'user_group': jsonify(
                UserGroupModel()
                .get_by_name(group_name)
                .get_api_data()
            )
        }
        expected = ret
        assert_ok(id_, expected, given=response.body)
        self.fixture.destroy_user_group(group_name)

    def test_api_create_user_group_regular_user(self):
        group_name = 'some_new_group'

        usr = UserModel().get_by_username(self.TEST_USER_LOGIN)
        usr.inherit_default_permissions = False
        Session().add(usr)
        UserModel().grant_perm(
            self.TEST_USER_LOGIN, 'hg.usergroup.create.true')
        Session().commit()

        id_, params = build_data(
            self.apikey_regular, 'create_user_group', group_name=group_name)
        response = api_call(self.app, params)

        expected = {
            'msg': 'created new user group `%s`' % (group_name,),
            'user_group': jsonify(
                UserGroupModel()
                .get_by_name(group_name)
                .get_api_data()
            )
        }
        try:
            assert_ok(id_, expected, given=response.body)
        finally:
            self.fixture.destroy_user_group(group_name)
            UserModel().revoke_perm(
                self.TEST_USER_LOGIN, 'hg.usergroup.create.true')
            usr = UserModel().get_by_username(self.TEST_USER_LOGIN)
            usr.inherit_default_permissions = True
            Session().add(usr)
            Session().commit()

    def test_api_create_user_group_regular_user_no_permission(self):
        group_name = 'some_new_group'
        id_, params = build_data(
            self.apikey_regular, 'create_user_group', group_name=group_name)
        response = api_call(self.app, params)
        expected = "Access was denied to this resource."
        assert_error(id_, expected, given=response.body)

    def test_api_create_user_group_that_exist(self, user_util):
        group = user_util.create_user_group()
        group_name = group.users_group_name

        id_, params = build_data(
            self.apikey, 'create_user_group', group_name=group_name)
        response = api_call(self.app, params)

        expected = "user group `%s` already exist" % (group_name,)
        assert_error(id_, expected, given=response.body)

    @mock.patch.object(UserGroupModel, 'create', crash)
    def test_api_create_user_group_exception_occurred(self):
        group_name = 'exception_happens'
        id_, params = build_data(
            self.apikey, 'create_user_group', group_name=group_name)
        response = api_call(self.app, params)

        expected = 'failed to create group `%s`' % (group_name,)
        assert_error(id_, expected, given=response.body)
