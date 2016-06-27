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

import rhodecode.lib.vcs.conf.settings
from rhodecode.lib.vcs import backends
from rhodecode.lib.vcs.backends.base import (
    Reference, MergeResponse, MergeFailureReason)
from rhodecode.lib.vcs.backends.hg import MercurialRepository, MercurialCommit
from rhodecode.lib.vcs.exceptions import (
    CommitError, RepositoryError, VCSError, NodeDoesNotExistError,
    CommitDoesNotExistError)
from rhodecode.lib.vcs.nodes import FileNode, NodeKind, NodeState
from rhodecode.tests import TEST_HG_REPO, TEST_HG_REPO_CLONE


pytestmark = pytest.mark.backends("hg")


def repo_path_generator():
    """
    Return a different path to be used for cloning repos.
    """
    i = 0
    while True:
        i += 1
        yield '%s-%d' % (TEST_HG_REPO_CLONE, i)


REPO_PATH_GENERATOR = repo_path_generator()


@pytest.fixture(scope='class', autouse=True)
def repo(request, pylonsapp):
    repo = MercurialRepository(TEST_HG_REPO)
    if request.cls:
        request.cls.repo = repo
    return repo


class TestMercurialRepository:

    # pylint: disable=protected-access

    def get_clone_repo(self):
        """
        Return a clone of the base repo.
        """
        clone_path = next(REPO_PATH_GENERATOR)
        repo_clone = MercurialRepository(
            clone_path, create=True, src_url=self.repo.path)

        return repo_clone

    def get_empty_repo(self):
        """
        Return an empty repo.
        """
        return MercurialRepository(next(REPO_PATH_GENERATOR), create=True)

    def test_wrong_repo_path(self):
        wrong_repo_path = '/tmp/errorrepo'
        with pytest.raises(RepositoryError):
            MercurialRepository(wrong_repo_path)

    def test_unicode_path_repo(self):
        with pytest.raises(VCSError):
            MercurialRepository(u'iShouldFail')

    def test_unicode_commit_id(self):
        with pytest.raises(CommitDoesNotExistError):
            self.repo.get_commit(u'unicode-commit-id')
        with pytest.raises(CommitDoesNotExistError):
            self.repo.get_commit(u'unícøde-spéçial-chäråcter-commit-id')

    def test_unicode_bookmark(self):
        self.repo.bookmark(u'unicode-bookmark')
        self.repo.bookmark(u'unícøde-spéçial-chäråcter-bookmark')

    def test_unicode_branch(self):
        with pytest.raises(KeyError):
            self.repo.branches[u'unicode-branch']
        with pytest.raises(KeyError):
            self.repo.branches[u'unícøde-spéçial-chäråcter-branch']

    def test_repo_clone(self):
        if os.path.exists(TEST_HG_REPO_CLONE):
            self.fail(
                'Cannot test mercurial clone repo as location %s already '
                'exists. You should manually remove it first.'
                % TEST_HG_REPO_CLONE)

        repo = MercurialRepository(TEST_HG_REPO)
        repo_clone = MercurialRepository(TEST_HG_REPO_CLONE,
                                         src_url=TEST_HG_REPO)
        assert len(repo.commit_ids) == len(repo_clone.commit_ids)
        # Checking hashes of commits should be enough
        for commit in repo.get_commits():
            raw_id = commit.raw_id
            assert raw_id == repo_clone.get_commit(raw_id).raw_id

    def test_repo_clone_with_update(self):
        repo = MercurialRepository(TEST_HG_REPO)
        repo_clone = MercurialRepository(
            TEST_HG_REPO_CLONE + '_w_update',
            src_url=TEST_HG_REPO, update_after_clone=True)
        assert len(repo.commit_ids) == len(repo_clone.commit_ids)

        # check if current workdir was updated
        assert os.path.isfile(
            os.path.join(TEST_HG_REPO_CLONE + '_w_update', 'MANIFEST.in'))

    def test_repo_clone_without_update(self):
        repo = MercurialRepository(TEST_HG_REPO)
        repo_clone = MercurialRepository(
            TEST_HG_REPO_CLONE + '_wo_update',
            src_url=TEST_HG_REPO, update_after_clone=False)
        assert len(repo.commit_ids) == len(repo_clone.commit_ids)
        assert not os.path.isfile(
            os.path.join(TEST_HG_REPO_CLONE + '_wo_update', 'MANIFEST.in'))

    def test_commit_ids(self):
        # there are 21 commits at bitbucket now
        # so we can assume they would be available from now on
        subset = set([
            'b986218ba1c9b0d6a259fac9b050b1724ed8e545',
            '3d8f361e72ab303da48d799ff1ac40d5ac37c67e',
            '6cba7170863a2411822803fa77a0a264f1310b35',
            '56349e29c2af3ac913b28bde9a2c6154436e615b',
            '2dda4e345facb0ccff1a191052dd1606dba6781d',
            '6fff84722075f1607a30f436523403845f84cd9e',
            '7d4bc8ec6be56c0f10425afb40b6fc315a4c25e7',
            '3803844fdbd3b711175fc3da9bdacfcd6d29a6fb',
            'dc5d2c0661b61928834a785d3e64a3f80d3aad9c',
            'be90031137367893f1c406e0a8683010fd115b79',
            'db8e58be770518cbb2b1cdfa69146e47cd481481',
            '84478366594b424af694a6c784cb991a16b87c21',
            '17f8e105dddb9f339600389c6dc7175d395a535c',
            '20a662e756499bde3095ffc9bc0643d1def2d0eb',
            '2e319b85e70a707bba0beff866d9f9de032aa4f9',
            '786facd2c61deb9cf91e9534735124fb8fc11842',
            '94593d2128d38210a2fcd1aabff6dda0d6d9edf8',
            'aa6a0de05b7612707db567078e130a6cd114a9a7',
            'eada5a770da98ab0dd7325e29d00e0714f228d09'
        ])
        assert subset.issubset(set(self.repo.commit_ids))

        # check if we have the proper order of commits
        org = [
            'b986218ba1c9b0d6a259fac9b050b1724ed8e545',
            '3d8f361e72ab303da48d799ff1ac40d5ac37c67e',
            '6cba7170863a2411822803fa77a0a264f1310b35',
            '56349e29c2af3ac913b28bde9a2c6154436e615b',
            '2dda4e345facb0ccff1a191052dd1606dba6781d',
            '6fff84722075f1607a30f436523403845f84cd9e',
            '7d4bc8ec6be56c0f10425afb40b6fc315a4c25e7',
            '3803844fdbd3b711175fc3da9bdacfcd6d29a6fb',
            'dc5d2c0661b61928834a785d3e64a3f80d3aad9c',
            'be90031137367893f1c406e0a8683010fd115b79',
            'db8e58be770518cbb2b1cdfa69146e47cd481481',
            '84478366594b424af694a6c784cb991a16b87c21',
            '17f8e105dddb9f339600389c6dc7175d395a535c',
            '20a662e756499bde3095ffc9bc0643d1def2d0eb',
            '2e319b85e70a707bba0beff866d9f9de032aa4f9',
            '786facd2c61deb9cf91e9534735124fb8fc11842',
            '94593d2128d38210a2fcd1aabff6dda0d6d9edf8',
            'aa6a0de05b7612707db567078e130a6cd114a9a7',
            'eada5a770da98ab0dd7325e29d00e0714f228d09',
            '2c1885c735575ca478bf9e17b0029dca68824458',
            'd9bcd465040bf869799b09ad732c04e0eea99fe9',
            '469e9c847fe1f6f7a697b8b25b4bc5b48780c1a7',
            '4fb8326d78e5120da2c7468dcf7098997be385da',
            '62b4a097164940bd66030c4db51687f3ec035eed',
            '536c1a19428381cfea92ac44985304f6a8049569',
            '965e8ab3c44b070cdaa5bf727ddef0ada980ecc4',
            '9bb326a04ae5d98d437dece54be04f830cf1edd9',
            'f8940bcb890a98c4702319fbe36db75ea309b475',
            'ff5ab059786ebc7411e559a2cc309dfae3625a3b',
            '6b6ad5f82ad5bb6190037671bd254bd4e1f4bf08',
            'ee87846a61c12153b51543bf860e1026c6d3dcba',
        ]
        assert org == self.repo.commit_ids[:31]

    def test_iter_slice(self):
        sliced = list(self.repo[:10])
        itered = list(self.repo)[:10]
        assert sliced == itered

    def test_slicing(self):
        # 4 1 5 10 95
        for sfrom, sto, size in [(0, 4, 4), (1, 2, 1), (10, 15, 5),
                                 (10, 20, 10), (5, 100, 95)]:
            indexes = list(self.repo[sfrom:sto])
            assert len(indexes) == size
            assert indexes[0] == self.repo.get_commit(commit_idx=sfrom)
            assert indexes[-1] == self.repo.get_commit(commit_idx=sto - 1)

    def test_branches(self):
        # TODO: Need more tests here

        # active branches
        assert 'default' in self.repo.branches
        assert 'stable' in self.repo.branches

        # closed
        assert 'git' in self.repo._get_branches(closed=True)
        assert 'web' in self.repo._get_branches(closed=True)

        for name, id in self.repo.branches.items():
            assert isinstance(self.repo.get_commit(id), MercurialCommit)

    def test_tip_in_tags(self):
        # tip is always a tag
        assert 'tip' in self.repo.tags

    def test_tip_commit_in_tags(self):
        tip = self.repo.get_commit()
        assert self.repo.tags['tip'] == tip.raw_id

    def test_initial_commit(self):
        init_commit = self.repo.get_commit(commit_idx=0)
        init_author = init_commit.author

        assert init_commit.message == 'initial import'
        assert init_author == 'Marcin Kuzminski <marcin@python-blog.com>'
        assert init_author == init_commit.committer
        assert sorted(init_commit._file_paths) == sorted([
            'vcs/__init__.py',
            'vcs/backends/BaseRepository.py',
            'vcs/backends/__init__.py',
        ])
        assert sorted(init_commit._dir_paths) == sorted(
            ['', 'vcs', 'vcs/backends'])

        assert init_commit._dir_paths + init_commit._file_paths == \
            init_commit._paths

        with pytest.raises(NodeDoesNotExistError):
            init_commit.get_node(path='foobar')

        node = init_commit.get_node('vcs/')
        assert hasattr(node, 'kind')
        assert node.kind == NodeKind.DIR

        node = init_commit.get_node('vcs')
        assert hasattr(node, 'kind')
        assert node.kind == NodeKind.DIR

        node = init_commit.get_node('vcs/__init__.py')
        assert hasattr(node, 'kind')
        assert node.kind == NodeKind.FILE

    def test_not_existing_commit(self):
        # rawid
        with pytest.raises(RepositoryError):
            self.repo.get_commit('abcd' * 10)
        # shortid
        with pytest.raises(RepositoryError):
            self.repo.get_commit('erro' * 4)
        # numeric
        with pytest.raises(RepositoryError):
            self.repo.get_commit(commit_idx=self.repo.count() + 1)

        # Small chance we ever get to this one
        idx = pow(2, 30)
        with pytest.raises(RepositoryError):
            self.repo.get_commit(commit_idx=idx)

    def test_commit10(self):
        commit10 = self.repo.get_commit(commit_idx=10)
        README = """===
VCS
===

Various Version Control System management abstraction layer for Python.

Introduction
------------

TODO: To be written...

"""
        node = commit10.get_node('README.rst')
        assert node.kind == NodeKind.FILE
        assert node.content == README

    def test_local_clone(self):
        clone_path = next(REPO_PATH_GENERATOR)
        self.repo._local_clone(clone_path)
        repo_clone = MercurialRepository(clone_path)

        assert self.repo.commit_ids == repo_clone.commit_ids

    def test_local_clone_fails_if_target_exists(self):
        with pytest.raises(RepositoryError):
            self.repo._local_clone(self.repo.path)

    def test_update(self):
        repo_clone = self.get_clone_repo()
        branches = repo_clone.branches

        repo_clone._update('default')
        assert branches['default'] == repo_clone._identify()
        repo_clone._update('stable')
        assert branches['stable'] == repo_clone._identify()

    def test_local_pull_branch(self):
        target_repo = self.get_empty_repo()
        source_repo = self.get_clone_repo()

        default = Reference(
            'branch', 'default', source_repo.branches['default'])
        target_repo._local_pull(source_repo.path, default)
        target_repo = MercurialRepository(target_repo.path)
        assert (target_repo.branches['default'] ==
                source_repo.branches['default'])

        stable = Reference('branch', 'stable', source_repo.branches['stable'])
        target_repo._local_pull(source_repo.path, stable)
        target_repo = MercurialRepository(target_repo.path)
        assert target_repo.branches['stable'] == source_repo.branches['stable']

    def test_local_pull_bookmark(self):
        target_repo = self.get_empty_repo()
        source_repo = self.get_clone_repo()

        commits = list(source_repo.get_commits(branch_name='default'))
        foo1_id = commits[-5].raw_id
        foo1 = Reference('book', 'foo1', foo1_id)
        source_repo._update(foo1_id)
        source_repo.bookmark('foo1')

        foo2_id = commits[-3].raw_id
        foo2 = Reference('book', 'foo2', foo2_id)
        source_repo._update(foo2_id)
        source_repo.bookmark('foo2')

        target_repo._local_pull(source_repo.path, foo1)
        target_repo = MercurialRepository(target_repo.path)
        assert target_repo.branches['default'] == commits[-5].raw_id

        target_repo._local_pull(source_repo.path, foo2)
        target_repo = MercurialRepository(target_repo.path)
        assert target_repo.branches['default'] == commits[-3].raw_id

    def test_local_pull_commit(self):
        target_repo = self.get_empty_repo()
        source_repo = self.get_clone_repo()

        commits = list(source_repo.get_commits(branch_name='default'))
        commit_id = commits[-5].raw_id
        commit = Reference('rev', commit_id, commit_id)
        target_repo._local_pull(source_repo.path, commit)
        target_repo = MercurialRepository(target_repo.path)
        assert target_repo.branches['default'] == commit_id

        commit_id = commits[-3].raw_id
        commit = Reference('rev', commit_id, commit_id)
        target_repo._local_pull(source_repo.path, commit)
        target_repo = MercurialRepository(target_repo.path)
        assert target_repo.branches['default'] == commit_id

    def test_local_pull_from_same_repo(self):
        reference = Reference('branch', 'default', None)
        with pytest.raises(ValueError):
            self.repo._local_pull(self.repo.path, reference)

    def test_validate_pull_reference_raises_on_missing_reference(
            self, vcsbackend_hg):
        target_repo = vcsbackend_hg.create_repo(number_of_commits=1)
        reference = Reference(
            'book', 'invalid_reference', 'a' * 40)

        with pytest.raises(CommitDoesNotExistError):
            target_repo._validate_pull_reference(reference)

    def test_heads(self):
        assert set(self.repo._heads()) == set(self.repo.branches.values())

    def test_ancestor(self):
        commits = [
            c.raw_id for c in self.repo.get_commits(branch_name='default')]
        assert self.repo._ancestor(commits[-3], commits[-5]) == commits[-5]
        assert self.repo._ancestor(commits[-5], commits[-3]) == commits[-5]

    def test_local_push(self):
        target_repo = self.get_empty_repo()

        revisions = list(self.repo.get_commits(branch_name='default'))
        revision = revisions[-5].raw_id
        self.repo._local_push(revision, target_repo.path)

        target_repo = MercurialRepository(target_repo.path)

        assert target_repo.branches['default'] == revision

    def test_hooks_can_be_enabled_for_local_push(self):
        revision = 'deadbeef'
        repo_path = 'test_group/test_repo'
        with mock.patch.object(self.repo, '_remote') as remote_mock:
            self.repo._local_push(revision, repo_path, enable_hooks=True)
        remote_mock.push.assert_called_once_with(
            [revision], repo_path, hooks=True, push_branches=False)

    def test_local_merge(self, vcsbackend_hg):
        target_repo = vcsbackend_hg.create_repo(number_of_commits=1)
        source_repo = vcsbackend_hg.clone_repo(target_repo)
        vcsbackend_hg.add_file(target_repo, 'README_MERGE1', 'Version 1')
        target_repo = MercurialRepository(target_repo.path)
        target_rev = target_repo.branches['default']
        target_ref = Reference(
            type='branch', name='default', commit_id=target_rev)
        vcsbackend_hg.add_file(source_repo, 'README_MERGE2', 'Version 2')
        source_repo = MercurialRepository(source_repo.path)
        source_rev = source_repo.branches['default']
        source_ref = Reference(
            type='branch', name='default', commit_id=source_rev)

        target_repo._local_pull(source_repo.path, source_ref)

        merge_message = 'Merge message\n\nDescription:...'
        user_name = 'Albert Einstein'
        user_email = 'albert@einstein.com'
        merge_commit_id, needs_push = target_repo._local_merge(
            target_ref, merge_message, user_name, user_email, source_ref)
        assert needs_push

        target_repo = MercurialRepository(target_repo.path)
        assert target_repo.commit_ids[-3] == target_rev
        assert target_repo.commit_ids[-2] == source_rev
        last_commit = target_repo.get_commit(merge_commit_id)
        assert last_commit.message.strip() == merge_message
        assert last_commit.author == '%s <%s>' % (user_name, user_email)

        assert not os.path.exists(
            os.path.join(target_repo.path, '.hg', 'merge', 'state'))

    def test_local_merge_source_is_fast_forward(self, vcsbackend_hg):
        target_repo = vcsbackend_hg.create_repo(number_of_commits=1)
        source_repo = vcsbackend_hg.clone_repo(target_repo)
        target_rev = target_repo.branches['default']
        target_ref = Reference(
            type='branch', name='default', commit_id=target_rev)
        vcsbackend_hg.add_file(source_repo, 'README_MERGE2', 'Version 2')
        source_repo = MercurialRepository(source_repo.path)
        source_rev = source_repo.branches['default']
        source_ref = Reference(
            type='branch', name='default', commit_id=source_rev)

        target_repo._local_pull(source_repo.path, source_ref)

        merge_message = 'Merge message\n\nDescription:...'
        user_name = 'Albert Einstein'
        user_email = 'albert@einstein.com'
        merge_commit_id, needs_push = target_repo._local_merge(
            target_ref, merge_message, user_name, user_email, source_ref)
        assert merge_commit_id == source_rev
        assert needs_push

        target_repo = MercurialRepository(target_repo.path)
        assert target_repo.commit_ids[-2] == target_rev
        assert target_repo.commit_ids[-1] == source_rev

        assert not os.path.exists(
            os.path.join(target_repo.path, '.hg', 'merge', 'state'))

    def test_local_merge_source_is_integrated(self, vcsbackend_hg):
        target_repo = vcsbackend_hg.create_repo(number_of_commits=1)
        target_rev = target_repo.branches['default']
        target_ref = Reference(
            type='branch', name='default', commit_id=target_rev)

        merge_message = 'Merge message\n\nDescription:...'
        user_name = 'Albert Einstein'
        user_email = 'albert@einstein.com'
        merge_commit_id, needs_push = target_repo._local_merge(
            target_ref, merge_message, user_name, user_email, target_ref)
        assert merge_commit_id == target_rev
        assert not needs_push

        target_repo = MercurialRepository(target_repo.path)
        assert target_repo.commit_ids[-1] == target_rev

        assert not os.path.exists(
            os.path.join(target_repo.path, '.hg', 'merge', 'state'))

    def test_local_merge_raises_exception_on_conflict(self, vcsbackend_hg):
        target_repo = vcsbackend_hg.create_repo(number_of_commits=1)
        source_repo = vcsbackend_hg.clone_repo(target_repo)
        vcsbackend_hg.add_file(target_repo, 'README_MERGE', 'Version 1')
        target_repo = MercurialRepository(target_repo.path)
        target_rev = target_repo.branches['default']
        target_ref = Reference(
            type='branch', name='default', commit_id=target_rev)
        vcsbackend_hg.add_file(source_repo, 'README_MERGE', 'Version 2')
        source_repo = MercurialRepository(source_repo.path)
        source_rev = source_repo.branches['default']
        source_ref = Reference(
            type='branch', name='default', commit_id=source_rev)

        target_repo._local_pull(source_repo.path, source_ref)
        with pytest.raises(RepositoryError):
            target_repo._local_merge(
                target_ref, 'merge_message', 'user name', 'user@name.com',
                source_ref)

        # Check we are not left in an intermediate merge state
        assert not os.path.exists(
            os.path.join(target_repo.path, '.hg', 'merge', 'state'))

    def test_local_merge_of_two_branches_of_the_same_repo(self, backend_hg):
        commits = [
            {'message': 'a'},
            {'message': 'b', 'branch': 'b'},
        ]
        repo = backend_hg.create_repo(commits)
        commit_ids = backend_hg.commit_ids
        target_ref = Reference(
            type='branch', name='default', commit_id=commit_ids['a'])
        source_ref = Reference(
            type='branch', name='b', commit_id=commit_ids['b'])
        merge_message = 'Merge message\n\nDescription:...'
        user_name = 'Albert Einstein'
        user_email = 'albert@einstein.com'
        vcs_repo = repo.scm_instance()
        merge_commit_id, needs_push = vcs_repo._local_merge(
            target_ref, merge_message, user_name, user_email, source_ref)
        assert merge_commit_id != source_ref.commit_id
        assert needs_push is True
        commit = vcs_repo.get_commit(merge_commit_id)
        assert commit.merge is True
        assert commit.message == merge_message

    def test_maybe_prepare_merge_workspace(self):
        workspace = self.repo._maybe_prepare_merge_workspace('pr2', 'unused')

        assert os.path.isdir(workspace)
        workspace_repo = MercurialRepository(workspace)
        assert workspace_repo.branches == self.repo.branches

        # Calling it a second time should also succeed
        workspace = self.repo._maybe_prepare_merge_workspace('pr2', 'unused')
        assert os.path.isdir(workspace)

    def test_cleanup_merge_workspace(self):
        workspace = self.repo._maybe_prepare_merge_workspace('pr3', 'unused')
        self.repo.cleanup_merge_workspace('pr3')

        assert not os.path.exists(workspace)

    def test_cleanup_merge_workspace_invalid_workspace_id(self):
        # No assert: because in case of an inexistent workspace this function
        # should still succeed.
        self.repo.cleanup_merge_workspace('pr4')

    def test_merge_target_is_bookmark(self, vcsbackend_hg):
        target_repo = vcsbackend_hg.create_repo(number_of_commits=1)
        source_repo = vcsbackend_hg.clone_repo(target_repo)
        vcsbackend_hg.add_file(target_repo, 'README_MERGE1', 'Version 1')
        vcsbackend_hg.add_file(source_repo, 'README_MERGE2', 'Version 2')
        imc = source_repo.in_memory_commit
        imc.add(FileNode('file_x', content=source_repo.name))
        imc.commit(
            message=u'Automatic commit from repo merge test',
            author=u'Automatic')
        target_commit = target_repo.get_commit()
        source_commit = source_repo.get_commit()
        default_branch = target_repo.DEFAULT_BRANCH_NAME
        bookmark_name = 'bookmark'
        target_repo._update(default_branch)
        target_repo.bookmark(bookmark_name)
        target_ref = Reference('book', bookmark_name, target_commit.raw_id)
        source_ref = Reference('branch', default_branch, source_commit.raw_id)
        workspace = 'test-merge'

        merge_response = target_repo.merge(
            target_ref, source_repo, source_ref, workspace,
            'test user', 'test@rhodecode.com', 'merge message 1',
            dry_run=False)
        expected_merge_response = MergeResponse(
            True, True, merge_response.merge_commit_id,
            MergeFailureReason.NONE)
        assert merge_response == expected_merge_response

        target_repo = backends.get_backend(vcsbackend_hg.alias)(
            target_repo.path)
        target_commits = list(target_repo.get_commits())
        commit_ids = [c.raw_id for c in target_commits[:-1]]
        assert source_ref.commit_id in commit_ids
        assert target_ref.commit_id in commit_ids

        merge_commit = target_commits[-1]
        assert merge_commit.raw_id == merge_response.merge_commit_id
        assert merge_commit.message.strip() == 'merge message 1'
        assert merge_commit.author == 'test user <test@rhodecode.com>'

        # Check the bookmark was updated in the target repo
        assert (
            target_repo.bookmarks[bookmark_name] ==
            merge_response.merge_commit_id)

    def test_merge_source_is_bookmark(self, vcsbackend_hg):
        target_repo = vcsbackend_hg.create_repo(number_of_commits=1)
        source_repo = vcsbackend_hg.clone_repo(target_repo)
        imc = source_repo.in_memory_commit
        imc.add(FileNode('file_x', content=source_repo.name))
        imc.commit(
            message=u'Automatic commit from repo merge test',
            author=u'Automatic')
        target_commit = target_repo.get_commit()
        source_commit = source_repo.get_commit()
        default_branch = target_repo.DEFAULT_BRANCH_NAME
        bookmark_name = 'bookmark'
        target_ref = Reference('branch', default_branch, target_commit.raw_id)
        source_repo._update(default_branch)
        source_repo.bookmark(bookmark_name)
        source_ref = Reference('book', bookmark_name, source_commit.raw_id)
        workspace = 'test-merge'

        merge_response = target_repo.merge(
            target_ref, source_repo, source_ref, workspace,
            'test user', 'test@rhodecode.com', 'merge message 1',
            dry_run=False)
        expected_merge_response = MergeResponse(
            True, True, merge_response.merge_commit_id,
            MergeFailureReason.NONE)
        assert merge_response == expected_merge_response

        target_repo = backends.get_backend(vcsbackend_hg.alias)(
            target_repo.path)
        target_commits = list(target_repo.get_commits())
        commit_ids = [c.raw_id for c in target_commits]
        assert source_ref.commit_id == commit_ids[-1]
        assert target_ref.commit_id == commit_ids[-2]

    def test_merge_target_has_multiple_heads(self, vcsbackend_hg):
        target_repo = vcsbackend_hg.create_repo(number_of_commits=2)
        source_repo = vcsbackend_hg.clone_repo(target_repo)
        vcsbackend_hg.add_file(target_repo, 'README_MERGE1', 'Version 1')
        vcsbackend_hg.add_file(source_repo, 'README_MERGE2', 'Version 2')

        # add an extra head to the target repo
        imc = target_repo.in_memory_commit
        imc.add(FileNode('file_x', content='foo'))
        commits = list(target_repo.get_commits())
        imc.commit(
            message=u'Automatic commit from repo merge test',
            author=u'Automatic', parents=commits[0:1])

        target_commit = target_repo.get_commit()
        source_commit = source_repo.get_commit()
        default_branch = target_repo.DEFAULT_BRANCH_NAME
        target_repo._update(default_branch)

        target_ref = Reference('branch', default_branch, target_commit.raw_id)
        source_ref = Reference('branch', default_branch, source_commit.raw_id)
        workspace = 'test-merge'

        assert len(target_repo._heads(branch='default')) == 2
        expected_merge_response = MergeResponse(
            False, False, None,
            MergeFailureReason.HG_TARGET_HAS_MULTIPLE_HEADS)
        merge_response = target_repo.merge(
            target_ref, source_repo, source_ref, workspace,
            'test user', 'test@rhodecode.com', 'merge message 1',
            dry_run=False)
        assert merge_response == expected_merge_response

    def test_merge_rebase_source_is_updated_bookmark(self, vcsbackend_hg):
        target_repo = vcsbackend_hg.create_repo(number_of_commits=1)
        source_repo = vcsbackend_hg.clone_repo(target_repo)
        vcsbackend_hg.add_file(target_repo, 'README_MERGE1', 'Version 1')
        vcsbackend_hg.add_file(source_repo, 'README_MERGE2', 'Version 2')
        imc = source_repo.in_memory_commit
        imc.add(FileNode('file_x', content=source_repo.name))
        imc.commit(
            message=u'Automatic commit from repo merge test',
            author=u'Automatic')
        target_commit = target_repo.get_commit()
        source_commit = source_repo.get_commit()

        vcsbackend_hg.add_file(source_repo, 'LICENSE', 'LICENSE Info')

        default_branch = target_repo.DEFAULT_BRANCH_NAME
        bookmark_name = 'bookmark'
        source_repo._update(default_branch)
        source_repo.bookmark(bookmark_name)

        target_ref = Reference('branch', default_branch, target_commit.raw_id)
        source_ref = Reference('book', bookmark_name, source_commit.raw_id)
        workspace = 'test-merge'

        merge_response = target_repo.merge(
            target_ref, source_repo, source_ref, workspace,
            'test user', 'test@rhodecode.com', 'merge message 1',
            dry_run=False, use_rebase=True)

        expected_merge_response = MergeResponse(
            True, True, merge_response.merge_commit_id,
            MergeFailureReason.NONE)
        assert merge_response == expected_merge_response

        target_repo = backends.get_backend(vcsbackend_hg.alias)(
            target_repo.path)
        last_commit = target_repo.get_commit()
        assert last_commit.message == source_commit.message
        assert last_commit.author == source_commit.author
        # This checks that we effectively did a rebase
        assert last_commit.raw_id != source_commit.raw_id

        # Check the target has only 4 commits: 2 were already in target and
        # only two should have been added
        assert len(target_repo.commit_ids) == 2 + 2


