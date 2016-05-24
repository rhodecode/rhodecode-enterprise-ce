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
class TestGrantUserPermissionFromUserGroup(object):
    @pytest.mark.parametrize("name, perm", [
        ('none', 'usergroup.none'),
        ('read', 'usergroup.read'),
        ('write', 'usergroup.write'),
        ('admin', 'usergroup.admin'),

        ('none', 'usergroup.none'),
        ('read', 'usergroup.read'),
        ('write', 'usergroup.write'),
        ('admin', 'usergroup.admin'),

        ('none', 'usergroup.none'),
        ('read', 'usergroup.read'),
        ('write', 'usergroup.write'),
        ('admin', 'usergroup.admin'),

        ('none', 'usergroup.none'),
        ('read', 'usergroup.read'),
        ('write', 'usergroup.write'),
        ('admin', 'usergroup.admin'),
    ])
    def test_api_grant_user_permission_to_user_group(
            self, name, perm, user_util):
        user = user_util.create_user()
        group = user_util.create_user_group()
        id_, params = build_data(
            self.apikey,
            'grant_user_permission_to_user_group',
            usergroupid=group.users_group_name,
            userid=user.username,
            perm=perm)
        response = api_call(self.app, params)

        ret = {
            'msg': 'Granted perm: `%s` for user: `%s` in user group: `%s`' % (
                perm, user.username, group.users_group_name
            ),
            'success': True
        }
        expected = ret
        assert_ok(id_, expected, given=response.body)

    @pytest.mark.parametrize("name, perm, grant_admin, access_ok", [
        ('none_fails', 'usergroup.none', False, False),
        ('read_fails', 'usergroup.read', False, False),
        ('write_fails', 'usergroup.write', False, False),
        ('admin_fails', 'usergroup.admin', False, False),

        # with granted perms
        ('none_ok', 'usergroup.none', True, True),
        ('read_ok', 'usergroup.read', True, True),
        ('write_ok', 'usergroup.write', True, True),
        ('admin_ok', 'usergroup.admin', True, True),
    ])
    def test_api_grant_user_permission_to_user_group_by_regular_user(
            self, name, perm, grant_admin, access_ok, user_util):
        api_user = UserModel().get_by_username(self.TEST_USER_LOGIN)
        user = user_util.create_user()
        group = user_util.create_user_group()
        # grant the user ability to at least read the group
        permission = 'usergroup.admin' if grant_admin else 'usergroup.read'
        user_util.grant_user_permission_to_user_group(
            group, api_user, permission)

        id_, params = build_data(
            self.apikey_regular,
            'grant_user_permission_to_user_group',
            usergroupid=group.users_group_name,
            userid=user.username,
            perm=perm)
        response = api_call(self.app, params)

        if access_ok:
            ret = {
                'msg': (
                    'Granted perm: `%s` for user: `%s` in user group: `%s`' % (
                        perm, user.username, group.users_group_name
                    )
                ),
                'success': True
            }
            expected = ret
            assert_ok(id_, expected, given=response.body)
        else:
            expected = 'user group `%s` does not exist' % (
                group.users_group_name)
            assert_error(id_, expected, given=response.body)

    def test_api_grant_user_permission_to_user_group_wrong_permission(
            self, user_util):
        user = user_util.create_user()
        group = user_util.create_user_group()
        perm = 'haha.no.permission'
        id_, params = build_data(
            self.apikey,
            'grant_user_permission_to_user_group',
            usergroupid=group.users_group_name,
            userid=user.username,
            perm=perm)
        response = api_call(self.app, params)

        expected = 'permission `%s` does not exist' % perm
        assert_error(id_, expected, given=response.body)

    def test_api_grant_user_permission_to_user_group_exception_when_adding(
            self, user_util):
        user = user_util.create_user()
        group = user_util.create_user_group()

        perm = 'usergroup.read'
        id_, params = build_data(
            self.apikey,
            'grant_user_permission_to_user_group',
            usergroupid=group.users_group_name,
            userid=user.username,
            perm=perm)
        with mock.patch.object(UserGroupModel, 'grant_user_permission', crash):
            response = api_call(self.app, params)

        expected = (
            'failed to edit permission for user: `%s` in user group: `%s`' % (
                user.username, group.users_group_name
            )
        )
        assert_error(id_, expected, given=response.body)
