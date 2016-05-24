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
import time

import pytest

from rhodecode.lib.vcs.backends.base import (
    CollectionGenerator, FILEMODE_DEFAULT, EmptyCommit)
from rhodecode.lib.vcs.exceptions import (
    BranchDoesNotExistError, CommitDoesNotExistError,
    RepositoryError, EmptyRepositoryError)
from rhodecode.lib.vcs.nodes import (
    FileNode, AddedFileNodesGenerator,
    ChangedFileNodesGenerator, RemovedFileNodesGenerator)
from rhodecode.tests import get_new_dir
from rhodecode.tests.vcs.base import BackendTestMixin


class TestBaseChangeset:

    def test_is_deprecated(self):
        from rhodecode.lib.vcs.backends.base import BaseChangeset
        pytest.deprecated_call(BaseChangeset)


class TestEmptyCommit:

    def test_branch_without_alias_returns_none(self):
        commit = EmptyCommit()
        assert commit.branch is None


class TestCommitsInNonEmptyRepo(BackendTestMixin):
    recreate_repo_per_test = True

    @classmethod
    def _get_commits(cls):
        start_date = datetime.datetime(2010, 1, 1, 20)
        for x in xrange(5):
            yield {
                'message': 'Commit %d' % x,
                'author': 'Joe Doe <joe.doe@example.com>',
                'date': start_date + datetime.timedelta(hours=12 * x),
                'added': [
                    FileNode('file_%d.txt' % x, content='Foobar %d' % x),
                ],
            }

    def test_walk_returns_empty_list_in_case_of_file(self):
        result = list(self.tip.walk('file_0.txt'))
        assert result == []

    @pytest.mark.backends("git", "hg")
    def test_new_branch(self):
        self.imc.add(FileNode('docs/index.txt',
                     content='Documentation\n'))
        foobar_tip = self.imc.commit(
            message=u'New branch: foobar',
            author=u'joe',
            branch='foobar',
        )
        assert 'foobar' in self.repo.branches
        assert foobar_tip.branch == 'foobar'
        # 'foobar' should be the only branch that contains the new commit
        branch = self.repo.branches.values()
        assert branch[0] != branch[1]

    @pytest.mark.backends("git", "hg")
    def test_new_head_in_default_branch(self):
        tip = self.repo.get_commit()
        self.imc.add(FileNode('docs/index.txt',
                     content='Documentation\n'))
        foobar_tip = self.imc.commit(
            message=u'New branch: foobar',
            author=u'joe',
            branch='foobar',
            parents=[tip],
        )
        self.imc.change(FileNode('docs/index.txt',
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

        assert newest_tip.branch == self.backend_class.DEFAULT_BRANCH_NAME

    @pytest.mark.backends("git", "hg")
    def test_get_commits_respects_branch_name(self):
        """
        * e1930d0 (HEAD, master) Back in default branch
        | * e1930d0 (docs) New Branch: docs2
        | * dcc14fa New branch: docs
        |/
        * e63c41a Initial commit
        ...
        * 624d3db Commit 0

        :return:
        """
        DEFAULT_BRANCH = self.repo.DEFAULT_BRANCH_NAME
        TEST_BRANCH = 'docs'
        org_tip = self.repo.get_commit()

        self.imc.add(FileNode('readme.txt', content='Document\n'))
        initial = self.imc.commit(
            message=u'Initial commit',
            author=u'joe',
            parents=[org_tip],
            branch=DEFAULT_BRANCH,)

        self.imc.add(FileNode('newdoc.txt', content='foobar\n'))
        docs_branch_commit1 = self.imc.commit(
            message=u'New branch: docs',
            author=u'joe',
            parents=[initial],
            branch=TEST_BRANCH,)

        self.imc.add(FileNode('newdoc2.txt', content='foobar2\n'))
        docs_branch_commit2 = self.imc.commit(
            message=u'New branch: docs2',
            author=u'joe',
            parents=[docs_branch_commit1],
            branch=TEST_BRANCH,)

        self.imc.add(FileNode('newfile', content='hello world\n'))
        self.imc.commit(
            message=u'Back in default branch',
            author=u'joe',
            parents=[initial],
            branch=DEFAULT_BRANCH,)

        default_branch_commits = self.repo.get_commits(
            branch_name=DEFAULT_BRANCH)
        assert docs_branch_commit1 not in list(default_branch_commits)
        assert docs_branch_commit2 not in list(default_branch_commits)

        docs_branch_commits = self.repo.get_commits(
            start_id=self.repo.commit_ids[0], end_id=self.repo.commit_ids[-1],
            branch_name=TEST_BRANCH)
        assert docs_branch_commit1 in list(docs_branch_commits)
        assert docs_branch_commit2 in list(docs_branch_commits)

    @pytest.mark.backends("svn")
    def test_get_commits_respects_branch_name_svn(self, vcsbackend_svn):
        repo = vcsbackend_svn['svn-simple-layout']
        commits = repo.get_commits(branch_name='trunk')
        commit_indexes = [c.idx for c in commits]
        assert commit_indexes == [1, 2, 3, 7, 12, 15]

    def test_get_commit_by_branch(self):
        for branch, commit_id in self.repo.branches.iteritems():
            assert commit_id == self.repo.get_commit(branch).raw_id

    def test_get_commit_by_tag(self):
        for tag, commit_id in self.repo.tags.iteritems():
            assert commit_id == self.repo.get_commit(tag).raw_id

    def test_get_commit_parents(self):
        repo = self.repo
        for test_idx in [1, 2, 3]:
            commit = repo.get_commit(commit_idx=test_idx - 1)
            assert [commit] == repo.get_commit(commit_idx=test_idx).parents

    def test_get_commit_children(self):
        repo = self.repo
        for test_idx in [1, 2, 3]:
            commit = repo.get_commit(commit_idx=test_idx + 1)
            assert [commit] == repo.get_commit(commit_idx=test_idx).children


class TestCommits(BackendTestMixin):
    recreate_repo_per_test = False

    @classmethod
    def _get_commits(cls):
        start_date = datetime.datetime(2010, 1, 1, 20)
        for x in xrange(5):
            yield {
                'message': u'Commit %d' % x,
                'author': u'Joe Doe <joe.doe@example.com>',
                'date': start_date + datetime.timedelta(hours=12 * x),
                'added': [
                    FileNode('file_%d.txt' % x, content='Foobar %d' % x),
                ],
            }

    def test_simple(self):
        tip = self.repo.get_commit()
        assert tip.date, datetime.datetime(2010, 1, 3 == 20)

    def test_simple_serialized_commit(self):
        tip = self.repo.get_commit()
        # json.dumps(tip) uses .__json__() method
        data = tip.__json__()
        assert 'branch' in data
        assert data['revision']

    def test_retrieve_tip(self):
        tip = self.repo.get_commit('tip')
        assert tip == self.repo.get_commit()

    def test_invalid(self):
        with pytest.raises(CommitDoesNotExistError):
            self.repo.get_commit(commit_idx=123456789)

    def test_idx(self):
        commit = self.repo[0]
        assert commit.idx == 0

    def test_negative_idx(self):
        commit = self.repo.get_commit(commit_idx=-1)
        assert commit.idx >= 0

    def test_revision_is_deprecated(self):
        def get_revision(commit):
            return commit.revision

        commit = self.repo[0]
        pytest.deprecated_call(get_revision, commit)

    def test_size(self):
        tip = self.repo.get_commit()
        size = 5 * len('Foobar N')  # Size of 5 files
        assert tip.size == size

    def test_size_at_commit(self):
        tip = self.repo.get_commit()
        size = 5 * len('Foobar N')  # Size of 5 files
        assert self.repo.size_at_commit(tip.raw_id) == size

    def test_size_at_first_commit(self):
        commit = self.repo[0]
        size = len('Foobar N')  # Size of 1 file
        assert self.repo.size_at_commit(commit.raw_id) == size

    def test_author(self):
        tip = self.repo.get_commit()
        assert_text_equal(tip.author, u'Joe Doe <joe.doe@example.com>')

    def test_author_name(self):
        tip = self.repo.get_commit()
        assert_text_equal(tip.author_name, u'Joe Doe')

    def test_author_email(self):
        tip = self.repo.get_commit()
        assert_text_equal(tip.author_email, u'joe.doe@example.com')

    def test_message(self):
        tip = self.repo.get_commit()
        assert_text_equal(tip.message, u'Commit 4')

    def test_diff(self):
        tip = self.repo.get_commit()
        diff = tip.diff()
        assert "+Foobar 4" in diff.raw

    def test_prev(self):
        tip = self.repo.get_commit()
        prev_commit = tip.prev()
        assert prev_commit.message == 'Commit 3'

    def test_prev_raises_on_first_commit(self):
        commit = self.repo.get_commit(commit_idx=0)
        with pytest.raises(CommitDoesNotExistError):
            commit.prev()

    def test_prev_works_on_second_commit_issue_183(self):
        commit = self.repo.get_commit(commit_idx=1)
        prev_commit = commit.prev()
        assert prev_commit.idx == 0

    def test_next(self):
        commit = self.repo.get_commit(commit_idx=2)
        next_commit = commit.next()
        assert next_commit.message == 'Commit 3'

    def test_next_raises_on_tip(self):
        commit = self.repo.get_commit()
        with pytest.raises(CommitDoesNotExistError):
            commit.next()

    def test_get_file_commit(self):
        commit = self.repo.get_commit()
        commit.get_file_commit('file_4.txt')
        assert commit.message == 'Commit 4'

    def test_get_filenodes_generator(self):
        tip = self.repo.get_commit()
        filepaths = [node.path for node in tip.get_filenodes_generator()]
        assert filepaths == ['file_%d.txt' % x for x in xrange(5)]

    def test_get_file_annotate(self):
        file_added_commit = self.repo.get_commit(commit_idx=3)
        annotations = list(file_added_commit.get_file_annotate('file_3.txt'))
        line_no, commit_id, commit_loader, line = annotations[0]
        assert line_no == 1
        assert commit_id == file_added_commit.raw_id
        assert commit_loader() == file_added_commit
        if self.repo.alias == 'git':
            pytest.xfail("TODO: Git returns wrong value in line")
        assert line == 'Foobar 3'

    def test_get_file_annotate_does_not_exist(self):
        file_added_commit = self.repo.get_commit(commit_idx=2)
        # TODO: Should use a specific exception class here?
        with pytest.raises(Exception):
            list(file_added_commit.get_file_annotate('file_3.txt'))

    def test_get_file_annotate_tip(self):
        tip = self.repo.get_commit()
        commit = self.repo.get_commit(commit_idx=3)
        expected_values = list(commit.get_file_annotate('file_3.txt'))
        annotations = list(tip.get_file_annotate('file_3.txt'))

        # Note: Skip index 2 because the loader function is not the same
        for idx in (0, 1, 3):
            assert annotations[0][idx] == expected_values[0][idx]

    def test_get_commits_is_ordered_by_date(self):
        commits = self.repo.get_commits()
        assert isinstance(commits, CollectionGenerator)
        assert len(commits) == 0 or len(commits) != 0
        commits = list(commits)
        ordered_by_date = sorted(commits, key=lambda commit: commit.date)
        assert commits == ordered_by_date

    def test_get_commits_respects_start(self):
        second_id = self.repo.commit_ids[1]
        commits = self.repo.get_commits(start_id=second_id)
        assert isinstance(commits, CollectionGenerator)
        commits = list(commits)
        assert len(commits) == 4

    def test_get_commits_includes_start_commit(self):
        second_id = self.repo.commit_ids[1]
        commits = self.repo.get_commits(start_id=second_id)
        assert isinstance(commits, CollectionGenerator)
        commits = list(commits)
        assert commits[0].raw_id == second_id

    def test_get_commits_respects_end(self):
        second_id = self.repo.commit_ids[1]
        commits = self.repo.get_commits(end_id=second_id)
        assert isinstance(commits, CollectionGenerator)
        commits = list(commits)
        assert commits[-1].raw_id == second_id
        assert len(commits) == 2

    def test_get_commits_respects_both_start_and_end(self):
        second_id = self.repo.commit_ids[1]
        third_id = self.repo.commit_ids[2]
        commits = self.repo.get_commits(start_id=second_id, end_id=third_id)
        assert isinstance(commits, CollectionGenerator)
        commits = list(commits)
        assert len(commits) == 2

    def test_get_commits_on_empty_repo_raises_EmptyRepository_error(self):
        repo_path = get_new_dir(str(time.time()))
        repo = self.Backend(repo_path, create=True)

        with pytest.raises(EmptyRepositoryError):
            list(repo.get_commits(start_id='foobar'))

    def test_get_commits_includes_end_commit(self):
        second_id = self.repo.commit_ids[1]
        commits = self.repo.get_commits(end_id=second_id)
        assert isinstance(commits, CollectionGenerator)
        assert len(commits) == 2
        commits = list(commits)
        assert commits[-1].raw_id == second_id

    def test_get_commits_respects_start_date(self):
        start_date = datetime.datetime(2010, 1, 2)
        commits = self.repo.get_commits(start_date=start_date)
        assert isinstance(commits, CollectionGenerator)
        # Should be 4 commits after 2010-01-02 00:00:00
        assert len(commits) == 4
        for c in commits:
            assert c.date >= start_date

    def test_get_commits_respects_start_date_and_end_date(self):
        start_date = datetime.datetime(2010, 1, 2)
        end_date = datetime.datetime(2010, 1, 3)
        commits = self.repo.get_commits(start_date=start_date,
                                        end_date=end_date)
        assert isinstance(commits, CollectionGenerator)
        assert len(commits) == 2
        for c in commits:
            assert c.date >= start_date
            assert c.date <= end_date

    def test_get_commits_respects_end_date(self):
        end_date = datetime.datetime(2010, 1, 2)
        commits = self.repo.get_commits(end_date=end_date)
        assert isinstance(commits, CollectionGenerator)
        assert len(commits) == 1
        for c in commits:
            assert c.date <= end_date

    def test_get_commits_respects_reverse(self):
        commits = self.repo.get_commits()  # no longer reverse support
        assert isinstance(commits, CollectionGenerator)
        assert len(commits) == 5
        commit_ids = reversed([c.raw_id for c in commits])
        assert list(commit_ids) == list(reversed(self.repo.commit_ids))

    def test_get_commits_slice_generator(self):
        commits = self.repo.get_commits(
            branch_name=self.repo.DEFAULT_BRANCH_NAME)
        assert isinstance(commits, CollectionGenerator)
        commit_slice = list(commits[1:3])
        assert len(commit_slice) == 2

    def test_get_commits_raise_commitdoesnotexist_for_wrong_start(self):
        with pytest.raises(CommitDoesNotExistError):
            list(self.repo.get_commits(start_id='foobar'))

    def test_get_commits_raise_commitdoesnotexist_for_wrong_end(self):
        with pytest.raises(CommitDoesNotExistError):
            list(self.repo.get_commits(end_id='foobar'))

    def test_get_commits_raise_branchdoesnotexist_for_wrong_branch_name(self):
        with pytest.raises(BranchDoesNotExistError):
            list(self.repo.get_commits(branch_name='foobar'))

    def test_get_commits_raise_repositoryerror_for_wrong_start_end(self):
        start_id = self.repo.commit_ids[-1]
        end_id = self.repo.commit_ids[0]
        with pytest.raises(RepositoryError):
            list(self.repo.get_commits(start_id=start_id, end_id=end_id))

    def test_get_commits_raises_for_numerical_ids(self):
        with pytest.raises(TypeError):
            self.repo.get_commits(start_id=1, end_id=2)


@pytest.mark.parametrize("filename, expected", [
    ("README.rst", False),
    ("README", True),
])
def test_commit_is_link(vcsbackend, filename, expected):
    commit = vcsbackend.repo.get_commit()
    link_status = commit.is_link(filename)
    assert link_status is expected


class TestCommitsChanges(BackendTestMixin):
    recreate_repo_per_test = False

    @classmethod
    def _get_commits(cls):
        return [
            {
                'message': u'Initial',
                'author': u'Joe Doe <joe.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 20),
                'added': [
                    FileNode('foo/bar', content='foo'),
                    FileNode('foo/bał', content='foo'),
                    FileNode('foobar', content='foo'),
                    FileNode('qwe', content='foo'),
                ],
            },
            {
                'message': u'Massive changes',
                'author': u'Joe Doe <joe.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 22),
                'added': [FileNode('fallout', content='War never changes')],
                'changed': [
                    FileNode('foo/bar', content='baz'),
                    FileNode('foobar', content='baz'),
                ],
                'removed': [FileNode('qwe')],
            },
        ]

    def test_initial_commit(self):
        commit = self.repo.get_commit(commit_idx=0)
        assert set(commit.added) == set([
            commit.get_node('foo/bar'),
            commit.get_node('foo/bał'),
            commit.get_node('foobar'),
            commit.get_node('qwe'),
        ])
        assert set(commit.changed) == set()
        assert set(commit.removed) == set()
        assert set(commit.affected_files) == set(
            ['foo/bar', 'foo/bał', 'foobar', 'qwe'])
        assert commit.date == datetime.datetime(2010, 1, 1, 20, 0)

    def test_head_added(self):
        commit = self.repo.get_commit()
        assert isinstance(commit.added, AddedFileNodesGenerator)
        assert set(commit.added) == set([commit.get_node('fallout')])
        assert isinstance(commit.changed, ChangedFileNodesGenerator)
        assert set(commit.changed) == set([
            commit.get_node('foo/bar'),
            commit.get_node('foobar'),
        ])
        assert isinstance(commit.removed, RemovedFileNodesGenerator)
        assert len(commit.removed) == 1
        assert list(commit.removed)[0].path == 'qwe'

    def test_get_filemode(self):
        commit = self.repo.get_commit()
        assert FILEMODE_DEFAULT == commit.get_file_mode('foo/bar')

    def test_get_filemode_non_ascii(self):
        commit = self.repo.get_commit()
        assert FILEMODE_DEFAULT == commit.get_file_mode('foo/bał')
        assert FILEMODE_DEFAULT == commit.get_file_mode(u'foo/bał')

    def test_get_file_history(self):
        commit = self.repo.get_commit()
        history = commit.get_file_history('foo/bar')
        assert len(history) == 2

    def test_get_file_history_with_limit(self):
        commit = self.repo.get_commit()
        history = commit.get_file_history('foo/bar', limit=1)
        assert len(history) == 1

    def test_get_file_history_first_commit(self):
        commit = self.repo[0]
        history = commit.get_file_history('foo/bar')
        assert len(history) == 1


def assert_text_equal(expected, given):
    assert expected == given
    assert isinstance(expected, unicode)
    assert isinstance(given, unicode)