class TestGetShadowInstance(object):

    @pytest.fixture
    def repo(self, vcsbackend_hg, monkeypatch):
        repo = vcsbackend_hg.repo
        monkeypatch.setattr(repo, 'config', mock.Mock())
        monkeypatch.setattr('rhodecode.lib.vcs.connection.Hg', mock.Mock())
        return repo

    def test_passes_config(self, repo):
        shadow = repo._get_shadow_instance(repo.path)
        assert shadow.config == repo.config.copy()

    def test_disables_hooks(self, repo):
        shadow = repo._get_shadow_instance(repo.path)
        shadow.config.clear_section.assert_called_once_with('hooks')

    def test_allows_to_keep_hooks(self, repo):
        shadow = repo._get_shadow_instance(repo.path, enable_hooks=True)
        assert not shadow.config.clear_section.called


class TestMercurialCommit(object):

    def _test_equality(self, commit):
        idx = commit.idx
        assert commit == self.repo.get_commit(commit_idx=idx)

    def test_equality(self):
        indexes = [0, 10, 20]
        commits = [self.repo.get_commit(commit_idx=idx) for idx in indexes]
        for commit in commits:
            self._test_equality(commit)

    def test_default_commit(self):
        tip = self.repo.get_commit('tip')
        assert tip == self.repo.get_commit()
        assert tip == self.repo.get_commit(commit_id=None)
        assert tip == self.repo.get_commit(commit_idx=None)
        assert tip == list(self.repo[-1:])[0]

    def test_root_node(self):
        tip = self.repo.get_commit('tip')
        assert tip.root is tip.get_node('')

    def test_lazy_fetch(self):
        """
        Test if commit's nodes expands and are cached as we walk through
        the commit. This test is somewhat hard to write as order of tests
        is a key here. Written by running command after command in a shell.
        """
        commit = self.repo.get_commit(commit_idx=45)
        assert len(commit.nodes) == 0
        root = commit.root
        assert len(commit.nodes) == 1
        assert len(root.nodes) == 8
        # accessing root.nodes updates commit.nodes
        assert len(commit.nodes) == 9

        docs = root.get_node('docs')
        # we haven't yet accessed anything new as docs dir was already cached
        assert len(commit.nodes) == 9
        assert len(docs.nodes) == 8
        # accessing docs.nodes updates commit.nodes
        assert len(commit.nodes) == 17

        assert docs is commit.get_node('docs')
        assert docs is root.nodes[0]
        assert docs is root.dirs[0]
        assert docs is commit.get_node('docs')

    def test_nodes_with_commit(self):
        commit = self.repo.get_commit(commit_idx=45)
        root = commit.root
        docs = root.get_node('docs')
        assert docs is commit.get_node('docs')
        api = docs.get_node('api')
        assert api is commit.get_node('docs/api')
        index = api.get_node('index.rst')
        assert index is commit.get_node('docs/api/index.rst')
        assert index is commit.get_node(
            'docs').get_node('api').get_node('index.rst')

    def test_branch_and_tags(self):
        commit0 = self.repo.get_commit(commit_idx=0)
        assert commit0.branch == 'default'
        assert commit0.tags == []

        commit10 = self.repo.get_commit(commit_idx=10)
        assert commit10.branch == 'default'
        assert commit10.tags == []

        commit44 = self.repo.get_commit(commit_idx=44)
        assert commit44.branch == 'web'

        tip = self.repo.get_commit('tip')
        assert 'tip' in tip.tags

    def test_bookmarks(self):
        commit0 = self.repo.get_commit(commit_idx=0)
        assert commit0.bookmarks == []

    def _test_file_size(self, idx, path, size):
        node = self.repo.get_commit(commit_idx=idx).get_node(path)
        assert node.is_file()
        assert node.size == size

    def test_file_size(self):
        to_check = (
            (10, 'setup.py', 1068),
            (20, 'setup.py', 1106),
            (60, 'setup.py', 1074),

            (10, 'vcs/backends/base.py', 2921),
            (20, 'vcs/backends/base.py', 3936),
            (60, 'vcs/backends/base.py', 6189),
        )
        for idx, path, size in to_check:
            self._test_file_size(idx, path, size)

    def test_file_history_from_commits(self):
        node = self.repo[10].get_node('setup.py')
        commit_ids = [commit.raw_id for commit in node.history]
        assert ['3803844fdbd3b711175fc3da9bdacfcd6d29a6fb'] == commit_ids

        node = self.repo[20].get_node('setup.py')
        node_ids = [commit.raw_id for commit in node.history]
        assert ['eada5a770da98ab0dd7325e29d00e0714f228d09',
                '3803844fdbd3b711175fc3da9bdacfcd6d29a6fb'] == node_ids

        # special case we check history from commit that has this particular
        # file changed this means we check if it's included as well
        node = self.repo.get_commit('eada5a770da98ab0dd7325e29d00e0714f228d09')\
            .get_node('setup.py')
        node_ids = [commit.raw_id for commit in node.history]
        assert ['eada5a770da98ab0dd7325e29d00e0714f228d09',
                '3803844fdbd3b711175fc3da9bdacfcd6d29a6fb'] == node_ids

    def test_file_history(self):
        # we can only check if those commits are present in the history
        # as we cannot update this test every time file is changed
        files = {
            'setup.py': [7, 18, 45, 46, 47, 69, 77],
            'vcs/nodes.py': [
                7, 8, 24, 26, 30, 45, 47, 49, 56, 57, 58, 59, 60, 61, 73, 76],
            'vcs/backends/hg.py': [
                4, 5, 6, 11, 12, 13, 14, 15, 16, 21, 22, 23, 26, 27, 28, 30,
                31, 33, 35, 36, 37, 38, 39, 40, 41, 44, 45, 47, 48, 49, 53, 54,
                55, 58, 60, 61, 67, 68, 69, 70, 73, 77, 78, 79, 82],
        }
        for path, indexes in files.items():
            tip = self.repo.get_commit(commit_idx=indexes[-1])
            node = tip.get_node(path)
            node_indexes = [commit.idx for commit in node.history]
            assert set(indexes).issubset(set(node_indexes)), (
                "We assumed that %s is subset of commits for which file %s "
                "has been changed, and history of that node returned: %s"
                % (indexes, path, node_indexes))

    def test_file_annotate(self):
        files = {
            'vcs/backends/__init__.py': {
                89: {
                    'lines_no': 31,
                    'commits': [
                        32, 32, 61, 32, 32, 37, 32, 32, 32, 44,
                        37, 37, 37, 37, 45, 37, 44, 37, 37, 37,
                        32, 32, 32, 32, 37, 32, 37, 37, 32,
                        32, 32
                    ]
                },
                20: {
                    'lines_no': 1,
                    'commits': [4]
                },
                55: {
                    'lines_no': 31,
                    'commits': [
                        32, 32, 45, 32, 32, 37, 32, 32, 32, 44,
                        37, 37, 37, 37, 45, 37, 44, 37, 37, 37,
                        32, 32, 32, 32, 37, 32, 37, 37, 32,
                        32, 32
                    ]
                }
            },
            'vcs/exceptions.py': {
                89: {
                    'lines_no': 18,
                    'commits': [
                        16, 16, 16, 16, 16, 16, 16, 16, 16, 16,
                        16, 16, 17, 16, 16, 18, 18, 18
                    ]
                },
                20: {
                    'lines_no': 18,
                    'commits': [
                        16, 16, 16, 16, 16, 16, 16, 16, 16, 16,
                        16, 16, 17, 16, 16, 18, 18, 18
                    ]
                },
                55: {
                    'lines_no': 18,
                    'commits': [
                        16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16,
                        17, 16, 16, 18, 18, 18
                    ]
                }
            },
            'MANIFEST.in': {
                89: {
                    'lines_no': 5,
                    'commits': [7, 7, 7, 71, 71]
                },
                20: {
                    'lines_no': 3,
                    'commits': [7, 7, 7]
                },
                55: {
                    'lines_no': 3,
                    'commits': [7, 7, 7]
                }
            }
        }

        for fname, commit_dict in files.items():
            for idx, __ in commit_dict.items():
                commit = self.repo.get_commit(commit_idx=idx)
                l1_1 = [x[1] for x in commit.get_file_annotate(fname)]
                l1_2 = [x[2]().raw_id for x in commit.get_file_annotate(fname)]
                assert l1_1 == l1_2
                l1 = l1_2 = [
                    x[2]().idx for x in commit.get_file_annotate(fname)]
                l2 = files[fname][idx]['commits']
                assert l1 == l2, (
                    "The lists of commit for %s@commit_id%s"
                    "from annotation list should match each other,"
                    "got \n%s \nvs \n%s " % (fname, idx, l1, l2))

    def test_commit_state(self):
        """
        Tests which files have been added/changed/removed at particular commit
        """

        # commit_id 46ad32a4f974:
        # hg st --rev 46ad32a4f974
        #    changed: 13
        #    added:   20
        #    removed: 1
        changed = set([
            '.hgignore', 'README.rst', 'docs/conf.py', 'docs/index.rst',
            'setup.py', 'tests/test_hg.py', 'tests/test_nodes.py',
            'vcs/__init__.py', 'vcs/backends/__init__.py',
            'vcs/backends/base.py', 'vcs/backends/hg.py', 'vcs/nodes.py',
            'vcs/utils/__init__.py'])

        added = set([
            'docs/api/backends/hg.rst', 'docs/api/backends/index.rst',
            'docs/api/index.rst', 'docs/api/nodes.rst',
            'docs/api/web/index.rst', 'docs/api/web/simplevcs.rst',
            'docs/installation.rst', 'docs/quickstart.rst', 'setup.cfg',
            'vcs/utils/baseui_config.py', 'vcs/utils/web.py',
            'vcs/web/__init__.py', 'vcs/web/exceptions.py',
            'vcs/web/simplevcs/__init__.py', 'vcs/web/simplevcs/exceptions.py',
            'vcs/web/simplevcs/middleware.py', 'vcs/web/simplevcs/models.py',
            'vcs/web/simplevcs/settings.py', 'vcs/web/simplevcs/utils.py',
            'vcs/web/simplevcs/views.py'])

        removed = set(['docs/api.rst'])

        commit64 = self.repo.get_commit('46ad32a4f974')
        assert set((node.path for node in commit64.added)) == added
        assert set((node.path for node in commit64.changed)) == changed
        assert set((node.path for node in commit64.removed)) == removed

        # commit_id b090f22d27d6:
        # hg st --rev b090f22d27d6
        #    changed: 13
        #    added:   20
        #    removed: 1
        commit88 = self.repo.get_commit('b090f22d27d6')
        assert set((node.path for node in commit88.added)) == set()
        assert set((node.path for node in commit88.changed)) == \
            set(['.hgignore'])
        assert set((node.path for node in commit88.removed)) == set()

        #
        # 85:
        #    added:   2 [
        #       'vcs/utils/diffs.py', 'vcs/web/simplevcs/views/diffs.py']
        #    changed: 4 ['vcs/web/simplevcs/models.py', ...]
        #    removed: 1 ['vcs/utils/web.py']
        commit85 = self.repo.get_commit(commit_idx=85)
        assert set((node.path for node in commit85.added)) == set([
            'vcs/utils/diffs.py',
            'vcs/web/simplevcs/views/diffs.py'])
        assert set((node.path for node in commit85.changed)) == set([
            'vcs/web/simplevcs/models.py',
            'vcs/web/simplevcs/utils.py',
            'vcs/web/simplevcs/views/__init__.py',
            'vcs/web/simplevcs/views/repository.py',
            ])
        assert set((node.path for node in commit85.removed)) == \
            set(['vcs/utils/web.py'])

    def test_files_state(self):
        """
        Tests state of FileNodes.
        """
        commit = self.repo.get_commit(commit_idx=85)
        node = commit.get_node('vcs/utils/diffs.py')
        assert node.state, NodeState.ADDED
        assert node.added
        assert not node.changed
        assert not node.not_changed
        assert not node.removed

        commit = self.repo.get_commit(commit_idx=88)
        node = commit.get_node('.hgignore')
        assert node.state, NodeState.CHANGED
        assert not node.added
        assert node.changed
        assert not node.not_changed
        assert not node.removed

        commit = self.repo.get_commit(commit_idx=85)
        node = commit.get_node('setup.py')
        assert node.state, NodeState.NOT_CHANGED
        assert not node.added
        assert not node.changed
        assert node.not_changed
        assert not node.removed

        # If node has REMOVED state then trying to fetch it would raise
        # CommitError exception
        commit = self.repo.get_commit(commit_idx=2)
        path = 'vcs/backends/BaseRepository.py'
        with pytest.raises(NodeDoesNotExistError):
            commit.get_node(path)
        # but it would be one of ``removed`` (commit's attribute)
        assert path in [rf.path for rf in commit.removed]

    def test_commit_message_is_unicode(self):
        for cm in self.repo:
            assert type(cm.message) == unicode

    def test_commit_author_is_unicode(self):
        for cm in self.repo:
            assert type(cm.author) == unicode

    def test_repo_files_content_is_unicode(self):
        test_commit = self.repo.get_commit(commit_idx=100)
        for node in test_commit.get_node('/'):
            if node.is_file():
                assert type(node.content) == unicode

    def test_wrong_path(self):
        # There is 'setup.py' in the root dir but not there:
        path = 'foo/bar/setup.py'
        with pytest.raises(VCSError):
            self.repo.get_commit().get_node(path)

    def test_large_file(self):
        # TODO: valid large file
        tip = self.repo.get_commit()
        with pytest.raises(CommitError):
            tip.get_largefile_node("invalid")

    def test_author_email(self):
        assert 'marcin@python-blog.com' == \
            self.repo.get_commit('b986218ba1c9').author_email
        assert 'lukasz.balcerzak@python-center.pl' == \
            self.repo.get_commit('3803844fdbd3').author_email
        assert '' == self.repo.get_commit('84478366594b').author_email

    def test_author_username(self):
        assert 'Marcin Kuzminski' == \
            self.repo.get_commit('b986218ba1c9').author_name
        assert 'Lukasz Balcerzak' == \
            self.repo.get_commit('3803844fdbd3').author_name
        assert 'marcink' == \
            self.repo.get_commit('84478366594b').author_name


