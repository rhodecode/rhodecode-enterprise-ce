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
import urlobject
from pylons import url

from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok)

pytestmark = pytest.mark.backends("git", "hg")


@pytest.mark.usefixtures("testuser_api", "app")
class TestGetPullRequest(object):

    def test_api_get_pull_request(self, pr_util):
        pull_request = pr_util.create_pull_request(mergeable=True)
        id_, params = build_data(
            self.apikey, 'get_pull_request',
            repoid=pull_request.target_repo.repo_name,
            pullrequestid=pull_request.pull_request_id)

        response = api_call(self.app, params)

        assert response.status == '200 OK'

        url_obj = urlobject.URLObject(
            url(
                'pullrequest_show',
                repo_name=pull_request.target_repo.repo_name,
                pull_request_id=pull_request.pull_request_id, qualified=True))
        pr_url = unicode(
            url_obj.with_netloc('test.example.com:80'))
        source_url = unicode(
            pull_request.source_repo.clone_url()
                .with_netloc('test.example.com:80'))
        target_url = unicode(
            pull_request.target_repo.clone_url()
                .with_netloc('test.example.com:80'))
        expected = {
            'pull_request_id': pull_request.pull_request_id,
            'url': pr_url,
            'title': pull_request.title,
            'description': pull_request.description,
            'status': pull_request.status,
            'created_on': pull_request.created_on,
            'updated_on': pull_request.updated_on,
            'commit_ids': pull_request.revisions,
            'review_status': pull_request.calculated_review_status(),
            'mergeable': {
                'status': True,
                'message': 'This pull request can be automatically merged.',
            },
            'source': {
                'clone_url': source_url,
                'repository': pull_request.source_repo.repo_name,
                'reference': {
                    'name': pull_request.source_ref_parts.name,
                    'type': pull_request.source_ref_parts.type,
                    'commit_id': pull_request.source_ref_parts.commit_id,
                },
            },
            'target': {
                'clone_url': target_url,
                'repository': pull_request.target_repo.repo_name,
                'reference': {
                    'name': pull_request.target_ref_parts.name,
                    'type': pull_request.target_ref_parts.type,
                    'commit_id': pull_request.target_ref_parts.commit_id,
                },
            },
            'author': pull_request.author.get_api_data(include_secrets=False,
                                                       details='basic'),
            'reviewers': [
                {
                    'user': reviewer.get_api_data(include_secrets=False,
                                                  details='basic'),
                    'review_status': st[0][1].status if st else 'not_reviewed',
                }
                for reviewer, st in pull_request.reviewers_statuses()
            ]
        }
        assert_ok(id_, expected, response.body)

    def test_api_get_pull_request_repo_error(self):
        id_, params = build_data(
            self.apikey, 'get_pull_request',
            repoid=666, pullrequestid=1)
        response = api_call(self.app, params)

        expected = 'repository `666` does not exist'
        assert_error(id_, expected, given=response.body)

    def test_api_get_pull_request_pull_request_error(self):
        id_, params = build_data(
            self.apikey, 'get_pull_request',
            repoid=1, pullrequestid=666)
        response = api_call(self.app, params)

        expected = 'pull request `666` does not exist'
        assert_error(id_, expected, given=response.body)
