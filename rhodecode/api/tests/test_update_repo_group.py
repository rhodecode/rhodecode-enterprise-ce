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

import os

import pytest

from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.user import UserModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok)


@pytest.mark.usefixtures("testuser_api", "app")
class TestApiUpdateRepoGroup(object):
    def test_update_group_name(self, user_util):
        new_group_name = 'new-group'
        initial_name = self._update(user_util, group_name=new_group_name)
        assert RepoGroupModel()._get_repo_group(initial_name) is None
        assert RepoGroupModel()._get_repo_group(new_group_name) is not None

    def test_update_parent(self, user_util):
        parent_group = user_util.create_repo_group()
        initial_name = self._update(user_util, parent=parent_group.name)

        expected_group_name = '{}/{}'.format(parent_group.name, initial_name)
        repo_group = RepoGroupModel()._get_repo_group(expected_group_name)
        assert repo_group is not None
        assert repo_group.group_name == expected_group_name
        assert repo_group.name == initial_name
        assert RepoGroupModel()._get_repo_group(initial_name) is None
        new_path = os.path.join(
            RepoGroupModel().repos_path, *repo_group.full_path_splitted)
        assert os.path.exists(new_path)

    def test_update_enable_locking(self, user_util):
        initial_name = self._update(user_util, enable_locking=True)
        repo_group = RepoGroupModel()._get_repo_group(initial_name)
        assert repo_group.enable_locking is True

    def test_update_description(self, user_util):
        description = 'New description'
        initial_name = self._update(user_util, description=description)
        repo_group = RepoGroupModel()._get_repo_group(initial_name)
        assert repo_group.group_description == description

    def test_update_owner(self, user_util):
        owner = self.TEST_USER_LOGIN
        initial_name = self._update(user_util, owner=owner)
        repo_group = RepoGroupModel()._get_repo_group(initial_name)
        assert repo_group.user.username == owner

    def test_api_update_repo_group_by_regular_user_no_permission(
            self, backend):
        repo = backend.create_repo()
        repo_name = repo.repo_name

        id_, params = build_data(
            self.apikey_regular, 'update_repo_group', repogroupid=repo_name)
        response = api_call(self.app, params)
        expected = 'repository group `%s` does not exist' % (repo_name,)
        assert_error(id_, expected, given=response.body)

    def _update(self, user_util, **kwargs):
        repo_group = user_util.create_repo_group()
        initial_name = repo_group.name
        user = UserModel().get_by_username(self.TEST_USER_LOGIN)
        user_util.grant_user_permission_to_repo_group(
            repo_group, user, 'group.admin')

        id_, params = build_data(
            self.apikey, 'update_repo_group', repogroupid=initial_name,
            **kwargs)
        response = api_call(self.app, params)
        ret = {
            'msg': 'updated repository group ID:{} {}'.format(
                repo_group.group_id, repo_group.group_name),
            'repo_group': {
                'repositories': [],
                'group_name': repo_group.group_name,
                'group_description': repo_group.group_description,
                'owner': repo_group.user.username,
                'group_id': repo_group.group_id,
                'parent_group': (
                    repo_group.parent_group.name
                    if repo_group.parent_group else None)
            }
        }
        assert_ok(id_, ret, given=response.body)
        return initial_name
