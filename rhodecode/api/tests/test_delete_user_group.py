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
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok, crash)


@pytest.mark.usefixtures("testuser_api", "app")
class TestDeleteUserGroup(object):
    def test_api_delete_user_group(self, user_util):
        user_group = user_util.create_user_group(auto_cleanup=False)
        group_name = user_group.users_group_name
        group_id = user_group.users_group_id
        id_, params = build_data(
            self.apikey, 'delete_user_group', usergroupid=group_name)
        response = api_call(self.app, params)

        expected = {
            'user_group': None,
            'msg': 'deleted user group ID:%s %s' % (group_id, group_name)
        }
        assert_ok(id_, expected, given=response.body)

    def test_api_delete_user_group_regular_user(self, user_util):
        ugroup = user_util.create_user_group(auto_cleanup=False)
        group_name = ugroup.users_group_name
        group_id = ugroup.users_group_id
        user = UserModel().get_by_username(self.TEST_USER_LOGIN)

        user_util.grant_user_permission_to_user_group(
            ugroup, user, 'usergroup.admin')

        id_, params = build_data(
            self.apikey_regular, 'delete_user_group', usergroupid=group_name)
        response = api_call(self.app, params)

        expected = {
            'user_group': None,
            'msg': 'deleted user group ID:%s %s' % (group_id, group_name)
        }
        assert_ok(id_, expected, given=response.body)

    def test_api_delete_user_group_regular_user_no_permission(self, user_util):
        user_group = user_util.create_user_group()
        group_name = user_group.users_group_name

        id_, params = build_data(
            self.apikey_regular, 'delete_user_group', usergroupid=group_name)
        response = api_call(self.app, params)

        expected = 'user group `%s` does not exist' % (group_name)
        assert_error(id_, expected, given=response.body)

    def test_api_delete_user_group_that_is_assigned(self, backend, user_util):
        ugroup = user_util.create_user_group()
        group_name = ugroup.users_group_name
        repo = backend.create_repo()

        ugr_to_perm = user_util.grant_user_group_permission_to_repo(
            repo, ugroup, 'repository.write')
        msg = 'UserGroup assigned to %s' % (ugr_to_perm.repository)

        id_, params = build_data(
            self.apikey, 'delete_user_group',
            usergroupid=group_name)
        response = api_call(self.app, params)

        expected = msg
        assert_error(id_, expected, given=response.body)

    def test_api_delete_user_group_exception_occurred(self, user_util):
        ugroup = user_util.create_user_group()
        group_name = ugroup.users_group_name
        group_id = ugroup.users_group_id
        id_, params = build_data(
            self.apikey, 'delete_user_group',
            usergroupid=group_name)

        with mock.patch.object(UserGroupModel, 'delete', crash):
            response = api_call(self.app, params)
            expected = 'failed to delete user group ID:%s %s' % (
                group_id, group_name)
            assert_error(id_, expected, given=response.body)
