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

from rhodecode.tests import url
from rhodecode.tests.functional.test_compare import ComparePage


@pytest.mark.usefixtures("autologin_user", "app")
class TestCompareController:

    @pytest.mark.xfail_backends("svn", msg="Depends on branch and tag support")
    def test_compare_tag(self, backend):
        tag1 = 'v0.1.2'
        tag2 = 'v0.1.3'
        response = self.app.get(
            url(
                'compare_url',
                repo_name=backend.repo_name,
                source_ref_type="tag",
                source_ref=tag1,
                target_ref_type="tag",
                target_ref=tag2),
            status=200)

        response.mustcontain('%s@%s' % (backend.repo_name, tag1))
        response.mustcontain('%s@%s' % (backend.repo_name, tag2))

        # outgoing changesets between tags
        commit_indexes = {
            'git': [113] + range(115, 121),
            'hg': [112] + range(115, 121),
        }
        repo = backend.repo
        commits = (repo.get_commit(commit_idx=idx)
                   for idx in commit_indexes[backend.alias])
        compare_page = ComparePage(response)
        compare_page.contains_change_summary(11, 94, 64)
        compare_page.contains_commits(commits)

        # files diff
        compare_page.contains_file_links_and_anchors([
            ('docs/api/utils/index.rst', 'a_c--1c5cf9e91c12'),
            ('test_and_report.sh', 'a_c--e3305437df55'),
            ('.hgignore', 'a_c--c8e92ef85cd1'),
            ('.hgtags', 'a_c--6e08b694d687'),
            ('docs/api/index.rst', 'a_c--2c14b00f3393'),
            ('vcs/__init__.py', 'a_c--430ccbc82bdf'),
            ('vcs/backends/hg.py', 'a_c--9c390eb52cd6'),
            ('vcs/utils/__init__.py', 'a_c--ebb592c595c0'),
            ('vcs/utils/annotate.py', 'a_c--7abc741b5052'),
            ('vcs/utils/diffs.py', 'a_c--2ef0ef106c56'),
            ('vcs/utils/lazy.py', 'a_c--3150cb87d4b7'),
        ])

    @pytest.mark.xfail_backends("svn", msg="Depends on branch and tag support")
    def test_compare_tag_branch(self, backend):
        revisions = {
            'hg': {
                'tag': 'v0.2.0',
                'branch': 'default',
                'response': (147, 5701, 10177)
            },
            'git': {
                'tag': 'v0.2.2',
                'branch': 'master',
                'response': (71, 2269, 3416)
            },
        }

        # Backend specific data, depends on the test repository for
        # functional tests.
        data = revisions[backend.alias]

        response = self.app.get(url(
            'compare_url',
            repo_name=backend.repo_name,
            source_ref_type='branch',
            source_ref=data['branch'],
            target_ref_type="tag",
            target_ref=data['tag'],
            ))

        response.mustcontain('%s@%s' % (backend.repo_name, data['branch']))
        response.mustcontain('%s@%s' % (backend.repo_name, data['tag']))
        compare_page = ComparePage(response)
        compare_page.contains_change_summary(*data['response'])

    def test_index_branch(self, backend):
        head_id = backend.default_head_id
        response = self.app.get(url(
            'compare_url',
            repo_name=backend.repo_name,
            source_ref_type="branch",
            source_ref=head_id,
            target_ref_type="branch",
            target_ref=head_id,
            ))

        response.mustcontain('%s@%s' % (backend.repo_name, head_id))

        # branches are equal
        response.mustcontain('<p class="empty_data">No files</p>')
        response.mustcontain('<p class="empty_data">No Commits</p>')

    def test_compare_commits(self, backend):
        repo = backend.repo
        commit1 = repo.get_commit(commit_idx=0)
        commit2 = repo.get_commit(commit_idx=1)

        response = self.app.get(url(
            'compare_url',
            repo_name=backend.repo_name,
            source_ref_type="rev",
            source_ref=commit1.raw_id,
            target_ref_type="rev",
            target_ref=commit2.raw_id,
            ))
        response.mustcontain('%s@%s' % (backend.repo_name, commit1.raw_id))
        response.mustcontain('%s@%s' % (backend.repo_name, commit2.raw_id))
        compare_page = ComparePage(response)

        # files
        compare_page.contains_change_summary(1, 7, 0)

        # outgoing commits between those commits
        compare_page.contains_commits([commit2])
        compare_page.contains_file_links_and_anchors([
            ('.hgignore', 'a_c--c8e92ef85cd1'),
        ])
