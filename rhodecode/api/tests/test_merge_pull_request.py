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

from rhodecode.model.db import UserLog
from rhodecode.model.meta import Session
from rhodecode.model.pull_request import PullRequestModel
from rhodecode.tests import TEST_USER_ADMIN_LOGIN
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error)


@pytest.mark.usefixtures("testuser_api", "app")
class TestMergePullRequest(object):
    @pytest.mark.backends("git", "hg")
    def test_api_merge_pull_request(self, pr_util, no_notifications):
        pull_request = pr_util.create_pull_request()
        pull_request_2 = PullRequestModel().create(
            created_by=pull_request.author,
            source_repo=pull_request.source_repo,
            source_ref=pull_request.source_ref,
            target_repo=pull_request.target_repo,
            target_ref=pull_request.target_ref,
            revisions=pull_request.revisions,
            reviewers=(),
            title=pull_request.title,
            description=pull_request.description,
        )
        author = pull_request.user_id
        repo = pull_request_2.target_repo.repo_id
        pull_request_2_id = pull_request_2.pull_request_id
        pull_request_2_repo = pull_request_2.target_repo.repo_name
        Session().commit()

        id_, params = build_data(
            self.apikey, 'merge_pull_request',
            repoid=pull_request_2_repo,
            pullrequestid=pull_request_2_id)
        response = api_call(self.app, params)

        expected = {
            'executed': True,
            'failure_reason': 0,
            'possible': True
        }

        response_json = response.json['result']
        assert response_json['merge_commit_id']
        response_json.pop('merge_commit_id')
        assert response_json == expected

        action = 'user_merged_pull_request:%d' % (pull_request_2_id, )
        journal = UserLog.query()\
            .filter(UserLog.user_id == author)\
            .filter(UserLog.repository_id == repo)\
            .filter(UserLog.action == action)\
            .all()
        assert len(journal) == 1

        id_, params = build_data(
            self.apikey, 'merge_pull_request',
            repoid=pull_request_2_repo, pullrequestid=pull_request_2_id)
        response = api_call(self.app, params)

        expected = 'pull request `%s` merge failed, pull request is closed' % (
            pull_request_2_id)
        assert_error(id_, expected, given=response.body)

    @pytest.mark.backends("git", "hg")
    def test_api_merge_pull_request_repo_error(self):
        id_, params = build_data(
            self.apikey, 'merge_pull_request',
            repoid=666, pullrequestid=1)
        response = api_call(self.app, params)

        expected = 'repository `666` does not exist'
        assert_error(id_, expected, given=response.body)

    @pytest.mark.backends("git", "hg")
    def test_api_merge_pull_request_non_admin_with_userid_error(self,
                                                                pr_util):
        pull_request = pr_util.create_pull_request(mergeable=True)
        id_, params = build_data(
            self.apikey_regular, 'merge_pull_request',
            repoid=pull_request.target_repo.repo_name,
            pullrequestid=pull_request.pull_request_id,
            userid=TEST_USER_ADMIN_LOGIN)
        response = api_call(self.app, params)

        expected = 'userid is not the same as your user'
        assert_error(id_, expected, given=response.body)
