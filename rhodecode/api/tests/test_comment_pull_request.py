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

from rhodecode.model.comment import ChangesetCommentsModel
from rhodecode.model.db import UserLog
from rhodecode.model.pull_request import PullRequestModel
from rhodecode.tests import TEST_USER_ADMIN_LOGIN
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok)


@pytest.mark.usefixtures("testuser_api", "app")
class TestCommentPullRequest(object):
    finalizers = []

    def teardown_method(self, method):
        if self.finalizers:
            for finalizer in self.finalizers:
                finalizer()
            self.finalizers = []

    @pytest.mark.backends("git", "hg")
    def test_api_comment_pull_request(self, pr_util, no_notifications):
        pull_request = pr_util.create_pull_request()
        pull_request_id = pull_request.pull_request_id
        author = pull_request.user_id
        repo = pull_request.target_repo.repo_id
        id_, params = build_data(
            self.apikey, 'comment_pull_request',
            repoid=pull_request.target_repo.repo_name,
            pullrequestid=pull_request.pull_request_id,
            message='test message')
        response = api_call(self.app, params)
        pull_request = PullRequestModel().get(pull_request.pull_request_id)

        comments = ChangesetCommentsModel().get_comments(
            pull_request.target_repo.repo_id, pull_request=pull_request)

        expected = {
            'pull_request_id': pull_request.pull_request_id,
            'comment_id': comments[-1].comment_id,
            'status': None
        }
        assert_ok(id_, expected, response.body)

        action = 'user_commented_pull_request:%d' % pull_request_id
        journal = UserLog.query()\
            .filter(UserLog.user_id == author)\
            .filter(UserLog.repository_id == repo)\
            .filter(UserLog.action == action)\
            .all()
        assert len(journal) == 2

    @pytest.mark.backends("git", "hg")
    def test_api_comment_pull_request_change_status(
            self, pr_util, no_notifications):
        pull_request = pr_util.create_pull_request()
        pull_request_id = pull_request.pull_request_id
        id_, params = build_data(
            self.apikey, 'comment_pull_request',
            repoid=pull_request.target_repo.repo_name,
            pullrequestid=pull_request.pull_request_id,
            status='rejected')
        response = api_call(self.app, params)
        pull_request = PullRequestModel().get(pull_request_id)

        comments = ChangesetCommentsModel().get_comments(
            pull_request.target_repo.repo_id, pull_request=pull_request)
        expected = {
            'pull_request_id': pull_request.pull_request_id,
            'comment_id': comments[-1].comment_id,
            'status': 'rejected'
        }
        assert_ok(id_, expected, response.body)

    @pytest.mark.backends("git", "hg")
    def test_api_comment_pull_request_missing_params_error(self, pr_util):
        pull_request = pr_util.create_pull_request()
        pull_request_id = pull_request.pull_request_id
        pull_request_repo = pull_request.target_repo.repo_name
        id_, params = build_data(
            self.apikey, 'comment_pull_request',
            repoid=pull_request_repo,
            pullrequestid=pull_request_id)
        response = api_call(self.app, params)

        expected = 'message and status parameter missing'
        assert_error(id_, expected, given=response.body)

    @pytest.mark.backends("git", "hg")
    def test_api_comment_pull_request_unknown_status_error(self, pr_util):
        pull_request = pr_util.create_pull_request()
        pull_request_id = pull_request.pull_request_id
        pull_request_repo = pull_request.target_repo.repo_name
        id_, params = build_data(
            self.apikey, 'comment_pull_request',
            repoid=pull_request_repo,
            pullrequestid=pull_request_id,
            status='42')
        response = api_call(self.app, params)

        expected = 'unknown comment status`42`'
        assert_error(id_, expected, given=response.body)

    @pytest.mark.backends("git", "hg")
    def test_api_comment_pull_request_repo_error(self):
        id_, params = build_data(
            self.apikey, 'comment_pull_request',
            repoid=666, pullrequestid=1)
        response = api_call(self.app, params)

        expected = 'repository `666` does not exist'
        assert_error(id_, expected, given=response.body)

    @pytest.mark.backends("git", "hg")
    def test_api_comment_pull_request_non_admin_with_userid_error(
            self, pr_util):
        pull_request = pr_util.create_pull_request()
        id_, params = build_data(
            self.apikey_regular, 'comment_pull_request',
            repoid=pull_request.target_repo.repo_name,
            pullrequestid=pull_request.pull_request_id,
            userid=TEST_USER_ADMIN_LOGIN)
        response = api_call(self.app, params)

        expected = 'userid is not the same as your user'
        assert_error(id_, expected, given=response.body)
