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

from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok, crash)


@pytest.mark.usefixtures("testuser_api", "app")
class TestRevokeUserPermissionFromRepoGroup(object):
    @pytest.mark.parametrize("name, apply_to_children", [
        ('none', 'none'),
        ('all', 'all'),
        ('repos', 'repos'),
        ('groups', 'groups'),
    ])
    def test_api_revoke_user_permission_from_repo_group(
            self, name, apply_to_children, user_util):
        user = user_util.create_user()
        repo_group = user_util.create_repo_group()
        user_util.grant_user_permission_to_repo_group(
            repo_group, user, 'group.read')

        id_, params = build_data(
            self.apikey,
            'revoke_user_permission_from_repo_group',
            repogroupid=repo_group.name,
            userid=user.username,
            apply_to_children=apply_to_children,)
        response = api_call(self.app, params)

        expected = {
            'msg': (
                'Revoked perm (recursive:%s) for user: `%s`'
                ' in repo group: `%s`' % (
                    apply_to_children, user.username, repo_group.name
                )
            ),
            'success': True
        }
        assert_ok(id_, expected, given=response.body)

    @pytest.mark.parametrize(
        "name, apply_to_children, grant_admin, access_ok", [
            ('none', 'none', False, False),
            ('all', 'all', False, False),
            ('repos', 'repos', False, False),
            ('groups', 'groups', False, False),

            # after granting admin rights
            ('none', 'none', False, False),
            ('all', 'all', False, False),
            ('repos', 'repos', False, False),
            ('groups', 'groups', False, False),
        ]
    )
    def test_api_revoke_user_permission_from_repo_group_by_regular_user(
            self, name, apply_to_children, grant_admin, access_ok, user_util):
        user = user_util.create_user()
        repo_group = user_util.create_repo_group()
        permission = 'group.admin' if grant_admin else 'group.read'
        user_util.grant_user_permission_to_repo_group(
            repo_group, user, permission)

        id_, params = build_data(
            self.apikey_regular,
            'revoke_user_permission_from_repo_group',
            repogroupid=repo_group.name,
            userid=user.username,
            apply_to_children=apply_to_children,)
        response = api_call(self.app, params)
        if access_ok:
            expected = {
                'msg': (
                    'Revoked perm (recursive:%s) for user: `%s`'
                    ' in repo group: `%s`' % (
                        apply_to_children, user.username, repo_group.name
                    )
                ),
                'success': True
            }
            assert_ok(id_, expected, given=response.body)
        else:
            expected = 'repository group `%s` does not exist' % (
                repo_group.name)
            assert_error(id_, expected, given=response.body)

    @mock.patch.object(RepoGroupModel, 'revoke_user_permission', crash)
    def test_api_revoke_user_permission_from_repo_group_exception_when_adding(
            self, user_util):
        user = user_util.create_user()
        repo_group = user_util.create_repo_group()
        id_, params = build_data(
            self.apikey,
            'revoke_user_permission_from_repo_group',
            repogroupid=repo_group.name,
            userid=user.username
        )
        response = api_call(self.app, params)

        expected = (
            'failed to edit permission for user: `%s` in repo group: `%s`' % (
                user.username, repo_group.name
            )
        )
        assert_error(id_, expected, given=response.body)
