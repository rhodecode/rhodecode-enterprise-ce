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
from rhodecode.model.user import UserModel
from rhodecode.tests import TEST_USER_ADMIN_LOGIN
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_ok, assert_error, expected_permissions)


@pytest.mark.usefixtures("testuser_api", "app")
class TestGetRepo(object):
    @pytest.mark.parametrize("apikey_attr, expect_secrets", [
        ('apikey', True),
        ('apikey_regular', False),
    ])
    @pytest.mark.parametrize("cache_param", [
        True,
        False,
        None,
    ])
    def test_api_get_repo(
            self, apikey_attr, expect_secrets, cache_param, backend,
            user_util):
        repo = backend.create_repo()
        usr = UserModel().get_by_username(TEST_USER_ADMIN_LOGIN)
        group = user_util.create_user_group(members=[usr])
        user_util.grant_user_group_permission_to_repo(
            repo=repo, user_group=group, permission_name='repository.read')
        Session().commit()
        kwargs = {
            'repoid': repo.repo_name,
        }
        if cache_param is not None:
            kwargs['cache'] = cache_param

        apikey = getattr(self, apikey_attr)
        id_, params = build_data(apikey, 'get_repo', **kwargs)
        response = api_call(self.app, params)

        ret = repo.get_api_data()

        permissions = expected_permissions(repo)

        followers = []
        for user in repo.followers:
            followers.append(user.user.get_api_data(
                include_secrets=expect_secrets))

        ret['members'] = permissions
        ret['permissions'] = permissions
        ret['followers'] = followers

        expected = ret

        assert_ok(id_, expected, given=response.body)

    @pytest.mark.parametrize("grant_perm", [
        'repository.admin',
        'repository.write',
        'repository.read',
    ])
    def test_api_get_repo_by_non_admin(self, grant_perm, backend):
        # TODO: Depending on which tests are running before this one, we
        # start with a different number of permissions in the database.
        repo = RepoModel().get_by_repo_name(backend.repo_name)
        permission_count = len(repo.repo_to_perm)

        RepoModel().grant_user_permission(repo=backend.repo_name,
                                          user=self.TEST_USER_LOGIN,
                                          perm=grant_perm)
        Session().commit()
        id_, params = build_data(
            self.apikey_regular, 'get_repo', repoid=backend.repo_name)
        response = api_call(self.app, params)

        repo = RepoModel().get_by_repo_name(backend.repo_name)
        ret = repo.get_api_data()

        assert permission_count + 1, len(repo.repo_to_perm)

        permissions = expected_permissions(repo)

        followers = []
        for user in repo.followers:
            followers.append(user.user.get_api_data())

        ret['members'] = permissions
        ret['permissions'] = permissions
        ret['followers'] = followers

        expected = ret
        try:
            assert_ok(id_, expected, given=response.body)
        finally:
            RepoModel().revoke_user_permission(
                backend.repo_name, self.TEST_USER_LOGIN)

    def test_api_get_repo_by_non_admin_no_permission_to_repo(self, backend):
        RepoModel().grant_user_permission(repo=backend.repo_name,
                                          user=self.TEST_USER_LOGIN,
                                          perm='repository.none')

        id_, params = build_data(
            self.apikey_regular, 'get_repo', repoid=backend.repo_name)
        response = api_call(self.app, params)

        expected = 'repository `%s` does not exist' % (backend.repo_name)
        assert_error(id_, expected, given=response.body)

    def test_api_get_repo_not_existing(self):
        id_, params = build_data(
            self.apikey, 'get_repo', repoid='no-such-repo')
        response = api_call(self.app, params)

        ret = 'repository `%s` does not exist' % 'no-such-repo'
        expected = ret
        assert_error(id_, expected, given=response.body)
