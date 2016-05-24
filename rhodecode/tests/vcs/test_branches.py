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

import datetime

import pytest

from rhodecode.lib.vcs.nodes import FileNode
from rhodecode.tests.vcs.base import BackendTestMixin


class TestBranches(BackendTestMixin):

    @classmethod
    def _get_commits(cls):
        commits = [
            {
                'message': 'Initial commit',
                'author': 'Joe Doe <joe.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 20),
                'added': [
                    FileNode('foobar', content='Foobar'),
                    FileNode('foobar2', content='Foobar II'),
                    FileNode('foo/bar/baz', content='baz here!'),
                ],
            },
            {
                'message': 'Changes...',
                'author': 'Jane Doe <jane.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 21),
                'added': [
                    FileNode('some/new.txt', content='news...'),
                ],
                'changed': [
                    FileNode('foobar', 'Foobar I'),
                ],
                'removed': [],
            },
        ]
        return commits

    def test_empty_repository_has_no_branches(self, vcsbackend):
        empty_repo = vcsbackend.create_repo()
        assert empty_repo.branches == {}

    def test_branches_all(self, vcsbackend):
        branch_count = {
            'git': 1,
            'hg': 1,
            'svn': 0,
        }
        assert len(self.repo.branches_all) == branch_count[vcsbackend.alias]

    def test_closed_branches(self):
        assert len(self.repo.branches_closed) == 0

    def test_simple(self):
        tip = self.repo.get_commit()
        assert tip.date == datetime.datetime(2010, 1, 1, 21)

    @pytest.mark.backends("git", "hg")
    def test_new_branch(self):
        # This check must not be removed to ensure the 'branches' LazyProperty
        # gets hit *before* the new 'foobar' branch got created:
        assert 'foobar' not in self.repo.branches
        self.imc.add(FileNode(
            'docs/index.txt',
            content='Documentation\n'))
        foobar_tip = self.imc.commit(
            message=u'New branch: foobar',
            author=u'joe',
            branch='foobar',
        )
        assert 'foobar' in self.repo.branches
        assert foobar_tip.branch == 'foobar'

    @pytest.mark.backends("git", "hg")
    def test_new_head(self):
        tip = self.repo.get_commit()
        self.imc.add(FileNode(
            'docs/index.txt',
            content='Documentation\n'))
        foobar_tip = self.imc.commit(
            message=u'New branch: foobar',
            author=u'joe',
            branch='foobar',
            parents=[tip],
        )
        self.imc.change(FileNode(
            'docs/index.txt',
            content='Documentation\nand more...\n'))
        newtip = self.imc.commit(
            message=u'At default branch',
            author=u'joe',
            branch=foobar_tip.branch,
            parents=[foobar_tip],
        )

        newest_tip = self.imc.commit(
            message=u'Merged with %s' % foobar_tip.raw_id,
            author=u'joe',
            branch=self.backend_class.DEFAULT_BRANCH_NAME,
            parents=[newtip, foobar_tip],
        )

        assert newest_tip.branch == \
            self.backend_class.DEFAULT_BRANCH_NAME

    @pytest.mark.backends("git", "hg")
    def test_branch_with_slash_in_name(self):
        self.imc.add(FileNode('extrafile', content='Some data\n'))
        self.imc.commit(
            u'Branch with a slash!', author=u'joe',
            branch='issue/123')
        assert 'issue/123' in self.repo.branches

    @pytest.mark.backends("git", "hg")
    def test_branch_with_slash_in_name_and_similar_without(self):
        self.imc.add(FileNode('extrafile', content='Some data\n'))
        self.imc.commit(
            u'Branch with a slash!', author=u'joe',
            branch='issue/123')
        self.imc.add(FileNode('extrafile II', content='Some data\n'))
        self.imc.commit(
            u'Branch without a slash...', author=u'joe',
            branch='123')
        assert 'issue/123' in self.repo.branches
        assert '123' in self.repo.branches


class TestSvnBranches:

    def test_empty_repository_has_no_tags_and_branches(self, vcsbackend_svn):
        empty_repo = vcsbackend_svn.create_repo()
        assert empty_repo.branches == {}
        assert empty_repo.tags == {}

    def test_missing_structure_has_no_tags_and_branches(self, vcsbackend_svn):
        repo = vcsbackend_svn.create_repo(number_of_commits=1)
        assert repo.branches == {}
        assert repo.tags == {}

    def test_discovers_ordered_branches(self, vcsbackend_svn):
        repo = vcsbackend_svn['svn-simple-layout']
        expected_branches = [
            'branches/add-docs',
            'branches/argparse',
            'trunk',
        ]
        assert repo.branches.keys() == expected_branches

    def test_discovers_ordered_tags(self, vcsbackend_svn):
        repo = vcsbackend_svn['svn-simple-layout']
        expected_tags = [
            'tags/v0.1', 'tags/v0.2', 'tags/v0.3', 'tags/v0.5']
        assert repo.tags.keys() == expected_tags
