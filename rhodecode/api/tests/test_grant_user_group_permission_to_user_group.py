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

from rhodecode.model.user_group import UserGroupModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_ok, assert_error)


@pytest.mark.usefixtures("testuser_api", "app")
class TestGrantUserGroupPermissionFromUserGroup(object):
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
    def test_api_grant_user_group_permission_to_user_group(
            self, name, perm, user_util):
        group = user_util.create_user_group()
        target_group = user_util.create_user_group()

        id_, params = build_data(
            self.apikey,
            'grant_user_group_permission_to_user_group',
            usergroupid=target_group.users_group_name,
            sourceusergroupid=group.users_group_name,
            perm=perm)
        response = api_call(self.app, params)

        expected = {
            'msg': (
                'Granted perm: `%s` for user group: `%s`'
                ' in user group: `%s`' % (
                    perm, group.users_group_name,
                    target_group.users_group_name
                )
            ),
            'success': True
        }
        try:
            assert_ok(id_, expected, given=response.body)
        finally:
            UserGroupModel().revoke_user_group_permission(
                target_group.users_group_id, group.users_group_id)

    def test_api_grant_user_group_permission_to_user_group_same_failure(
            self, user_util):
        group = user_util.create_user_group()

        id_, params = build_data(
            self.apikey,
            'grant_user_group_permission_to_user_group',
            usergroupid=group.users_group_name,
            sourceusergroupid=group.users_group_name,
            perm='usergroup.none')
        response = api_call(self.app, params)

        expected = (
            'failed to edit permission for user group: `%s`'
            ' in user group: `%s`' % (
                group.users_group_name, group.users_group_name)
        )
        assert_error(id_, expected, given=response.body)
