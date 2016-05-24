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

from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.user import UserModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok)


@pytest.mark.usefixtures("testuser_api", "app")
class TestApiDeleteRepoGroup(object):
    def test_api_delete_repo_group(self, user_util):
        repo_group = user_util.create_repo_group(auto_cleanup=False)
        repo_group_name = repo_group.group_name
        repo_group_id = repo_group.group_id
        id_, params = build_data(
            self.apikey, 'delete_repo_group', repogroupid=repo_group_name, )
        response = api_call(self.app, params)

        ret = {
            'msg': 'deleted repo group ID:%s %s' % (
                repo_group_id, repo_group_name
            ),
            'repo_group': None
        }
        expected = ret
        assert_ok(id_, expected, given=response.body)
        gr = RepoGroupModel()._get_repo_group(repo_group_name)
        assert gr is None

    def test_api_delete_repo_group_regular_user(self, user_util):
        repo_group = user_util.create_repo_group(auto_cleanup=False)
        repo_group_name = repo_group.group_name
        repo_group_id = repo_group.group_id

        user = UserModel().get_by_username(self.TEST_USER_LOGIN)
        user_util.grant_user_permission_to_repo_group(
            repo_group, user, 'group.admin')

        id_, params = build_data(
            self.apikey, 'delete_repo_group', repogroupid=repo_group_name, )
        response = api_call(self.app, params)

        ret = {
            'msg': 'deleted repo group ID:%s %s' % (
                repo_group_id, repo_group_name
            ),
            'repo_group': None
        }
        expected = ret
        assert_ok(id_, expected, given=response.body)
        gr = RepoGroupModel()._get_repo_group(repo_group_name)
        assert gr is None

    def test_api_delete_repo_group_regular_user_no_permission(self, user_util):
        repo_group = user_util.create_repo_group()
        repo_group_name = repo_group.group_name

        id_, params = build_data(
            self.apikey_regular, 'delete_repo_group',
            repogroupid=repo_group_name, )
        response = api_call(self.app, params)

        expected = 'repository group `%s` does not exist' % (
            repo_group_name,)
        assert_error(id_, expected, given=response.body)
