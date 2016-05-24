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

from rhodecode.model.db import Repository
from rhodecode.model.user import UserModel
from rhodecode.lib.ext_json import json
from rhodecode.lib.utils2 import time_to_datetime
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_ok, assert_error, crash)
from rhodecode.tests import TEST_USER_ADMIN_LOGIN


@pytest.mark.usefixtures("testuser_api", "app")
class TestLock(object):
    def test_api_lock_repo_lock_aquire(self, backend):
        id_, params = build_data(
            self.apikey, 'lock',
            userid=TEST_USER_ADMIN_LOGIN,
            repoid=backend.repo_name,
            locked=True)
        response = api_call(self.app, params)
        expected = {
            'repo': backend.repo_name, 'locked': True,
            'locked_since': response.json['result']['locked_since'],
            'locked_by': TEST_USER_ADMIN_LOGIN,
            'lock_state_changed': True,
            'lock_reason': Repository.LOCK_API,
            'msg': ('User `%s` set lock state for repo `%s` to `%s`'
                    % (TEST_USER_ADMIN_LOGIN, backend.repo_name, True))
        }
        assert_ok(id_, expected, given=response.body)

    def test_repo_lock_aquire_by_non_admin(self, backend):
        repo = backend.create_repo(cur_user=self.TEST_USER_LOGIN)
        repo_name = repo.repo_name
        id_, params = build_data(
            self.apikey_regular, 'lock',
            repoid=repo_name,
            locked=True)
        response = api_call(self.app, params)
        expected = {
            'repo': repo_name,
            'locked': True,
            'locked_since': response.json['result']['locked_since'],
            'locked_by': self.TEST_USER_LOGIN,
            'lock_state_changed': True,
            'lock_reason': Repository.LOCK_API,
            'msg': ('User `%s` set lock state for repo `%s` to `%s`'
                    % (self.TEST_USER_LOGIN, repo_name, True))
        }
        assert_ok(id_, expected, given=response.body)

    def test_api_lock_repo_lock_aquire_non_admin_with_userid(self, backend):
        repo = backend.create_repo(cur_user=self.TEST_USER_LOGIN)
        repo_name = repo.repo_name
        id_, params = build_data(
            self.apikey_regular, 'lock',
            userid=TEST_USER_ADMIN_LOGIN,
            repoid=repo_name,
            locked=True)
        response = api_call(self.app, params)
        expected = 'userid is not the same as your user'
        assert_error(id_, expected, given=response.body)

    def test_api_lock_repo_lock_aquire_non_admin_not_his_repo(self, backend):
        id_, params = build_data(
            self.apikey_regular, 'lock',
            repoid=backend.repo_name,
            locked=True)
        response = api_call(self.app, params)
        expected = 'repository `%s` does not exist' % (backend.repo_name, )
        assert_error(id_, expected, given=response.body)

    def test_api_lock_repo_lock_release(self, backend):
        id_, params = build_data(
            self.apikey, 'lock',
            userid=TEST_USER_ADMIN_LOGIN,
            repoid=backend.repo_name,
            locked=False)
        response = api_call(self.app, params)
        expected = {
            'repo': backend.repo_name,
            'locked': False,
            'locked_since': None,
            'locked_by': TEST_USER_ADMIN_LOGIN,
            'lock_state_changed': True,
            'lock_reason': Repository.LOCK_API,
            'msg': ('User `%s` set lock state for repo `%s` to `%s`'
                    % (TEST_USER_ADMIN_LOGIN, backend.repo_name, False))
        }
        assert_ok(id_, expected, given=response.body)

    def test_api_lock_repo_lock_aquire_optional_userid(self, backend):
        id_, params = build_data(
            self.apikey, 'lock',
            repoid=backend.repo_name,
            locked=True)
        response = api_call(self.app, params)
        time_ = response.json['result']['locked_since']
        expected = {
            'repo': backend.repo_name,
            'locked': True,
            'locked_since': time_,
            'locked_by': TEST_USER_ADMIN_LOGIN,
            'lock_state_changed': True,
            'lock_reason': Repository.LOCK_API,
            'msg': ('User `%s` set lock state for repo `%s` to `%s`'
                    % (TEST_USER_ADMIN_LOGIN, backend.repo_name, True))
        }

        assert_ok(id_, expected, given=response.body)

    def test_api_lock_repo_lock_optional_locked(self, backend):
        # TODO: Provide a fixture locked_repository or similar
        repo = Repository.get_by_repo_name(backend.repo_name)
        user = UserModel().get_by_username(TEST_USER_ADMIN_LOGIN)
        Repository.lock(repo, user.user_id, lock_reason=Repository.LOCK_API)

        id_, params = build_data(self.apikey, 'lock', repoid=backend.repo_name)
        response = api_call(self.app, params)
        time_ = response.json['result']['locked_since']
        expected = {
            'repo': backend.repo_name,
            'locked': True,
            'locked_since': time_,
            'locked_by': TEST_USER_ADMIN_LOGIN,
            'lock_state_changed': False,
            'lock_reason': Repository.LOCK_API,
            'msg': ('Repo `%s` locked by `%s` on `%s`.'
                    % (backend.repo_name, TEST_USER_ADMIN_LOGIN,
                       json.dumps(time_to_datetime(time_))))
        }
        assert_ok(id_, expected, given=response.body)

    def test_api_lock_repo_lock_optional_not_locked(self, backend):
        repo = backend.create_repo(cur_user=self.TEST_USER_LOGIN)
        repo_name = repo.repo_name
        assert repo.locked == [None, None, None]
        id_, params = build_data(self.apikey, 'lock', repoid=repo.repo_id)
        response = api_call(self.app, params)
        expected = {
            'repo': repo_name,
            'locked': False,
            'locked_since': None,
            'locked_by': None,
            'lock_state_changed': False,
            'lock_reason': None,
            'msg': ('Repo `%s` not locked.' % (repo_name,))
        }
        assert_ok(id_, expected, given=response.body)

    @mock.patch.object(Repository, 'lock', crash)
    def test_api_lock_error(self, backend):
        id_, params = build_data(
            self.apikey, 'lock',
            userid=TEST_USER_ADMIN_LOGIN,
            repoid=backend.repo_name,
            locked=True)
        response = api_call(self.app, params)

        expected = 'Error occurred locking repository `%s`' % (
            backend.repo_name,)
        assert_error(id_, expected, given=response.body)
