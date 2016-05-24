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

from rhodecode.model.meta import Session
from rhodecode.model.repo import RepoModel
from rhodecode.model.user import UserModel
from rhodecode.tests import TEST_USER_ADMIN_LOGIN
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok, crash)
from rhodecode.tests.fixture import Fixture


fixture = Fixture()


@pytest.mark.usefixtures("testuser_api", "app")
class TestApiForkRepo(object):
    def test_api_fork_repo(self, backend):
        source_name = backend['minimal'].repo_name
        fork_name = backend.new_repo_name()

        id_, params = build_data(
            self.apikey, 'fork_repo',
            repoid=source_name,
            fork_name=fork_name,
            owner=TEST_USER_ADMIN_LOGIN)
        response = api_call(self.app, params)

        expected = {
            'msg': 'Created fork of `%s` as `%s`' % (source_name, fork_name),
            'success': True,
            'task': None,
        }
        try:
            assert_ok(id_, expected, given=response.body)
        finally:
            fixture.destroy_repo(fork_name)

    def test_api_fork_repo_into_group(self, backend, user_util):
        source_name = backend['minimal'].repo_name
        repo_group = user_util.create_repo_group()
        fork_name = '%s/api-repo-fork' % repo_group.group_name
        id_, params = build_data(
            self.apikey, 'fork_repo',
            repoid=source_name,
            fork_name=fork_name,
            owner=TEST_USER_ADMIN_LOGIN)
        response = api_call(self.app, params)

        ret = {
            'msg': 'Created fork of `%s` as `%s`' % (source_name, fork_name),
            'success': True,
            'task': None,
        }
        expected = ret
        try:
            assert_ok(id_, expected, given=response.body)
        finally:
            fixture.destroy_repo(fork_name)

    def test_api_fork_repo_non_admin(self, backend):
        source_name = backend['minimal'].repo_name
        fork_name = backend.new_repo_name()

        id_, params = build_data(
            self.apikey_regular, 'fork_repo',
            repoid=source_name,
            fork_name=fork_name)
        response = api_call(self.app, params)

        expected = {
            'msg': 'Created fork of `%s` as `%s`' % (source_name, fork_name),
            'success': True,
            'task': None,
        }
        try:
            assert_ok(id_, expected, given=response.body)
        finally:
            fixture.destroy_repo(fork_name)

    def test_api_fork_repo_non_admin_into_group(self, backend, user_util):
        source_name = backend['minimal'].repo_name
        repo_group = user_util.create_repo_group()
        fork_name = '%s/api-repo-fork' % repo_group.group_name

        id_, params = build_data(
            self.apikey_regular, 'fork_repo',
            repoid=source_name,
            fork_name=fork_name)
        response = api_call(self.app, params)

        expected = {
            'msg': 'Created fork of `%s` as `%s`' % (source_name, fork_name),
            'success': True,
            'task': None,
        }
        try:
            assert_ok(id_, expected, given=response.body)
        finally:
            fixture.destroy_repo(fork_name)

    def test_api_fork_repo_non_admin_specify_owner(self, backend):
        source_name = backend['minimal'].repo_name
        fork_name = backend.new_repo_name()
        id_, params = build_data(
            self.apikey_regular, 'fork_repo',
            repoid=source_name,
            fork_name=fork_name,
            owner=TEST_USER_ADMIN_LOGIN)
        response = api_call(self.app, params)
        expected = 'Only RhodeCode admin can specify `owner` param'
        assert_error(id_, expected, given=response.body)

    def test_api_fork_repo_non_admin_no_permission_to_fork(self, backend):
        source_name = backend['minimal'].repo_name
        RepoModel().grant_user_permission(repo=source_name,
                                          user=self.TEST_USER_LOGIN,
                                          perm='repository.none')
        fork_name = backend.new_repo_name()
        id_, params = build_data(
            self.apikey_regular, 'fork_repo',
            repoid=backend.repo_name,
            fork_name=fork_name)
        response = api_call(self.app, params)
        expected = 'repository `%s` does not exist' % (backend.repo_name)
        assert_error(id_, expected, given=response.body)

    def test_api_fork_repo_non_admin_no_permission_to_fork_to_root_level(
            self, backend):
        source_name = backend['minimal'].repo_name

        usr = UserModel().get_by_username(self.TEST_USER_LOGIN)
        usr.inherit_default_permissions = False
        Session().add(usr)

        fork_name = backend.new_repo_name()
        id_, params = build_data(
            self.apikey_regular, 'fork_repo',
            repoid=source_name,
            fork_name=fork_name)
        response = api_call(self.app, params)
        expected = "Access was denied to this resource."
        assert_error(id_, expected, given=response.body)

    def test_api_fork_repo_unknown_owner(self, backend):
        source_name = backend['minimal'].repo_name
        fork_name = backend.new_repo_name()
        owner = 'i-dont-exist'
        id_, params = build_data(
            self.apikey, 'fork_repo',
            repoid=source_name,
            fork_name=fork_name,
            owner=owner)
        response = api_call(self.app, params)
        expected = 'user `%s` does not exist' % (owner,)
        assert_error(id_, expected, given=response.body)

    def test_api_fork_repo_fork_exists(self, backend):
        source_name = backend['minimal'].repo_name
        fork_name = backend.new_repo_name()
        fork_repo = fixture.create_fork(source_name, fork_name)

        id_, params = build_data(
            self.apikey, 'fork_repo',
            repoid=source_name,
            fork_name=fork_name,
            owner=TEST_USER_ADMIN_LOGIN)
        response = api_call(self.app, params)

        try:
            expected = "fork `%s` already exist" % (fork_name,)
            assert_error(id_, expected, given=response.body)
        finally:
            fixture.destroy_repo(fork_repo.repo_name)

    def test_api_fork_repo_repo_exists(self, backend):
        source_name = backend['minimal'].repo_name
        fork_name = source_name

        id_, params = build_data(
            self.apikey, 'fork_repo',
            repoid=source_name,
            fork_name=fork_name,
            owner=TEST_USER_ADMIN_LOGIN)
        response = api_call(self.app, params)

        expected = "repo `%s` already exist" % (fork_name,)
        assert_error(id_, expected, given=response.body)

    @mock.patch.object(RepoModel, 'create_fork', crash)
    def test_api_fork_repo_exception_occurred(self, backend):
        source_name = backend['minimal'].repo_name
        fork_name = backend.new_repo_name()
        id_, params = build_data(
            self.apikey, 'fork_repo',
            repoid=source_name,
            fork_name=fork_name,
            owner=TEST_USER_ADMIN_LOGIN)
        response = api_call(self.app, params)

        expected = 'failed to fork repository `%s` as `%s`' % (source_name,
                                                               fork_name)
        assert_error(id_, expected, given=response.body)
