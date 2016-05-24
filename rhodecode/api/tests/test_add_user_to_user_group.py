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
class TestAddUserToUserGroup(object):
    def test_api_add_user_to_user_group(self, user_util):
        group = user_util.create_user_group()
        user = user_util.create_user()
        group_name = group.users_group_name
        user_name = user.username
        id_, params = build_data(
            self.apikey, 'add_user_to_user_group',
            usergroupid=group_name, userid=user_name)
        response = api_call(self.app, params)
        expected = {
            'msg': 'added member `%s` to user group `%s`' % (
                user_name, group_name
            ),
            'success': True
        }
        assert_ok(id_, expected, given=response.body)

    def test_api_add_user_to_user_group_that_doesnt_exist(self, user_util):
        user = user_util.create_user()
        user_name = user.username
        id_, params = build_data(
            self.apikey, 'add_user_to_user_group',
            usergroupid='false-group',
            userid=user_name)
        response = api_call(self.app, params)

        expected = 'user group `%s` does not exist' % 'false-group'
        assert_error(id_, expected, given=response.body)

    @mock.patch.object(UserGroupModel, 'add_user_to_group', crash)
    def test_api_add_user_to_user_group_exception_occurred(self, user_util):
        group = user_util.create_user_group()
        user = user_util.create_user()
        group_name = group.users_group_name
        user_name = user.username
        id_, params = build_data(
            self.apikey, 'add_user_to_user_group',
            usergroupid=group_name, userid=user_name)
        response = api_call(self.app, params)

        expected = 'failed to add member to user group `%s`' % (group_name,)
        assert_error(id_, expected, given=response.body)
