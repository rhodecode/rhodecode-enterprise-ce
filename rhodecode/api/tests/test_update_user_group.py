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

from rhodecode.model.user import UserModel
from rhodecode.model.user_group import UserGroupModel
from rhodecode.tests import TEST_USER_REGULAR_LOGIN
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok, crash, jsonify)


@pytest.mark.usefixtures("testuser_api", "app")
class TestUpdateUserGroup(object):
    @pytest.mark.parametrize("changing_attr, updates", [
        ('group_name', {'group_name': 'new_group_name'}),
        ('group_name', {'group_name': 'test_group_for_update'}),
        ('owner', {'owner': TEST_USER_REGULAR_LOGIN}),
        ('active', {'active': False}),
        ('active', {'active': True})
    ])
    def test_api_update_user_group(self, changing_attr, updates, user_util):
        user_group = user_util.create_user_group()
        group_name = user_group.users_group_name
        expected_api_data = user_group.get_api_data()
        expected_api_data.update(updates)

        id_, params = build_data(
            self.apikey, 'update_user_group', usergroupid=group_name,
            **updates)
        response = api_call(self.app, params)

        expected = {
            'msg': 'updated user group ID:%s %s' % (
                user_group.users_group_id, user_group.users_group_name),
            'user_group': jsonify(expected_api_data)
        }
        assert_ok(id_, expected, given=response.body)

    @pytest.mark.parametrize("changing_attr, updates", [
        # TODO: mikhail: decide if we need to test against the commented params
        # ('group_name', {'group_name': 'new_group_name'}),
        # ('group_name', {'group_name': 'test_group_for_update'}),
        ('owner', {'owner': TEST_USER_REGULAR_LOGIN}),
        ('active', {'active': False}),
        ('active', {'active': True})
    ])
    def test_api_update_user_group_regular_user(
            self, changing_attr, updates, user_util):
        user_group = user_util.create_user_group()
        group_name = user_group.users_group_name
        expected_api_data = user_group.get_api_data()
        expected_api_data.update(updates)


        # grant permission to this user
        user = UserModel().get_by_username(self.TEST_USER_LOGIN)

        user_util.grant_user_permission_to_user_group(
            user_group, user, 'usergroup.admin')
        id_, params = build_data(
            self.apikey_regular, 'update_user_group',
            usergroupid=group_name, **updates)
        response = api_call(self.app, params)
        expected = {
            'msg': 'updated user group ID:%s %s' % (
                user_group.users_group_id, user_group.users_group_name),
            'user_group': jsonify(expected_api_data)
        }
        assert_ok(id_, expected, given=response.body)

    def test_api_update_user_group_regular_user_no_permission(self, user_util):
        user_group = user_util.create_user_group()
        group_name = user_group.users_group_name
        id_, params = build_data(
            self.apikey_regular, 'update_user_group', usergroupid=group_name)
        response = api_call(self.app, params)

        expected = 'user group `%s` does not exist' % (group_name)
        assert_error(id_, expected, given=response.body)

    @mock.patch.object(UserGroupModel, 'update', crash)
    def test_api_update_user_group_exception_occurred(self, user_util):
        user_group = user_util.create_user_group()
        group_name = user_group.users_group_name
        id_, params = build_data(
            self.apikey, 'update_user_group', usergroupid=group_name)
        response = api_call(self.app, params)
        expected = 'failed to update user group `%s`' % (group_name,)
        assert_error(id_, expected, given=response.body)