class TestGetBranchName(object):
    def test_returns_ref_name_when_type_is_branch(self):
        ref = self._create_ref('branch', 'fake-name')
        result = self.repo._get_branch_name(ref)
        assert result == ref.name

    @pytest.mark.parametrize("type_", ("book", "tag"))
    def test_queries_remote_when_type_is_not_branch(self, type_):
        ref = self._create_ref(type_, 'wrong-fake-name')
        with mock.patch.object(self.repo, "_remote") as remote_mock:
            remote_mock.ctx_branch.return_value = "fake-name"
            result = self.repo._get_branch_name(ref)
        assert result == "fake-name"
        remote_mock.ctx_branch.assert_called_once_with(ref.commit_id)

    def _create_ref(self, type_, name):
        ref = mock.Mock()
        ref.type = type_
        ref.name = 'wrong-fake-name'
        ref.commit_id = "deadbeef"
        return ref


class TestIsTheSameBranch(object):
    def test_returns_true_when_branches_are_equal(self):
        source_ref = mock.Mock(name="source-ref")
        target_ref = mock.Mock(name="target-ref")
        branch_name_patcher = mock.patch.object(
            self.repo, "_get_branch_name", return_value="default")
        with branch_name_patcher as branch_name_mock:
            result = self.repo._is_the_same_branch(source_ref, target_ref)

        expected_calls = [mock.call(source_ref), mock.call(target_ref)]
        assert branch_name_mock.call_args_list == expected_calls
        assert result is True

    def test_returns_false_when_branches_are_not_equal(self):
        source_ref = mock.Mock(name="source-ref")
        source_ref.name = "source-branch"
        target_ref = mock.Mock(name="target-ref")
        source_ref.name = "target-branch"

        def side_effect(ref):
            return ref.name

        branch_name_patcher = mock.patch.object(
            self.repo, "_get_branch_name", side_effect=side_effect)
        with branch_name_patcher as branch_name_mock:
            result = self.repo._is_the_same_branch(source_ref, target_ref)

        expected_calls = [mock.call(source_ref), mock.call(target_ref)]
        assert branch_name_mock.call_args_list == expected_calls
        assert result is False
