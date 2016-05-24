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

import os

import mock
import pytest
from whoosh import query

from rhodecode.tests import (
    TestController, url, SkipTest, HG_REPO,
    TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
from rhodecode.tests.utils import AssertResponse


class TestSearchController(TestController):

    def test_index(self):
        self.log_user()
        response = self.app.get(url(controller='search', action='index'))
        assert_response = AssertResponse(response)
        assert_response.one_element_exists('input#q')

    def test_search_files_empty_search(self):
        if os.path.isdir(self.index_location):
            raise SkipTest('skipped due to existing index')
        else:
            self.log_user()
            response = self.app.get(url(controller='search', action='index'),
                                    {'q': HG_REPO})
            response.mustcontain('There is no index to search in. '
                                 'Please run whoosh indexer')

    def test_search_validation(self):
        self.log_user()
        response = self.app.get(
            url(controller='search', action='index'), {'q': query,
                                                       'type': 'content',
                                                       'page_limit': 1000})

        response.mustcontain(
            'page_limit - 1000 is greater than maximum value 500')

    @pytest.mark.parametrize("query, expected_hits, expected_paths", [
        ('todo', 23, [
            'vcs/backends/hg/inmemory.py',
            'vcs/tests/test_git.py']),
        ('extension:rst installation', 6, [
            'docs/index.rst',
            'docs/installation.rst']),
        ('def repo', 87, [
            'vcs/tests/test_git.py',
            'vcs/tests/test_changesets.py']),
        ('repository:%s def test' % HG_REPO, 18, [
            'vcs/tests/test_git.py',
            'vcs/tests/test_changesets.py']),
        ('"def main"', 9, [
            'vcs/__init__.py',
            'vcs/tests/__init__.py',
            'vcs/utils/progressbar.py']),
        ('owner:test_admin', 358, [
            'vcs/tests/base.py',
            'MANIFEST.in',
            'vcs/utils/termcolors.py',
            'docs/theme/ADC/static/documentation.png']),
        ('owner:test_admin def main', 72, [
            'vcs/__init__.py',
            'vcs/tests/test_utils_filesize.py',
            'vcs/tests/test_cli.py']),
        ('owner:michał test', 0, []),
    ])
    def test_search_files(self, query, expected_hits, expected_paths):
        self.log_user()
        response = self.app.get(
            url(controller='search', action='index'), {'q': query,
                                                       'type': 'content',
                                                       'page_limit': 500})

        response.mustcontain('%s results' % expected_hits)
        for path in expected_paths:
            response.mustcontain(path)

    @pytest.mark.parametrize("query, expected_hits, expected_commits", [
        ('bother to ask where to fetch repo during tests', 3, [
            ('hg', 'a00c1b6f5d7a6ae678fd553a8b81d92367f7ecf1'),
            ('git', 'c6eb379775c578a95dad8ddab53f963b80894850'),
            ('svn', '98')]),
        ('michał', 0, []),
        ('changed:tests/utils.py', 36, [
            ('hg', 'a00c1b6f5d7a6ae678fd553a8b81d92367f7ecf1')]),
        ('changed:vcs/utils/archivers.py', 11, [
            ('hg', '25213a5fbb048dff8ba65d21e466a835536e5b70'),
            ('hg', '47aedd538bf616eedcb0e7d630ea476df0e159c7'),
            ('hg', 'f5d23247fad4856a1dabd5838afade1e0eed24fb'),
            ('hg', '04ad456aefd6461aea24f90b63954b6b1ce07b3e'),
            ('git', 'c994f0de03b2a0aa848a04fc2c0d7e737dba31fc'),
            ('git', 'd1f898326327e20524fe22417c22d71064fe54a1'),
            ('git', 'fe568b4081755c12abf6ba673ba777fc02a415f3'),
            ('git', 'bafe786f0d8c2ff7da5c1dcfcfa577de0b5e92f1')]),
        ('added:README.rst', 3, [
            ('hg', '3803844fdbd3b711175fc3da9bdacfcd6d29a6fb'),
            ('git', 'ff7ca51e58c505fec0dd2491de52c622bb7a806b'),
            ('svn', '8')]),
        ('changed:lazy.py', 15, [
            ('hg', 'eaa291c5e6ae6126a203059de9854ccf7b5baa12'),
            ('git', '17438a11f72b93f56d0e08e7d1fa79a378578a82'),
            ('svn', '82'),
            ('svn', '262'),
            ('hg', 'f5d23247fad4856a1dabd5838afade1e0eed24fb'),
            ('git', '33fa3223355104431402a888fa77a4e9956feb3e')
            ]),
        ('author:marcin@python-blog.com '
         'commit_id:b986218ba1c9b0d6a259fac9b050b1724ed8e545', 1, [
             ('hg', 'b986218ba1c9b0d6a259fac9b050b1724ed8e545')]),
    ])
    def test_search_commit_messages(
            self, query, expected_hits, expected_commits, enabled_backends):
        self.log_user()
        response = self.app.get(
            url(controller='search', action='index'), {'q': query,
                                                       'type': 'commit',
                                                       'page_limit': 500})

        response.mustcontain('%s results' % expected_hits)
        for backend, commit_id in expected_commits:
            if backend in enabled_backends:
                response.mustcontain(commit_id)

    @pytest.mark.parametrize("query, expected_hits, expected_paths", [
        ('readme.rst', 3, []),
        ('test*', 75, []),
        ('*model*', 1, []),
        ('extension:rst', 48, []),
        ('extension:rst api', 24, []),
    ])
    def test_search_file_paths(self, query, expected_hits, expected_paths):
        self.log_user()
        response = self.app.get(
            url(controller='search', action='index'), {'q': query,
                                                       'type': 'path',
                                                       'page_limit': 500})

        response.mustcontain('%s results' % expected_hits)
        for path in expected_paths:
            response.mustcontain(path)

    def test_search_commit_message_specific_repo(self, backend):
        self.log_user()
        response = self.app.get(
            url(controller='search', action='index',
                repo_name=backend.repo_name),
            {'q': 'bother to ask where to fetch repo during tests',
             'type': 'commit'})

        response.mustcontain('1 results')

    def test_filters_are_not_applied_for_admin_user(self):
        self.log_user()
        with mock.patch('whoosh.searching.Searcher.search') as search_mock:
            self.app.get(
                url(controller='search', action='index'),
                {'q': 'test query', 'type': 'commit'})
        assert search_mock.call_count == 1
        _, kwargs = search_mock.call_args
        assert kwargs['filter'] is None

    def test_filters_are_applied_for_normal_user(self, enabled_backends):
        self.log_user(TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        with mock.patch('whoosh.searching.Searcher.search') as search_mock:
            self.app.get(
                url(controller='search', action='index'),
                {'q': 'test query', 'type': 'commit'})
        assert search_mock.call_count == 1
        _, kwargs = search_mock.call_args
        assert isinstance(kwargs['filter'], query.Or)
        expected_repositories = [
            'vcs_test_{}'.format(b) for b in enabled_backends]
        queried_repositories = [
            name for type_, name in kwargs['filter'].all_terms()]
        for repository in expected_repositories:
            assert repository in queried_repositories
