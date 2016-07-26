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

from rhodecode.model.meta import Session
from rhodecode.model.repo import RepoModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok)


@pytest.mark.usefixtures("testuser_api", "app")
class TestGetRepoNodes(object):
    @pytest.mark.parametrize("name, ret_type", [
        ('all', 'all'),
        ('dirs', 'dirs'),
        ('files', 'files'),
    ])
    def test_api_get_repo_nodes(self, name, ret_type, backend):
        commit_id = 'tip'
        path = '/'
        id_, params = build_data(
            self.apikey, 'get_repo_nodes',
            repoid=backend.repo_name, revision=commit_id,
            root_path=path,
            ret_type=ret_type)
        response = api_call(self.app, params)

        # we don't the actual return types here since it's tested somewhere
        # else
        expected = response.json['result']
        assert_ok(id_, expected, given=response.body)

    def test_api_get_repo_nodes_bad_commits(self, backend):
        commit_id = 'i-dont-exist'
        path = '/'
        id_, params = build_data(
            self.apikey, 'get_repo_nodes',
            repoid=backend.repo_name, revision=commit_id,
            root_path=path, )
        response = api_call(self.app, params)

        expected = 'failed to get repo: `%s` nodes' % (backend.repo_name,)
        assert_error(id_, expected, given=response.body)

    def test_api_get_repo_nodes_bad_path(self, backend):
        commit_id = 'tip'
        path = '/idontexits'
        id_, params = build_data(
            self.apikey, 'get_repo_nodes',
            repoid=backend.repo_name, revision=commit_id,
            root_path=path, )
        response = api_call(self.app, params)

        expected = 'failed to get repo: `%s` nodes' % (backend.repo_name,)
        assert_error(id_, expected, given=response.body)

    def test_api_get_repo_nodes_max_file_bytes(self, backend):
        commit_id = 'tip'
        path = '/'
        max_file_bytes = 500

        id_, params = build_data(
            self.apikey, 'get_repo_nodes',
            repoid=backend.repo_name, revision=commit_id, details='full',
            root_path=path)
        response = api_call(self.app, params)
        assert any(file['content'] and len(file['content']) > max_file_bytes
                   for file in response.json['result'])

        id_, params = build_data(
            self.apikey, 'get_repo_nodes',
            repoid=backend.repo_name, revision=commit_id,
            root_path=path, details='full',
            max_file_bytes=max_file_bytes)
        response = api_call(self.app, params)
        assert all(
            file['content'] is None if file['size'] > max_file_bytes else True
            for file in response.json['result'])

    def test_api_get_repo_nodes_bad_ret_type(self, backend):
        commit_id = 'tip'
        path = '/'
        ret_type = 'error'
        id_, params = build_data(
            self.apikey, 'get_repo_nodes',
            repoid=backend.repo_name, revision=commit_id,
            root_path=path,
            ret_type=ret_type)
        response = api_call(self.app, params)

        expected = ('ret_type must be one of %s'
                    % (','.join(['all', 'dirs', 'files'])))
        assert_error(id_, expected, given=response.body)

    @pytest.mark.parametrize("name, ret_type, grant_perm", [
        ('all', 'all', 'repository.write'),
        ('dirs', 'dirs', 'repository.admin'),
        ('files', 'files', 'repository.read'),
    ])
    def test_api_get_repo_nodes_by_regular_user(
            self, name, ret_type, grant_perm, backend):
        RepoModel().grant_user_permission(repo=backend.repo_name,
                                          user=self.TEST_USER_LOGIN,
                                          perm=grant_perm)
        Session().commit()

        commit_id = 'tip'
        path = '/'
        id_, params = build_data(
            self.apikey_regular, 'get_repo_nodes',
            repoid=backend.repo_name, revision=commit_id,
            root_path=path,
            ret_type=ret_type)
        response = api_call(self.app, params)

        # we don't the actual return types here since it's tested somewhere
        # else
        expected = response.json['result']
        try:
            assert_ok(id_, expected, given=response.body)
        finally:
            RepoModel().revoke_user_permission(
                backend.repo_name, self.TEST_USER_LOGIN)
