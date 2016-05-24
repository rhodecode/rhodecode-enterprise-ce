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
class TestRemoveUserFromUserGroup(object):
    def test_api_remove_user_from_user_group(self, user_util):
        user, group = user_util.create_user_with_group()
        user_name = user.username
        group_name = group.users_group_name
        id_, params = build_data(
            self.apikey, 'remove_user_from_user_group',
            usergroupid=group_name,
            userid=user.username)
        response = api_call(self.app, params)

        expected = {
            'msg': 'removed member `%s` from user group `%s`' % (
                user_name, group_name
            ),
            'success': True}
        assert_ok(id_, expected, given=response.body)

    @mock.patch.object(UserGroupModel, 'remove_user_from_group', crash)
    def test_api_remove_user_from_user_group_exception_occurred(
            self, user_util):
        user, group = user_util.create_user_with_group()
        id_, params = build_data(
            self.apikey, 'remove_user_from_user_group',
            usergroupid=group.users_group_name, userid=user.username)
        response = api_call(self.app, params)
        expected = 'failed to remove member from user group `%s`' % (
            group.users_group_name)
        assert_error(id_, expected, given=response.body)
