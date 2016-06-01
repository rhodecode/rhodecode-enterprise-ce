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
from rhodecode.tests import TEST_USER_ADMIN_LOGIN, TEST_USER_REGULAR_LOGIN
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok, crash, jsonify)
from rhodecode.tests.fixture import Fixture


fixture = Fixture()

UPDATE_REPO_NAME = 'api_update_me'

class SAME_AS_UPDATES(object): """ Constant used for tests below """

@pytest.mark.usefixtures("testuser_api", "app")
class TestApiUpdateRepo(object):

    @pytest.mark.parametrize("updates, expected", [
        ({'owner': TEST_USER_REGULAR_LOGIN}, SAME_AS_UPDATES),
        ({'description': 'new description'}, SAME_AS_UPDATES),
        ({'clone_uri': 'http://foo.com/repo'}, SAME_AS_UPDATES),
        ({'clone_uri': None}, {'clone_uri': ''}),
        ({'clone_uri': ''}, {'clone_uri': ''}),
        ({'landing_rev': 'branch:master'}, {'landing_rev': ['branch','master']}),
        ({'enable_statistics': True}, SAME_AS_UPDATES),
        ({'enable_locking': True}, SAME_AS_UPDATES),
        ({'enable_downloads': True}, SAME_AS_UPDATES),
        ({'name': 'new_repo_name'}, {'repo_name': 'new_repo_name'}),
        ({'group': 'test_group_for_update'},
            {'repo_name': 'test_group_for_update/%s' % UPDATE_REPO_NAME}),
    ])
    def test_api_update_repo(self, updates, expected, backend):
        repo_name = UPDATE_REPO_NAME
        repo = fixture.create_repo(repo_name, repo_type=backend.alias)
        if updates.get('group'):
            fixture.create_repo_group(updates['group'])

        expected_api_data = repo.get_api_data(include_secrets=True)
        if expected is SAME_AS_UPDATES:
            expected_api_data.update(updates)
        else:
            expected_api_data.update(expected)


        id_, params = build_data(
            self.apikey, 'update_repo', repoid=repo_name, **updates)
        response = api_call(self.app, params)

        if updates.get('name'):
            repo_name = updates['name']
        if updates.get('group'):
            repo_name = '/'.join([updates['group'], repo_name])

        try:
            expected = {
                'msg': 'updated repo ID:%s %s' % (repo.repo_id, repo_name),
                'repository': jsonify(expected_api_data)
            }
            assert_ok(id_, expected, given=response.body)
        finally:
            fixture.destroy_repo(repo_name)
            if updates.get('group'):
                fixture.destroy_repo_group(updates['group'])

    def test_api_update_repo_fork_of_field(self, backend):
        master_repo = backend.create_repo()
        repo = backend.create_repo()
        updates = {
            'fork_of': master_repo.repo_name
        }
        expected_api_data = repo.get_api_data(include_secrets=True)
        expected_api_data.update(updates)

        id_, params = build_data(
            self.apikey, 'update_repo', repoid=repo.repo_name, **updates)
        response = api_call(self.app, params)
        expected = {
            'msg': 'updated repo ID:%s %s' % (repo.repo_id, repo.repo_name),
            'repository': jsonify(expected_api_data)
        }
        assert_ok(id_, expected, given=response.body)
        result = response.json['result']['repository']
        assert result['fork_of'] == master_repo.repo_name

    def test_api_update_repo_fork_of_not_found(self, backend):
        master_repo_name = 'fake-parent-repo'
        repo = backend.create_repo()
        updates = {
            'fork_of': master_repo_name
        }
        id_, params = build_data(
            self.apikey, 'update_repo', repoid=repo.repo_name, **updates)
        response = api_call(self.app, params)
        expected = 'repository `{}` does not exist'.format(master_repo_name)
        assert_error(id_, expected, given=response.body)

    def test_api_update_repo_with_repo_group_not_existing(self):
        repo_name = 'admin_owned'
        fixture.create_repo(repo_name)
        updates = {'group': 'test_group_for_update'}
        id_, params = build_data(
            self.apikey, 'update_repo', repoid=repo_name, **updates)
        response = api_call(self.app, params)
        try:
            expected = 'repository group `%s` does not exist' % (
                updates['group'],)
            assert_error(id_, expected, given=response.body)
        finally:
            fixture.destroy_repo(repo_name)

    def test_api_update_repo_regular_user_not_allowed(self):
        repo_name = 'admin_owned'
        fixture.create_repo(repo_name)
        updates = {'active': False}
        id_, params = build_data(
            self.apikey_regular, 'update_repo', repoid=repo_name, **updates)
        response = api_call(self.app, params)
        try:
            expected = 'repository `%s` does not exist' % (repo_name,)
            assert_error(id_, expected, given=response.body)
        finally:
            fixture.destroy_repo(repo_name)

    @mock.patch.object(RepoModel, 'update', crash)
    def test_api_update_repo_exception_occurred(self, backend):
        repo_name = UPDATE_REPO_NAME
        fixture.create_repo(repo_name, repo_type=backend.alias)
        id_, params = build_data(
            self.apikey, 'update_repo', repoid=repo_name,
            owner=TEST_USER_ADMIN_LOGIN,)
        response = api_call(self.app, params)
        try:
            expected = 'failed to update repo `%s`' % (repo_name,)
            assert_error(id_, expected, given=response.body)
        finally:
            fixture.destroy_repo(repo_name)
