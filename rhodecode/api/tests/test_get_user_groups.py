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


import json

import pytest

from rhodecode.model.user import UserModel
from rhodecode.api.tests.utils import build_data, api_call


@pytest.mark.usefixtures("testuser_api", "app")
class TestGetUserGroups(object):
    @pytest.mark.parametrize("apikey_attr, expect_secrets", [
        ('apikey', True),
        ('apikey_regular', False),
    ])
    def test_api_get_user_groups(self, apikey_attr, expect_secrets, user_util):
        first_group = user_util.create_user_group()
        second_group = user_util.create_user_group()
        expected = [
            g.get_api_data(include_secrets=expect_secrets)
            for g in (first_group, second_group)]

        apikey = getattr(self, apikey_attr)
        id_, params = build_data(apikey, 'get_user_groups', )
        response = api_call(self.app, params)
        self._assert_ok(id_, expected, response)

    def test_api_get_user_groups_regular_user(self, user_util):
        first_group = user_util.create_user_group()
        second_group = user_util.create_user_group()
        expected = [g.get_api_data() for g in (first_group, second_group)]

        id_, params = build_data(self.apikey_regular, 'get_user_groups', )
        response = api_call(self.app, params)
        self._assert_ok(id_, expected, response)

    def test_api_get_user_groups_regular_user_no_permission(self, user_util):
        group = user_util.create_user_group()
        user = UserModel().get_by_username(self.TEST_USER_LOGIN)
        user_util.grant_user_permission_to_user_group(
            group, user, 'usergroup.none')
        id_, params = build_data(self.apikey_regular, 'get_user_groups', )
        response = api_call(self.app, params)
        expected = []
        self._assert_ok(id_, expected, response)

    def _assert_ok(self, id_, expected_list, response):
        result = json.loads(response.body)
        assert result['id'] == id_
        assert result['error'] is None
        assert sorted(result['result']) == sorted(expected_list)
