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

from rhodecode.model.db import User
from rhodecode.model.pull_request import PullRequestModel
from rhodecode.model.repo import RepoModel
from rhodecode.model.user import UserModel
from rhodecode.tests import TEST_USER_ADMIN_LOGIN, TEST_USER_REGULAR_LOGIN
from rhodecode.api.tests.utils import build_data, api_call, assert_error


@pytest.mark.usefixtures("testuser_api", "app")
class TestCreatePullRequestApi(object):
    finalizers = []

    def teardown_method(self, method):
        if self.finalizers:
            for finalizer in self.finalizers:
                finalizer()
            self.finalizers = []

    def test_create_with_wrong_data(self):
        required_data = {
            'source_repo': 'tests/source_repo',
            'target_repo': 'tests/target_repo',
            'source_ref': 'branch:default:initial',
            'target_ref': 'branch:default:new-feature',
            'title': 'Test PR 1'
        }
        for key in required_data:
            data = required_data.copy()
            data.pop(key)
            id_, params = build_data(
                self.apikey, 'create_pull_request', **data)
            response = api_call(self.app, params)

            expected = 'Missing non optional `{}` arg in JSON DATA'.format(key)
            assert_error(id_, expected, given=response.body)

    @pytest.mark.backends("git", "hg")
    def test_create_with_correct_data(self, backend):
        data = self._prepare_data(backend)
        RepoModel().revoke_user_permission(
            self.source.repo_name, User.DEFAULT_USER)
        id_, params = build_data(
            self.apikey_regular, 'create_pull_request', **data)
        response = api_call(self.app, params)
        expected_message = "Created new pull request `{title}`".format(
            title=data['title'])
        result = response.json
        assert result['result']['msg'] == expected_message
        pull_request_id = result['result']['pull_request_id']
        pull_request = PullRequestModel().get(pull_request_id)
        assert pull_request.title == data['title']
        assert pull_request.description == data['description']
        assert pull_request.source_ref == data['source_ref']
        assert pull_request.target_ref == data['target_ref']
        assert pull_request.source_repo.repo_name == data['source_repo']
        assert pull_request.target_repo.repo_name == data['target_repo']
        assert pull_request.revisions == [self.commit_ids['change']]
        assert pull_request.reviewers == []

    @pytest.mark.backends("git", "hg")
    def test_create_with_empty_description(self, backend):
        data = self._prepare_data(backend)
        data.pop('description')
        id_, params = build_data(
            self.apikey_regular, 'create_pull_request', **data)
        response = api_call(self.app, params)
        expected_message = "Created new pull request `{title}`".format(
            title=data['title'])
        result = response.json
        assert result['result']['msg'] == expected_message
        pull_request_id = result['result']['pull_request_id']
        pull_request = PullRequestModel().get(pull_request_id)
        assert pull_request.description == ''

    @pytest.mark.backends("git", "hg")
    def test_create_with_reviewers_specified_by_names(
            self, backend, no_notifications):
        data = self._prepare_data(backend)
        reviewers = [TEST_USER_REGULAR_LOGIN, TEST_USER_ADMIN_LOGIN]
        data['reviewers'] = reviewers
        id_, params = build_data(
            self.apikey_regular, 'create_pull_request', **data)
        response = api_call(self.app, params)

        expected_message = "Created new pull request `{title}`".format(
            title=data['title'])
        result = response.json
        assert result['result']['msg'] == expected_message
        pull_request_id = result['result']['pull_request_id']
        pull_request = PullRequestModel().get(pull_request_id)
        actual_reviewers = [r.user.username for r in pull_request.reviewers]
        assert sorted(actual_reviewers) == sorted(reviewers)

    @pytest.mark.backends("git", "hg")
    def test_create_with_reviewers_specified_by_ids(
            self, backend, no_notifications):
        data = self._prepare_data(backend)
        reviewer_names = [TEST_USER_REGULAR_LOGIN, TEST_USER_ADMIN_LOGIN]
        reviewers = [
            UserModel().get_by_username(n).user_id for n in reviewer_names]
        data['reviewers'] = reviewers
        id_, params = build_data(
            self.apikey_regular, 'create_pull_request', **data)
        response = api_call(self.app, params)

        expected_message = "Created new pull request `{title}`".format(
            title=data['title'])
        result = response.json
        assert result['result']['msg'] == expected_message
        pull_request_id = result['result']['pull_request_id']
        pull_request = PullRequestModel().get(pull_request_id)
        actual_reviewers = [r.user.username for r in pull_request.reviewers]
        assert sorted(actual_reviewers) == sorted(reviewer_names)

    @pytest.mark.backends("git", "hg")
    def test_create_fails_when_the_reviewer_is_not_found(self, backend):
        data = self._prepare_data(backend)
        reviewers = ['somebody']
        data['reviewers'] = reviewers
        id_, params = build_data(
            self.apikey_regular, 'create_pull_request', **data)
        response = api_call(self.app, params)
        expected_message = 'user `somebody` does not exist'
        assert_error(id_, expected_message, given=response.body)

    @pytest.mark.backends("git", "hg")
    def test_cannot_create_with_reviewers_in_wrong_format(self, backend):
        data = self._prepare_data(backend)
        reviewers = ','.join([TEST_USER_REGULAR_LOGIN, TEST_USER_ADMIN_LOGIN])
        data['reviewers'] = reviewers
        id_, params = build_data(
            self.apikey_regular, 'create_pull_request', **data)
        response = api_call(self.app, params)
        expected_message = 'reviewers should be specified as a list'
        assert_error(id_, expected_message, given=response.body)

    @pytest.mark.backends("git", "hg")
    def test_create_with_no_commit_hashes(self, backend):
        data = self._prepare_data(backend)
        expected_source_ref = data['source_ref']
        expected_target_ref = data['target_ref']
        data['source_ref'] = 'branch:{}'.format(backend.default_branch_name)
        data['target_ref'] = 'branch:{}'.format(backend.default_branch_name)
        id_, params = build_data(
            self.apikey_regular, 'create_pull_request', **data)
        response = api_call(self.app, params)
        expected_message = "Created new pull request `{title}`".format(
            title=data['title'])
        result = response.json
        assert result['result']['msg'] == expected_message
        pull_request_id = result['result']['pull_request_id']
        pull_request = PullRequestModel().get(pull_request_id)
        assert pull_request.source_ref == expected_source_ref
        assert pull_request.target_ref == expected_target_ref

    @pytest.mark.backends("git", "hg")
    @pytest.mark.parametrize("data_key", ["source_repo", "target_repo"])
    def test_create_fails_with_wrong_repo(self, backend, data_key):
        repo_name = 'fake-repo'
        data = self._prepare_data(backend)
        data[data_key] = repo_name
        id_, params = build_data(
            self.apikey_regular, 'create_pull_request', **data)
        response = api_call(self.app, params)
        expected_message = 'repository `{}` does not exist'.format(repo_name)
        assert_error(id_, expected_message, given=response.body)

    @pytest.mark.backends("git", "hg")
    @pytest.mark.parametrize("data_key", ["source_ref", "target_ref"])
    def test_create_fails_with_non_existing_branch(self, backend, data_key):
        branch_name = 'test-branch'
        data = self._prepare_data(backend)
        data[data_key] = "branch:{}".format(branch_name)
        id_, params = build_data(
            self.apikey_regular, 'create_pull_request', **data)
        response = api_call(self.app, params)
        expected_message = 'The specified branch `{}` does not exist'.format(
            branch_name)
        assert_error(id_, expected_message, given=response.body)

    @pytest.mark.backends("git", "hg")
    @pytest.mark.parametrize("data_key", ["source_ref", "target_ref"])
    def test_create_fails_with_ref_in_a_wrong_format(self, backend, data_key):
        data = self._prepare_data(backend)
        ref = 'stange-ref'
        data[data_key] = ref
        id_, params = build_data(
            self.apikey_regular, 'create_pull_request', **data)
        response = api_call(self.app, params)
        expected_message = (
            'Ref `{ref}` given in a wrong format. Please check the API'
            ' documentation for more details'.format(ref=ref))
        assert_error(id_, expected_message, given=response.body)

    @pytest.mark.backends("git", "hg")
    @pytest.mark.parametrize("data_key", ["source_ref", "target_ref"])
    def test_create_fails_with_non_existing_ref(self, backend, data_key):
        commit_id = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa10'
        ref = self._get_full_ref(backend, commit_id)
        data = self._prepare_data(backend)
        data[data_key] = ref
        id_, params = build_data(
            self.apikey_regular, 'create_pull_request', **data)
        response = api_call(self.app, params)
        expected_message = 'Ref `{}` does not exist'.format(ref)
        assert_error(id_, expected_message, given=response.body)

    @pytest.mark.backends("git", "hg")
    def test_create_fails_when_no_revisions(self, backend):
        data = self._prepare_data(backend, source_head='initial')
        id_, params = build_data(
            self.apikey_regular, 'create_pull_request', **data)
        response = api_call(self.app, params)
        expected_message = 'no commits found'
        assert_error(id_, expected_message, given=response.body)

    @pytest.mark.backends("git", "hg")
    def test_create_fails_when_no_permissions(self, backend):
        data = self._prepare_data(backend)
        RepoModel().revoke_user_permission(
            self.source.repo_name, User.DEFAULT_USER)
        RepoModel().revoke_user_permission(
            self.source.repo_name, self.test_user)
        id_, params = build_data(
            self.apikey_regular, 'create_pull_request', **data)
        response = api_call(self.app, params)
        expected_message = 'repository `{}` does not exist'.format(
            self.source.repo_name)
        assert_error(id_, expected_message, given=response.body)

    def _prepare_data(
            self, backend, source_head='change', target_head='initial'):
        commits = [
            {'message': 'initial'},
            {'message': 'change'},
            {'message': 'new-feature', 'parents': ['initial']},
        ]
        self.commit_ids = backend.create_master_repo(commits)
        self.source = backend.create_repo(heads=[source_head])
        self.target = backend.create_repo(heads=[target_head])
        data = {
            'source_repo': self.source.repo_name,
            'target_repo': self.target.repo_name,
            'source_ref': self._get_full_ref(
                backend, self.commit_ids[source_head]),
            'target_ref': self._get_full_ref(
                backend, self.commit_ids[target_head]),
            'title': 'Test PR 1',
            'description': 'Test'
        }
        RepoModel().grant_user_permission(
            self.source.repo_name, self.TEST_USER_LOGIN, 'repository.read')
        return data

    def _get_full_ref(self, backend, commit_id):
        return 'branch:{branch}:{commit_id}'.format(
            branch=backend.default_branch_name, commit_id=commit_id)
