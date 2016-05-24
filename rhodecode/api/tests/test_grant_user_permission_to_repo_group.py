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
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok, crash)


@pytest.mark.usefixtures("testuser_api", "app")
class TestGrantUserPermissionFromRepoGroup(object):
    @pytest.mark.parametrize("name, perm, apply_to_children", [
        ('none', 'group.none', 'none'),
        ('read', 'group.read', 'none'),
        ('write', 'group.write', 'none'),
        ('admin', 'group.admin', 'none'),

        ('none', 'group.none', 'all'),
        ('read', 'group.read', 'all'),
        ('write', 'group.write', 'all'),
        ('admin', 'group.admin', 'all'),

        ('none', 'group.none', 'repos'),
        ('read', 'group.read', 'repos'),
        ('write', 'group.write', 'repos'),
        ('admin', 'group.admin', 'repos'),

        ('none', 'group.none', 'groups'),
        ('read', 'group.read', 'groups'),
        ('write', 'group.write', 'groups'),
        ('admin', 'group.admin', 'groups'),
    ])
    def test_api_grant_user_permission_to_repo_group(
            self, name, perm, apply_to_children, user_util):
        user = user_util.create_user()
        repo_group = user_util.create_repo_group()
        id_, params = build_data(
            self.apikey, 'grant_user_permission_to_repo_group',
            repogroupid=repo_group.name, userid=user.username,
            perm=perm, apply_to_children=apply_to_children)
        response = api_call(self.app, params)

        ret = {
            'msg': (
                'Granted perm: `%s` (recursive:%s) for user: `%s`'
                ' in repo group: `%s`' % (
                    perm, apply_to_children, user.username, repo_group.name
                )
            ),
            'success': True
        }
        expected = ret
        assert_ok(id_, expected, given=response.body)

    @pytest.mark.parametrize(
        "name, perm, apply_to_children, grant_admin, access_ok", [
            ('none_fails', 'group.none', 'none', False, False),
            ('read_fails', 'group.read', 'none', False, False),
            ('write_fails', 'group.write', 'none', False, False),
            ('admin_fails', 'group.admin', 'none', False, False),

            # with granted perms
            ('none_ok', 'group.none', 'none', True, True),
            ('read_ok', 'group.read', 'none', True, True),
            ('write_ok', 'group.write', 'none', True, True),
            ('admin_ok', 'group.admin', 'none', True, True),
        ]
    )
    def test_api_grant_user_permission_to_repo_group_by_regular_user(
            self, name, perm, apply_to_children, grant_admin, access_ok,
            user_util):
        user = user_util.create_user()
        repo_group = user_util.create_repo_group()

        if grant_admin:
            test_user = UserModel().get_by_username(self.TEST_USER_LOGIN)
            user_util.grant_user_permission_to_repo_group(
                repo_group, test_user, 'group.admin')

        id_, params = build_data(
            self.apikey_regular, 'grant_user_permission_to_repo_group',
            repogroupid=repo_group.name, userid=user.username,
            perm=perm, apply_to_children=apply_to_children)
        response = api_call(self.app, params)
        if access_ok:
            ret = {
                'msg': (
                    'Granted perm: `%s` (recursive:%s) for user: `%s`'
                    ' in repo group: `%s`' % (
                        perm, apply_to_children, user.username, repo_group.name
                    )
                ),
                'success': True
            }
            expected = ret
            assert_ok(id_, expected, given=response.body)
        else:
            expected = 'repository group `%s` does not exist' % (
                repo_group.name, )
            assert_error(id_, expected, given=response.body)

    def test_api_grant_user_permission_to_repo_group_wrong_permission(
            self, user_util):
        user = user_util.create_user()
        repo_group = user_util.create_repo_group()
        perm = 'haha.no.permission'
        id_, params = build_data(
            self.apikey,
            'grant_user_permission_to_repo_group',
            repogroupid=repo_group.name,
            userid=user.username,
            perm=perm)
        response = api_call(self.app, params)

        expected = 'permission `%s` does not exist' % (perm,)
        assert_error(id_, expected, given=response.body)

    @mock.patch.object(RepoGroupModel, 'grant_user_permission', crash)
    def test_api_grant_user_permission_to_repo_group_exception_when_adding(
            self, user_util):
        user = user_util.create_user()
        repo_group = user_util.create_repo_group()
        perm = 'group.read'
        id_, params = build_data(
            self.apikey,
            'grant_user_permission_to_repo_group',
            repogroupid=repo_group.name,
            userid=user.username,
            perm=perm)
        response = api_call(self.app, params)

        expected = (
            'failed to edit permission for user: `%s` in repo group: `%s`' % (
                user.username, repo_group.name
            )
        )
        assert_error(id_, expected, given=response.body)
