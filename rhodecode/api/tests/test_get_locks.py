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

from rhodecode.model.db import Repository, User
from rhodecode.tests import TEST_USER_ADMIN_LOGIN, TEST_USER_REGULAR_LOGIN
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_ok, assert_error)


@pytest.mark.usefixtures("testuser_api", "app")
class TestGetLocks(object):
    def test_api_get_user_locks_regular_user(self):
        id_, params = build_data(self.apikey_regular, 'get_user_locks')
        response = api_call(self.app, params)
        expected = []
        assert_ok(id_, expected, given=response.body)

    def test_api_get_user_locks_with_userid_regular_user(self):
        id_, params = build_data(
            self.apikey_regular, 'get_user_locks', userid=TEST_USER_ADMIN_LOGIN)
        response = api_call(self.app, params)
        expected = 'userid is not the same as your user'
        assert_error(id_, expected, given=response.body)

    def test_api_get_user_locks(self):
        id_, params = build_data(self.apikey, 'get_user_locks')
        response = api_call(self.app, params)
        expected = []
        assert_ok(id_, expected, given=response.body)

    @pytest.mark.parametrize("apikey_attr, expect_secrets", [
        ('apikey', True),
        ('apikey_regular', False),
    ])
    def test_api_get_user_locks_with_one_locked_repo(
            self, apikey_attr, expect_secrets, backend):

        repo = backend.create_repo(cur_user=self.TEST_USER_LOGIN)
        Repository.lock(
            repo, User.get_by_username(self.TEST_USER_LOGIN).user_id)

        apikey = getattr(self, apikey_attr)

        id_, params = build_data(apikey, 'get_user_locks')
        if apikey_attr == 'apikey':
            # super-admin should call in specific user
            id_, params = build_data(apikey, 'get_user_locks',
                                     userid=self.TEST_USER_LOGIN)

        response = api_call(self.app, params)
        expected = [repo.get_api_data(include_secrets=expect_secrets)]
        assert_ok(id_, expected, given=response.body)

    def test_api_get_user_locks_with_one_locked_repo_for_specific_user(
            self, backend):
        repo = backend.create_repo(cur_user=self.TEST_USER_LOGIN)

        Repository.lock(repo, User.get_by_username(
            self.TEST_USER_LOGIN).user_id)
        id_, params = build_data(
            self.apikey, 'get_user_locks', userid=self.TEST_USER_LOGIN)
        response = api_call(self.app, params)
        expected = [repo.get_api_data(include_secrets=True)]
        assert_ok(id_, expected, given=response.body)

    def test_api_get_user_locks_with_userid(self):
        id_, params = build_data(
            self.apikey, 'get_user_locks', userid=TEST_USER_REGULAR_LOGIN)
        response = api_call(self.app, params)
        expected = []
        assert_ok(id_, expected, given=response.body)
