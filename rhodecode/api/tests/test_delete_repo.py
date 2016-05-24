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
class TestApiDeleteRepo(object):
    def test_api_delete_repo(self, backend):
        repo = backend.create_repo()

        id_, params = build_data(
            self.apikey, 'delete_repo', repoid=repo.repo_name, )
        response = api_call(self.app, params)

        expected = {
            'msg': 'Deleted repository `%s`' % (repo.repo_name,),
            'success': True
        }
        assert_ok(id_, expected, given=response.body)

    def test_api_delete_repo_by_non_admin(self, backend, user_regular):
        repo = backend.create_repo(cur_user=user_regular.username)
        id_, params = build_data(
            user_regular.api_key, 'delete_repo', repoid=repo.repo_name, )
        response = api_call(self.app, params)

        expected = {
            'msg': 'Deleted repository `%s`' % (repo.repo_name,),
            'success': True
        }
        assert_ok(id_, expected, given=response.body)

    def test_api_delete_repo_by_non_admin_no_permission(
            self, backend, user_regular):
        repo = backend.create_repo()
        id_, params = build_data(
            user_regular.api_key, 'delete_repo', repoid=repo.repo_name, )
        response = api_call(self.app, params)
        expected = 'repository `%s` does not exist' % (repo.repo_name)
        assert_error(id_, expected, given=response.body)

    def test_api_delete_repo_exception_occurred(self, backend):
        repo = backend.create_repo()
        id_, params = build_data(
            self.apikey, 'delete_repo', repoid=repo.repo_name, )
        with mock.patch.object(RepoModel, 'delete', crash):
            response = api_call(self.app, params)
        expected = 'failed to delete repository `%s`' % (
            repo.repo_name,)
        assert_error(id_, expected, given=response.body)
