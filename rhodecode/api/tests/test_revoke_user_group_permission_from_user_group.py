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
from rhodecode.api.tests.utils import build_data, api_call, assert_ok


@pytest.mark.usefixtures("testuser_api", "app")
class TestRevokeUserGroupPermissionFromUserGroup(object):
    @pytest.mark.parametrize("name", [
        ('none',),
        ('all',),
        ('repos',),
        ('groups',),
    ])
    def test_api_revoke_user_group_permission_from_user_group(
            self, name, user_util):
        user = UserModel().get_by_username(self.TEST_USER_LOGIN)
        group = user_util.create_user_group()
        source_group = user_util.create_user_group()

        user_util.grant_user_permission_to_user_group(
            group, user, 'usergroup.read')
        user_util.grant_user_group_permission_to_user_group(
            source_group, group, 'usergroup.read')

        id_, params = build_data(
            self.apikey, 'revoke_user_group_permission_from_user_group',
            usergroupid=group.users_group_name,
            sourceusergroupid=source_group.users_group_name)
        response = api_call(self.app, params)

        expected = {
            'msg': 'Revoked perm for user group: `%s` in user group: `%s`' % (
                source_group.users_group_name, group.users_group_name
            ),
            'success': True
        }
        assert_ok(id_, expected, given=response.body)
