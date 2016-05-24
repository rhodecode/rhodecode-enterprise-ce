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
class TestRevokeUserPermission(object):
    def test_api_revoke_user_permission(self, backend, user_util):
        repo = backend.create_repo()
        user = user_util.create_user()
        user_util.grant_user_permission_to_repo(
            repo, user, 'repository.read')

        id_, params = build_data(
            self.apikey,
            'revoke_user_permission',
            repoid=repo.repo_name,
            userid=user.username)
        response = api_call(self.app, params)

        expected = {
            'msg': 'Revoked perm for user: `%s` in repo: `%s`' % (
                user.username, backend.repo_name
            ),
            'success': True
        }
        assert_ok(id_, expected, given=response.body)

    @mock.patch.object(RepoModel, 'revoke_user_permission', crash)
    def test_api_revoke_user_permission_exception_when_adding(
            self, backend, user_util):
        user = user_util.create_user()
        id_, params = build_data(
            self.apikey,
            'revoke_user_permission',
            repoid=backend.repo_name,
            userid=user.username)
        response = api_call(self.app, params)

        expected = 'failed to edit permission for user: `%s` in repo: `%s`' % (
            user.username, backend.repo_name
        )
        assert_error(id_, expected, given=response.body)
