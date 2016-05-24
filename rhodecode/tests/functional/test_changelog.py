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

import re

import pytest

from rhodecode.controllers.changelog import DEFAULT_CHANGELOG_SIZE
from rhodecode.tests import url, TestController
from rhodecode.tests.utils import AssertResponse


MATCH_HASH = re.compile(r'<span class="commit_hash">r(\d+):[\da-f]+</span>')


class TestChangelogController(TestController):

    def test_index(self, backend):
        self.log_user()
        response = self.app.get(url(controller='changelog', action='index',
                                    repo_name=backend.repo_name))

        first_idx = -1
        last_idx = -DEFAULT_CHANGELOG_SIZE
        self.assert_commit_range_on_page(
            response, first_idx, last_idx, backend)

    @pytest.mark.backends("hg", "git")
    def test_index_filtered_by_branch(self, backend):
        self.log_user()
        self.app.get(
            url(
                controller='changelog',
                action='index',
                repo_name=backend.repo_name,
                branch=backend.default_branch_name),
            status=200)

    @pytest.mark.backends("svn")
    def test_index_filtered_by_branch_svn(self, autologin_user, backend):
        repo = backend['svn-simple-layout']
        response = self.app.get(
            url(
                controller='changelog',
                action='index',
                repo_name=repo.repo_name,
                branch='trunk'),
            status=200)

        self.assert_commits_on_page(
            response, indexes=[15, 12, 7, 3, 2, 1])

    def test_index_filtered_by_wrong_branch(self, backend):
        self.log_user()
        branch = 'wrong-branch-name'
        response = self.app.get(
            url(
                controller='changelog',
                action='index',
                repo_name=backend.repo_name,
                branch=branch),
            status=302)
        expected_url = '/{repo}/changelog/{branch}'.format(
            repo=backend.repo_name, branch=branch)
        assert expected_url in response.location
        response = response.follow()
        expected_warning = 'Branch {} is not found.'.format(branch)
        assert_response = AssertResponse(response)
        assert_response.element_contains('.alert-warning', expected_warning)

    def assert_commits_on_page(self, response, indexes):
        found_indexes = [int(idx) for idx in MATCH_HASH.findall(response.body)]
        assert found_indexes == indexes

    @pytest.mark.xfail_backends("svn", reason="Depends on branch support")
    def test_index_filtered_by_branch_with_merges(
            self, autologin_user, backend):

        # Note: The changelog of branch "b" does not contain the commit "a1"
        # although this is a parent of commit "b1". And branch "b" has commits
        # which have a smaller index than commit "a1".
        commits = [
            {'message': 'a'},
            {'message': 'b', 'branch': 'b'},
            {'message': 'a1', 'parents': ['a']},
            {'message': 'b1', 'branch': 'b', 'parents': ['b', 'a1']},
        ]
        backend.create_repo(commits)

        self.app.get(
            url('changelog_home',
                controller='changelog',
                action='index',
                repo_name=backend.repo_name,
                branch='b'),
            status=200)

    @pytest.mark.backends("hg")
    def test_index_closed_branches(self, autologin_user, backend):
        repo = backend['closed_branch']
        response = self.app.get(
            url(
                controller='changelog',
                action='index',
                repo_name=repo.repo_name,
                branch='experimental'),
            status=200)

        self.assert_commits_on_page(
            response, indexes=[3, 1])

    def test_index_pagination(self, backend):
        self.log_user()
        # pagination, walk up to page 6
        changelog_url = url(
            controller='changelog', action='index',
            repo_name=backend.repo_name)
        for page in range(1, 7):
            response = self.app.get(changelog_url, {'page': page})

        first_idx = -DEFAULT_CHANGELOG_SIZE * (page - 1) - 1
        last_idx = -DEFAULT_CHANGELOG_SIZE * page
        self.assert_commit_range_on_page(response, first_idx, last_idx, backend)

    def assert_commit_range_on_page(
            self, response, first_idx, last_idx, backend):
        input_template = (
            """<input class="commit-range" id="%(raw_id)s" """
            """name="%(raw_id)s" type="checkbox" value="1" />"""
        )
        commit_span_template = """<span class="commit_hash">r%s:%s</span>"""
        repo = backend.repo

        first_commit_on_page = repo.get_commit(commit_idx=first_idx)
        response.mustcontain(
            input_template % {'raw_id': first_commit_on_page.raw_id})
        response.mustcontain(commit_span_template % (
            first_commit_on_page.idx, first_commit_on_page.short_id)
        )

        last_commit_on_page = repo.get_commit(commit_idx=last_idx)
        response.mustcontain(
            input_template % {'raw_id': last_commit_on_page.raw_id})
        response.mustcontain(commit_span_template % (
            last_commit_on_page.idx, last_commit_on_page.short_id)
        )

        first_commit_of_next_page = repo.get_commit(commit_idx=last_idx - 1)
        first_span_of_next_page = commit_span_template % (
            first_commit_of_next_page.idx, first_commit_of_next_page.short_id)
        assert first_span_of_next_page not in response

    def test_index_with_filenode(self, backend):
        self.log_user()
        response = self.app.get(url(
            controller='changelog', action='index', revision='tip',
            f_path='/vcs/exceptions.py', repo_name=backend.repo_name))

        # history commits messages
        response.mustcontain('Added exceptions module, this time for real')
        response.mustcontain('Added not implemented hg backend test case')
        response.mustcontain('Added BaseChangeset class')

    def test_index_with_filenode_that_is_dirnode(self, backend):
        self.log_user()
        response = self.app.get(url(controller='changelog', action='index',
                                    revision='tip', f_path='/tests',
                                    repo_name=backend.repo_name))
        assert response.status == '302 Found'

    def test_index_with_filenode_not_existing(self, backend):
        self.log_user()
        response = self.app.get(url(controller='changelog', action='index',
                                    revision='tip', f_path='/wrong_path',
                                    repo_name=backend.repo_name))
        assert response.status == '302 Found'
