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

from rhodecode.model.user import UserModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_ok, assert_error, expected_permissions)


@pytest.mark.usefixtures("testuser_api", "app")
class TestGetUserGroups(object):
    def test_api_get_user_group(self, user_util):
        user, group = user_util.create_user_with_group()
        id_, params = build_data(
            self.apikey, 'get_user_group', usergroupid=group.users_group_name)
        response = api_call(self.app, params)

        ret = group.get_api_data()
        ret['users'] = [user.get_api_data()]

        permissions = expected_permissions(group)

        ret['members'] = permissions
        expected = ret
        assert_ok(id_, expected, given=response.body)

    def test_api_get_user_group_regular_user(self, user_util):
        user, group = user_util.create_user_with_group()
        id_, params = build_data(
            self.apikey_regular, 'get_user_group',
            usergroupid=group.users_group_name)
        response = api_call(self.app, params)

        ret = group.get_api_data()
        ret['users'] = [user.get_api_data()]

        permissions = expected_permissions(group)

        ret['members'] = permissions
        expected = ret
        assert_ok(id_, expected, given=response.body)

    def test_api_get_user_group_regular_user_permission_denied(
            self, user_util):
        group = user_util.create_user_group()
        user = UserModel().get_by_username(self.TEST_USER_LOGIN)
        group_name = group.users_group_name
        user_util.grant_user_permission_to_user_group(
            group, user, 'usergroup.none')

        id_, params = build_data(
            self.apikey_regular, 'get_user_group', usergroupid=group_name)
        response = api_call(self.app, params)

        expected = 'user group `%s` does not exist' % (group_name,)
        assert_error(id_, expected, given=response.body)
