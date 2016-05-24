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

from rhodecode.model.user_group import UserGroupModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok, crash)


@pytest.mark.usefixtures("testuser_api", "app")
class TestRevokeUserPermissionFromUserGroup(object):
    @pytest.mark.parametrize("name", [
        ('none',),
        ('all',),
        ('repos',),
        ('groups',),
    ])
    def test_api_revoke_user_permission_from_user_group(self, name, user_util):
        user = user_util.create_user()
        group = user_util.create_user_group()
        user_util.grant_user_permission_to_user_group(
            group, user, 'usergroup.admin')

        id_, params = build_data(
            self.apikey,
            'revoke_user_permission_from_user_group',
            usergroupid=group.users_group_name,
            userid=user.username)
        response = api_call(self.app, params)

        expected = {
            'msg': 'Revoked perm for user: `%s` in user group: `%s`' % (
                user.username, group.users_group_name
            ),
            'success': True
        }
        assert_ok(id_, expected, given=response.body)

    @pytest.mark.parametrize("name, grant_admin, access_ok", [
        ('none', False, False),
        ('all', False, False),
        ('repos', False, False),
        ('groups', False, False),

        # after granting admin rights
        ('none', False, False),
        ('all', False, False),
        ('repos', False, False),
        ('groups', False, False),
    ])
    def test_api_revoke_user_permission_from_user_group_by_regular_user(
            self, name, grant_admin, access_ok, user_util):
        user = user_util.create_user()
        group = user_util.create_user_group()
        permission = 'usergroup.admin' if grant_admin else 'usergroup.read'
        user_util.grant_user_permission_to_user_group(group, user, permission)

        id_, params = build_data(
            self.apikey_regular,
            'revoke_user_permission_from_user_group',
            usergroupid=group.users_group_name,
            userid=user.username)
        response = api_call(self.app, params)
        if access_ok:
            expected = {
                'msg': 'Revoked perm for user: `%s` in user group: `%s`' % (
                    user.username, group.users_group_name
                ),
                'success': True
            }
            assert_ok(id_, expected, given=response.body)
        else:
            expected = 'user group `%s` does not exist' % (
                group.users_group_name)
            assert_error(id_, expected, given=response.body)

    @mock.patch.object(UserGroupModel, 'revoke_user_permission', crash)
    def test_api_revoke_user_permission_from_user_group_exception_when_adding(
            self, user_util):
        user = user_util.create_user()
        group = user_util.create_user_group()
        id_, params = build_data(
            self.apikey,
            'revoke_user_permission_from_user_group',
            usergroupid=group.users_group_name,
            userid=user.username)
        response = api_call(self.app, params)

        expected = (
            'failed to edit permission for user: `%s` in user group: `%s`' % (
                user.username, group.users_group_name)
        )
        assert_error(id_, expected, given=response.body)
