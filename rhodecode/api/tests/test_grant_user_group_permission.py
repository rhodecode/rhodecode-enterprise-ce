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

from rhodecode.model.repo import RepoModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok, crash)


@pytest.mark.usefixtures("testuser_api", "app")
class TestGrantUserGroupPermission(object):
    @pytest.mark.parametrize("name, perm", [
        ('none', 'repository.none'),
        ('read', 'repository.read'),
        ('write', 'repository.write'),
        ('admin', 'repository.admin')
    ])
    def test_api_grant_user_group_permission(
            self, name, perm, backend, user_util):
        user_group = user_util.create_user_group()
        id_, params = build_data(
            self.apikey,
            'grant_user_group_permission',
            repoid=backend.repo_name,
            usergroupid=user_group.users_group_name,
            perm=perm)
        response = api_call(self.app, params)

        ret = {
            'msg': 'Granted perm: `%s` for user group: `%s` in repo: `%s`' % (
                perm, user_group.users_group_name, backend.repo_name
            ),
            'success': True
        }
        expected = ret
        assert_ok(id_, expected, given=response.body)

    def test_api_grant_user_group_permission_wrong_permission(
            self, backend, user_util):
        perm = 'haha.no.permission'
        user_group = user_util.create_user_group()
        id_, params = build_data(
            self.apikey,
            'grant_user_group_permission',
            repoid=backend.repo_name,
            usergroupid=user_group.users_group_name,
            perm=perm)
        response = api_call(self.app, params)

        expected = 'permission `%s` does not exist' % (perm,)
        assert_error(id_, expected, given=response.body)

    @mock.patch.object(RepoModel, 'grant_user_group_permission', crash)
    def test_api_grant_user_group_permission_exception_when_adding(
            self, backend, user_util):
        perm = 'repository.read'
        user_group = user_util.create_user_group()
        id_, params = build_data(
            self.apikey,
            'grant_user_group_permission',
            repoid=backend.repo_name,
            usergroupid=user_group.users_group_name,
            perm=perm)
        response = api_call(self.app, params)

        expected = (
            'failed to edit permission for user group: `%s` in repo: `%s`' % (
                user_group.users_group_name, backend.repo_name
            )
        )
        assert_error(id_, expected, given=response.body)
