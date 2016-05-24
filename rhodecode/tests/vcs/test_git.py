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
import mock
import os
import sys

import pytest

from rhodecode.lib.vcs.backends.base import Reference
from rhodecode.lib.vcs.backends.git import (
    GitRepository, GitCommit, discover_git_version)
from rhodecode.lib.vcs.exceptions import (
    RepositoryError, VCSError, NodeDoesNotExistError
)
from rhodecode.lib.vcs.nodes import (
    NodeKind, FileNode, DirNode, NodeState, SubModuleNode)
from rhodecode.tests import TEST_GIT_REPO, TEST_GIT_REPO_CLONE, get_new_dir
from rhodecode.tests.vcs.base import BackendTestMixin


pytestmark = pytest.mark.backends("git")


def repo_path_generator():
    """
    Return a different path to be used for cloning repos.
    """
    i = 0
    while True:
        i += 1
        yield '%s-%d' % (TEST_GIT_REPO_CLONE, i)


REPO_PATH_GENERATOR = repo_path_generator()


class TestGitRepository:

    # pylint: disable=protected-access

    def __check_for_existing_repo(self):
        if os.path.exists(TEST_GIT_REPO_CLONE):
            self.fail('Cannot test git clone repo as location %s already '
                      'exists. You should manually remove it first.'
                      % TEST_GIT_REPO_CLONE)

    @pytest.fixture(autouse=True)
    def prepare(self, request, pylonsapp):
        self.repo = GitRepository(TEST_GIT_REPO, bare=True)

    def get_clone_repo(self):
        """
        Return a non bare clone of the base repo.
        """
        clone_path = next(REPO_PATH_GENERATOR)
        repo_clone = GitRepository(
            clone_path, create=True, src_url=self.repo.path, bare=False)

        return repo_clone

    def get_empty_repo(self, bare=False):
        """
        Return a non bare empty repo.
        """
        return GitRepository(next(REPO_PATH_GENERATOR), create=True, bare=bare)

    def test_wrong_repo_path(self):
        wrong_repo_path = '/tmp/errorrepo'
        with pytest.raises(RepositoryError):
            GitRepository(wrong_repo_path)

    def test_repo_clone(self):
        self.__check_for_existing_repo()
        repo = GitRepository(TEST_GIT_REPO)
        repo_clone = GitRepository(
            TEST_GIT_REPO_CLONE,
            src_url=TEST_GIT_REPO, create=True, update_after_clone=True)
        assert len(repo.commit_ids) == len(repo_clone.commit_ids)
        # Checking hashes of commits should be enough
        for commit in repo.get_commits():
            raw_id = commit.raw_id
            assert raw_id == repo_clone.get_commit(raw_id).raw_id

    def test_repo_clone_without_create(self):
        with pytest.raises(RepositoryError):
            GitRepository(
                TEST_GIT_REPO_CLONE + '_wo_create', src_url=TEST_GIT_REPO)

    def test_repo_clone_with_update(self):
        repo = GitRepository(TEST_GIT_REPO)
        clone_path = TEST_GIT_REPO_CLONE + '_with_update'
        repo_clone = GitRepository(
            clone_path,
            create=True, src_url=TEST_GIT_REPO, update_after_clone=True)
        assert len(repo.commit_ids) == len(repo_clone.commit_ids)

        # check if current workdir was updated
        fpath = os.path.join(clone_path, 'MANIFEST.in')
        assert os.path.isfile(fpath)

    def test_repo_clone_without_update(self):
        repo = GitRepository(TEST_GIT_REPO)
        clone_path = TEST_GIT_REPO_CLONE + '_without_update'
        repo_clone = GitRepository(
            clone_path,
            create=True, src_url=TEST_GIT_REPO, update_after_clone=False)
        assert len(repo.commit_ids) == len(repo_clone.commit_ids)
        # check if current workdir was *NOT* updated
        fpath = os.path.join(clone_path, 'MANIFEST.in')
        # Make sure it's not bare repo
        assert not repo_clone.bare
        assert not os.path.isfile(fpath)

    def test_repo_clone_into_bare_repo(self):
        repo = GitRepository(TEST_GIT_REPO)
        clone_path = TEST_GIT_REPO_CLONE + '_bare.git'
        repo_clone = GitRepository(
            clone_path, create=True, src_url=repo.path, bare=True)
        assert repo_clone.bare

    def test_create_repo_is_not_bare_by_default(self):
        repo = GitRepository(get_new_dir('not-bare-by-default'), create=True)
        assert not repo.bare

    def test_create_bare_repo(self):
        repo = GitRepository(get_new_dir('bare-repo'), create=True, bare=True)
        assert repo.bare

    def test_update_server_info(self):
        self.repo._update_server_info()

    def test_fetch(self, vcsbackend_git):
        # Note: This is a git specific part of the API, it's only implemented
        # by the git backend.
        source_repo = vcsbackend_git.repo
        target_repo = vcsbackend_git.create_repo()
        target_repo.fetch(source_repo.path)
        # Note: Get a fresh instance, avoids caching trouble
        target_repo = vcsbackend_git.backend(target_repo.path)
        assert len(source_repo.commit_ids) == len(target_repo.commit_ids)

    def test_commit_ids(self):
        # there are 112 commits (by now)
        # so we can assume they would be available from now on
        subset = set([
            'c1214f7e79e02fc37156ff215cd71275450cffc3',
            '38b5fe81f109cb111f549bfe9bb6b267e10bc557',
            'fa6600f6848800641328adbf7811fd2372c02ab2',
            '102607b09cdd60e2793929c4f90478be29f85a17',
            '49d3fd156b6f7db46313fac355dca1a0b94a0017',
            '2d1028c054665b962fa3d307adfc923ddd528038',
            'd7e0d30fbcae12c90680eb095a4f5f02505ce501',
            'ff7ca51e58c505fec0dd2491de52c622bb7a806b',
            'dd80b0f6cf5052f17cc738c2951c4f2070200d7f',
            '8430a588b43b5d6da365400117c89400326e7992',
            'd955cd312c17b02143c04fa1099a352b04368118',
            'f67b87e5c629c2ee0ba58f85197e423ff28d735b',
            'add63e382e4aabc9e1afdc4bdc24506c269b7618',
            'f298fe1189f1b69779a4423f40b48edf92a703fc',
            'bd9b619eb41994cac43d67cf4ccc8399c1125808',
            '6e125e7c890379446e98980d8ed60fba87d0f6d1',
            'd4a54db9f745dfeba6933bf5b1e79e15d0af20bd',
            '0b05e4ed56c802098dfc813cbe779b2f49e92500',
            '191caa5b2c81ed17c0794bf7bb9958f4dcb0b87e',
            '45223f8f114c64bf4d6f853e3c35a369a6305520',
            'ca1eb7957a54bce53b12d1a51b13452f95bc7c7e',
            'f5ea29fc42ef67a2a5a7aecff10e1566699acd68',
            '27d48942240f5b91dfda77accd2caac94708cc7d',
            '622f0eb0bafd619d2560c26f80f09e3b0b0d78af',
            'e686b958768ee96af8029fe19c6050b1a8dd3b2b'])
        assert subset.issubset(set(self.repo.commit_ids))

    def test_slicing(self):
        # 4 1 5 10 95
        for sfrom, sto, size in [(0, 4, 4), (1, 2, 1), (10, 15, 5),
                                 (10, 20, 10), (5, 100, 95)]:
            commit_ids = list(self.repo[sfrom:sto])
            assert len(commit_ids) == size
            assert commit_ids[0] == self.repo.get_commit(commit_idx=sfrom)
            assert commit_ids[-1] == self.repo.get_commit(commit_idx=sto - 1)

    def test_branches(self):
        # TODO: Need more tests here
        # Removed (those are 'remotes' branches for cloned repo)
        # assert 'master' in self.repo.branches
        # assert 'gittree' in self.repo.branches
        # assert 'web-branch' in self.repo.branches
        for __, commit_id in self.repo.branches.items():
            assert isinstance(self.repo.get_commit(commit_id), GitCommit)

    def test_tags(self):
        # TODO: Need more tests here
        assert 'v0.1.1' in self.repo.tags
        assert 'v0.1.2' in self.repo.tags
        for __, commit_id in self.repo.tags.items():
            assert isinstance(self.repo.get_commit(commit_id), GitCommit)

    def _test_single_commit_cache(self, commit_id):
        commit = self.repo.get_commit(commit_id)
        assert commit_id in self.repo.commits
        assert commit is self.repo.commits[commit_id]

    def test_initial_commit(self):
        commit_id = self.repo.commit_ids[0]
        init_commit = self.repo.get_commit(commit_id)
        init_author = init_commit.author

        assert init_commit.message == 'initial import\n'
        assert init_author == 'Marcin Kuzminski <marcin@python-blog.com>'
        assert init_author == init_commit.committer
        for path in ('vcs/__init__.py',
                     'vcs/backends/BaseRepository.py',
                     'vcs/backends/__init__.py'):
            assert isinstance(init_commit.get_node(path), FileNode)
        for path in ('', 'vcs', 'vcs/backends'):
            assert isinstance(init_commit.get_node(path), DirNode)

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
        with pytest.raises(RepositoryError):
            self.repo.get_commit('f' * 40)

    def test_commit10(self):

        commit10 = self.repo.get_commit(self.repo.commit_ids[9])
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

    def test_head(self):
        assert self.repo.head == self.repo.get_commit().raw_id

    def test_checkout_with_create(self):
        repo_clone = self.get_clone_repo()

        new_branch = 'new_branch'
        assert repo_clone._current_branch() == 'master'
        assert set(repo_clone.branches) == set(('master',))
        repo_clone._checkout(new_branch, create=True)

        # Branches is a lazy property so we need to recrete the Repo object.
        repo_clone = GitRepository(repo_clone.path)
        assert set(repo_clone.branches) == set(('master', new_branch))
        assert repo_clone._current_branch() == new_branch

    def test_checkout(self):
        repo_clone = self.get_clone_repo()

        repo_clone._checkout('new_branch', create=True)
        repo_clone._checkout('master')

        assert repo_clone._current_branch() == 'master'

    def test_checkout_same_branch(self):
        repo_clone = self.get_clone_repo()

        repo_clone._checkout('master')
        assert repo_clone._current_branch() == 'master'

    def test_checkout_branch_already_exists(self):
        repo_clone = self.get_clone_repo()

        with pytest.raises(RepositoryError):
            repo_clone._checkout('master', create=True)

    def test_checkout_bare_repo(self):
        with pytest.raises(RepositoryError):
            self.repo._checkout('master')

    def test_current_branch_bare_repo(self):
        with pytest.raises(RepositoryError):
            self.repo._current_branch()

    def test_current_branch_empty_repo(self):
        repo = self.get_empty_repo()
        assert repo._current_branch() is None

    def test_local_clone(self):
        clone_path = next(REPO_PATH_GENERATOR)
        self.repo._local_clone(clone_path, 'master')
        repo_clone = GitRepository(clone_path)

        assert self.repo.commit_ids == repo_clone.commit_ids

    def test_local_clone_with_specific_branch(self):
        source_repo = self.get_clone_repo()

        # Create a new branch in source repo
        new_branch_commit = source_repo.commit_ids[-3]
        source_repo._checkout(new_branch_commit)
        source_repo._checkout('new_branch', create=True)

        clone_path = next(REPO_PATH_GENERATOR)
        source_repo._local_clone(clone_path, 'new_branch')
        repo_clone = GitRepository(clone_path)

        assert source_repo.commit_ids[:-3 + 1] == repo_clone.commit_ids

        clone_path = next(REPO_PATH_GENERATOR)
        source_repo._local_clone(clone_path, 'master')
        repo_clone = GitRepository(clone_path)

        assert source_repo.commit_ids == repo_clone.commit_ids

    def test_local_clone_fails_if_target_exists(self):
        with pytest.raises(RepositoryError):
            self.repo._local_clone(self.repo.path, 'master')

    def test_local_fetch(self):
        target_repo = self.get_empty_repo()
        source_repo = self.get_clone_repo()

        # Create a new branch in source repo
        master_commit = source_repo.commit_ids[-1]
        new_branch_commit = source_repo.commit_ids[-3]
        source_repo._checkout(new_branch_commit)
        source_repo._checkout('new_branch', create=True)

        target_repo._local_fetch(source_repo.path, 'new_branch')
        assert target_repo._last_fetch_heads() == [new_branch_commit]

        target_repo._local_fetch(source_repo.path, 'master')
        assert target_repo._last_fetch_heads() == [master_commit]

    def test_local_fetch_from_bare_repo(self):
        target_repo = self.get_empty_repo()
        target_repo._local_fetch(self.repo.path, 'master')

        master_commit = self.repo.commit_ids[-1]
        assert target_repo._last_fetch_heads() == [master_commit]

    def test_local_fetch_from_same_repo(self):
        with pytest.raises(ValueError):
            self.repo._local_fetch(self.repo.path, 'master')

    def test_local_fetch_branch_does_not_exist(self):
        target_repo = self.get_empty_repo()

        with pytest.raises(RepositoryError):
            target_repo._local_fetch(self.repo.path, 'new_branch')

    def test_local_pull(self):
        target_repo = self.get_empty_repo()
        source_repo = self.get_clone_repo()

        # Create a new branch in source repo
        master_commit = source_repo.commit_ids[-1]
        new_branch_commit = source_repo.commit_ids[-3]
        source_repo._checkout(new_branch_commit)
        source_repo._checkout('new_branch', create=True)

        target_repo._local_pull(source_repo.path, 'new_branch')
        target_repo = GitRepository(target_repo.path)
        assert target_repo.head == new_branch_commit

        target_repo._local_pull(source_repo.path, 'master')
        target_repo = GitRepository(target_repo.path)
        assert target_repo.head == master_commit

    def test_local_pull_in_bare_repo(self):
        with pytest.raises(RepositoryError):
            self.repo._local_pull(self.repo.path, 'master')

    def test_local_merge(self):
        target_repo = self.get_empty_repo()
        source_repo = self.get_clone_repo()

        # Create a new branch in source repo
        master_commit = source_repo.commit_ids[-1]
        new_branch_commit = source_repo.commit_ids[-3]
        source_repo._checkout(new_branch_commit)
        source_repo._checkout('new_branch', create=True)

        # This is required as one cannot do a -ff-only merge in an empty repo.
        target_repo._local_pull(source_repo.path, 'new_branch')

        target_repo._local_fetch(source_repo.path, 'master')
        merge_message = 'Merge message\n\nDescription:...'
        user_name = 'Albert Einstein'
        user_email = 'albert@einstein.com'
        target_repo._local_merge(merge_message, user_name, user_email,
                                 target_repo._last_fetch_heads())

        target_repo = GitRepository(target_repo.path)
        assert target_repo.commit_ids[-2] == master_commit
        last_commit = target_repo.get_commit(target_repo.head)
        assert last_commit.message.strip() == merge_message
        assert last_commit.author == '%s <%s>' % (user_name, user_email)

        assert not os.path.exists(
            os.path.join(target_repo.path, '.git', 'MERGE_HEAD'))

    def test_local_merge_raises_exception_on_conflict(self, vcsbackend_git):
        target_repo = vcsbackend_git.create_repo(number_of_commits=1)
        vcsbackend_git.ensure_file('README', 'I will conflict with you!!!')

        target_repo._local_fetch(self.repo.path, 'master')
        with pytest.raises(RepositoryError):
            target_repo._local_merge(
                'merge_message', 'user name', 'user@name.com',
                target_repo._last_fetch_heads())

        # Check we are not left in an intermediate merge state
        assert not os.path.exists(
            os.path.join(target_repo.path, '.git', 'MERGE_HEAD'))

    def test_local_merge_into_empty_repo(self):
        target_repo = self.get_empty_repo()

        # This is required as one cannot do a -ff-only merge in an empty repo.
        target_repo._local_fetch(self.repo.path, 'master')
        with pytest.raises(RepositoryError):
            target_repo._local_merge(
                'merge_message', 'user name', 'user@name.com',
                target_repo._last_fetch_heads())

    def test_local_merge_in_bare_repo(self):
        with pytest.raises(RepositoryError):
            self.repo._local_merge(
                'merge_message', 'user name', 'user@name.com', None)

    def test_local_push_non_bare(self):
        target_repo = self.get_empty_repo()

        pushed_branch = 'pushed_branch'
        self.repo._local_push('master', target_repo.path, pushed_branch)
        # Fix the HEAD of the target repo, or otherwise GitRepository won't
        # report any branches.
        with open(os.path.join(target_repo.path, '.git', 'HEAD'), 'w') as f:
            f.write('ref: refs/heads/%s' % pushed_branch)

        target_repo = GitRepository(target_repo.path)

        assert (target_repo.branches[pushed_branch] ==
                self.repo.branches['master'])

    def test_local_push_bare(self):
        target_repo = self.get_empty_repo(bare=True)

        pushed_branch = 'pushed_branch'
        self.repo._local_push('master', target_repo.path, pushed_branch)
        # Fix the HEAD of the target repo, or otherwise GitRepository won't
        # report any branches.
        with open(os.path.join(target_repo.path, 'HEAD'), 'w') as f:
            f.write('ref: refs/heads/%s' % pushed_branch)

        target_repo = GitRepository(target_repo.path)

        assert (target_repo.branches[pushed_branch] ==
                self.repo.branches['master'])

    def test_local_push_non_bare_target_branch_is_checked_out(self):
        target_repo = self.get_clone_repo()

        pushed_branch = 'pushed_branch'
        # Create a new branch in source repo
        new_branch_commit = target_repo.commit_ids[-3]
        target_repo._checkout(new_branch_commit)
        target_repo._checkout(pushed_branch, create=True)

        self.repo._local_push('master', target_repo.path, pushed_branch)

        target_repo = GitRepository(target_repo.path)

        assert (target_repo.branches[pushed_branch] ==
                self.repo.branches['master'])

    def test_local_push_raises_exception_on_conflict(self, vcsbackend_git):
        target_repo = vcsbackend_git.create_repo(number_of_commits=1)
        with pytest.raises(RepositoryError):
            self.repo._local_push('master', target_repo.path, 'master')

    def test_hooks_can_be_enabled_via_env_variable_for_local_push(self):
        target_repo = self.get_empty_repo(bare=True)

        with mock.patch.object(self.repo, 'run_git_command') as run_mock:
            self.repo._local_push(
                'master', target_repo.path, 'master', enable_hooks=True)
        env = run_mock.call_args[1]['extra_env']
        assert 'RC_SKIP_HOOKS' not in env

    def _add_failing_hook(self, repo_path, hook_name, bare=False):
        path_components = (
            ['hooks', hook_name] if bare else ['.git', 'hooks', hook_name])
        hook_path = os.path.join(repo_path, *path_components)
        with open(hook_path, 'w') as f:
            script_lines = [
                '#!%s' % sys.executable,
                'import os',
                'import sys',
                'if os.environ.get("RC_SKIP_HOOKS"):',
                '    sys.exit(0)',
                'sys.exit(1)',
            ]
            f.write('\n'.join(script_lines))
        os.chmod(hook_path, 0755)

    def test_local_push_does_not_execute_hook(self):
        target_repo = self.get_empty_repo()

        pushed_branch = 'pushed_branch'
        self._add_failing_hook(target_repo.path, 'pre-receive')
        self.repo._local_push('master', target_repo.path, pushed_branch)
        # Fix the HEAD of the target repo, or otherwise GitRepository won't
        # report any branches.
        with open(os.path.join(target_repo.path, '.git', 'HEAD'), 'w') as f:
            f.write('ref: refs/heads/%s' % pushed_branch)

        target_repo = GitRepository(target_repo.path)

        assert (target_repo.branches[pushed_branch] ==
                self.repo.branches['master'])

    def test_local_push_executes_hook(self):
        target_repo = self.get_empty_repo(bare=True)
        self._add_failing_hook(target_repo.path, 'pre-receive', bare=True)
        with pytest.raises(RepositoryError):
            self.repo._local_push(
                'master', target_repo.path, 'master', enable_hooks=True)

    def test_maybe_prepare_merge_workspace(self):
        workspace = self.repo._maybe_prepare_merge_workspace(
            'pr2', Reference('branch', 'master', 'unused'))

        assert os.path.isdir(workspace)
        workspace_repo = GitRepository(workspace)
        assert workspace_repo.branches == self.repo.branches

        # Calling it a second time should also succeed
        workspace = self.repo._maybe_prepare_merge_workspace(
            'pr2', Reference('branch', 'master', 'unused'))
        assert os.path.isdir(workspace)

    def test_cleanup_merge_workspace(self):
        workspace = self.repo._maybe_prepare_merge_workspace(
            'pr3', Reference('branch', 'master', 'unused'))
        self.repo.cleanup_merge_workspace('pr3')

        assert not os.path.exists(workspace)

    def test_cleanup_merge_workspace_invalid_workspace_id(self):
        # No assert: because in case of an inexistent workspace this function
        # should still succeed.
        self.repo.cleanup_merge_workspace('pr4')

    def test_set_refs(self):
        test_ref = 'refs/test-refs/abcde'
        test_commit_id = 'ecb86e1f424f2608262b130db174a7dfd25a6623'

        self.repo.set_refs(test_ref, test_commit_id)
        stdout, _ = self.repo.run_git_command(['show-ref'])
        assert test_ref in stdout
        assert test_commit_id in stdout

    def test_remove_ref(self):
        test_ref = 'refs/test-refs/abcde'
        test_commit_id = 'ecb86e1f424f2608262b130db174a7dfd25a6623'
        self.repo.set_refs(test_ref, test_commit_id)
        stdout, _ = self.repo.run_git_command(['show-ref'])
        assert test_ref in stdout
        assert test_commit_id in stdout

        self.repo.remove_ref(test_ref)
        stdout, _ = self.repo.run_git_command(['show-ref'])
        assert test_ref not in stdout
        assert test_commit_id not in stdout


class TestGitCommit(object):

    @pytest.fixture(autouse=True)
    def prepare(self):
        self.repo = GitRepository(TEST_GIT_REPO)

    def test_default_commit(self):
        tip = self.repo.get_commit()
        assert tip == self.repo.get_commit(None)
        assert tip == self.repo.get_commit('tip')

    def test_root_node(self):
        tip = self.repo.get_commit()
        assert tip.root is tip.get_node('')

    def test_lazy_fetch(self):
        """
        Test if commit's nodes expands and are cached as we walk through
        the commit. This test is somewhat hard to write as order of tests
        is a key here. Written by running command after command in a shell.
        """
        commit_id = '2a13f185e4525f9d4b59882791a2d397b90d5ddc'
        assert commit_id in self.repo.commit_ids
        commit = self.repo.get_commit(commit_id)
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
        commit_id = '2a13f185e4525f9d4b59882791a2d397b90d5ddc'
        commit = self.repo.get_commit(commit_id)
        root = commit.root
        docs = root.get_node('docs')
        assert docs is commit.get_node('docs')
        api = docs.get_node('api')
        assert api is commit.get_node('docs/api')
        index = api.get_node('index.rst')
        assert index is commit.get_node('docs/api/index.rst')
        assert index is commit.get_node('docs')\
            .get_node('api')\
            .get_node('index.rst')

    def test_branch_and_tags(self):
        """
        rev0 = self.repo.commit_ids[0]
        commit0 = self.repo.get_commit(rev0)
        assert commit0.branch == 'master'
        assert commit0.tags == []

        rev10 = self.repo.commit_ids[10]
        commit10 = self.repo.get_commit(rev10)
        assert commit10.branch == 'master'
        assert commit10.tags == []

        rev44 = self.repo.commit_ids[44]
        commit44 = self.repo.get_commit(rev44)
        assert commit44.branch == 'web-branch'

        tip = self.repo.get_commit('tip')
        assert 'tip' in tip.tags
        """
        # Those tests would fail - branches are now going
        # to be changed at main API in order to support git backend
        pass

    def test_file_size(self):
        to_check = (
            ('c1214f7e79e02fc37156ff215cd71275450cffc3',
                'vcs/backends/BaseRepository.py', 502),
            ('d7e0d30fbcae12c90680eb095a4f5f02505ce501',
                'vcs/backends/hg.py', 854),
            ('6e125e7c890379446e98980d8ed60fba87d0f6d1',
                'setup.py', 1068),

            ('d955cd312c17b02143c04fa1099a352b04368118',
                'vcs/backends/base.py', 2921),
            ('ca1eb7957a54bce53b12d1a51b13452f95bc7c7e',
                'vcs/backends/base.py', 3936),
            ('f50f42baeed5af6518ef4b0cb2f1423f3851a941',
                'vcs/backends/base.py', 6189),
        )
        for commit_id, path, size in to_check:
            node = self.repo.get_commit(commit_id).get_node(path)
            assert node.is_file()
            assert node.size == size

    def test_file_history_from_commits(self):
        node = self.repo[10].get_node('setup.py')
        commit_ids = [commit.raw_id for commit in node.history]
        assert ['ff7ca51e58c505fec0dd2491de52c622bb7a806b'] == commit_ids

        node = self.repo[20].get_node('setup.py')
        node_ids = [commit.raw_id for commit in node.history]
        assert ['191caa5b2c81ed17c0794bf7bb9958f4dcb0b87e',
                'ff7ca51e58c505fec0dd2491de52c622bb7a806b'] == node_ids

        # special case we check history from commit that has this particular
        # file changed this means we check if it's included as well
        node = self.repo.get_commit('191caa5b2c81ed17c0794bf7bb9958f4dcb0b87e') \
            .get_node('setup.py')
        node_ids = [commit.raw_id for commit in node.history]
        assert ['191caa5b2c81ed17c0794bf7bb9958f4dcb0b87e',
                'ff7ca51e58c505fec0dd2491de52c622bb7a806b'] == node_ids

    def test_file_history(self):
        # we can only check if those commits are present in the history
        # as we cannot update this test every time file is changed
        files = {
            'setup.py': [
                '54386793436c938cff89326944d4c2702340037d',
                '51d254f0ecf5df2ce50c0b115741f4cf13985dab',
                '998ed409c795fec2012b1c0ca054d99888b22090',
                '5e0eb4c47f56564395f76333f319d26c79e2fb09',
                '0115510b70c7229dbc5dc49036b32e7d91d23acd',
                '7cb3fd1b6d8c20ba89e2264f1c8baebc8a52d36e',
                '2a13f185e4525f9d4b59882791a2d397b90d5ddc',
                '191caa5b2c81ed17c0794bf7bb9958f4dcb0b87e',
                'ff7ca51e58c505fec0dd2491de52c622bb7a806b',
            ],
            'vcs/nodes.py': [
                '33fa3223355104431402a888fa77a4e9956feb3e',
                'fa014c12c26d10ba682fadb78f2a11c24c8118e1',
                'e686b958768ee96af8029fe19c6050b1a8dd3b2b',
                'ab5721ca0a081f26bf43d9051e615af2cc99952f',
                'c877b68d18e792a66b7f4c529ea02c8f80801542',
                '4313566d2e417cb382948f8d9d7c765330356054',
                '6c2303a793671e807d1cfc70134c9ca0767d98c2',
                '54386793436c938cff89326944d4c2702340037d',
                '54000345d2e78b03a99d561399e8e548de3f3203',
                '1c6b3677b37ea064cb4b51714d8f7498f93f4b2b',
                '2d03ca750a44440fb5ea8b751176d1f36f8e8f46',
                '2a08b128c206db48c2f0b8f70df060e6db0ae4f8',
                '30c26513ff1eb8e5ce0e1c6b477ee5dc50e2f34b',
                'ac71e9503c2ca95542839af0ce7b64011b72ea7c',
                '12669288fd13adba2a9b7dd5b870cc23ffab92d2',
                '5a0c84f3e6fe3473e4c8427199d5a6fc71a9b382',
                '12f2f5e2b38e6ff3fbdb5d722efed9aa72ecb0d5',
                '5eab1222a7cd4bfcbabc218ca6d04276d4e27378',
                'f50f42baeed5af6518ef4b0cb2f1423f3851a941',
                'd7e390a45f6aa96f04f5e7f583ad4f867431aa25',
                'f15c21f97864b4f071cddfbf2750ec2e23859414',
                'e906ef056cf539a4e4e5fc8003eaf7cf14dd8ade',
                'ea2b108b48aa8f8c9c4a941f66c1a03315ca1c3b',
                '84dec09632a4458f79f50ddbbd155506c460b4f9',
                '0115510b70c7229dbc5dc49036b32e7d91d23acd',
                '2a13f185e4525f9d4b59882791a2d397b90d5ddc',
                '3bf1c5868e570e39569d094f922d33ced2fa3b2b',
                'b8d04012574729d2c29886e53b1a43ef16dd00a1',
                '6970b057cffe4aab0a792aa634c89f4bebf01441',
                'dd80b0f6cf5052f17cc738c2951c4f2070200d7f',
                'ff7ca51e58c505fec0dd2491de52c622bb7a806b',
            ],
            'vcs/backends/git.py': [
                '4cf116ad5a457530381135e2f4c453e68a1b0105',
                '9a751d84d8e9408e736329767387f41b36935153',
                'cb681fb539c3faaedbcdf5ca71ca413425c18f01',
                '428f81bb652bcba8d631bce926e8834ff49bdcc6',
                '180ab15aebf26f98f714d8c68715e0f05fa6e1c7',
                '2b8e07312a2e89e92b90426ab97f349f4bce2a3a',
                '50e08c506174d8645a4bb517dd122ac946a0f3bf',
                '54000345d2e78b03a99d561399e8e548de3f3203',
            ],
        }
        for path, commit_ids in files.items():
            node = self.repo.get_commit(commit_ids[0]).get_node(path)
            node_ids = [commit.raw_id for commit in node.history]
            assert set(commit_ids).issubset(set(node_ids)), (
                "We assumed that %s is subset of commit_ids for which file %s "
                "has been changed, and history of that node returned: %s"
                % (commit_ids, path, node_ids))

    def test_file_annotate(self):
        files = {
            'vcs/backends/__init__.py': {
                'c1214f7e79e02fc37156ff215cd71275450cffc3': {
                    'lines_no': 1,
                    'commits': [
                        'c1214f7e79e02fc37156ff215cd71275450cffc3',
                    ],
                },
                '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647': {
                    'lines_no': 21,
                    'commits': [
                        '49d3fd156b6f7db46313fac355dca1a0b94a0017',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                    ],
                },
                'e29b67bd158580fc90fc5e9111240b90e6e86064': {
                    'lines_no': 32,
                    'commits': [
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '5eab1222a7cd4bfcbabc218ca6d04276d4e27378',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '992f38217b979d0b0987d0bae3cc26dac85d9b19',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '54000345d2e78b03a99d561399e8e548de3f3203',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '78c3f0c23b7ee935ec276acb8b8212444c33c396',
                        '992f38217b979d0b0987d0bae3cc26dac85d9b19',
                        '992f38217b979d0b0987d0bae3cc26dac85d9b19',
                        '992f38217b979d0b0987d0bae3cc26dac85d9b19',
                        '992f38217b979d0b0987d0bae3cc26dac85d9b19',
                        '2a13f185e4525f9d4b59882791a2d397b90d5ddc',
                        '992f38217b979d0b0987d0bae3cc26dac85d9b19',
                        '78c3f0c23b7ee935ec276acb8b8212444c33c396',
                        '992f38217b979d0b0987d0bae3cc26dac85d9b19',
                        '992f38217b979d0b0987d0bae3cc26dac85d9b19',
                        '992f38217b979d0b0987d0bae3cc26dac85d9b19',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '992f38217b979d0b0987d0bae3cc26dac85d9b19',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '992f38217b979d0b0987d0bae3cc26dac85d9b19',
                        '992f38217b979d0b0987d0bae3cc26dac85d9b19',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                        '16fba1ae9334d79b66d7afed2c2dfbfa2ae53647',
                    ],
                },
            },
        }

        for fname, commit_dict in files.items():
            for commit_id, __ in commit_dict.items():
                commit = self.repo.get_commit(commit_id)

                l1_1 = [x[1] for x in commit.get_file_annotate(fname)]
                l1_2 = [x[2]().raw_id for x in commit.get_file_annotate(fname)]
                assert l1_1 == l1_2
                l1 = l1_1
                l2 = files[fname][commit_id]['commits']
                assert l1 == l2, (
                    "The lists of commit_ids for %s@commit_id %s"
                    "from annotation list should match each other, "
                    "got \n%s \nvs \n%s " % (fname, commit_id, l1, l2))

    def test_files_state(self):
        """
        Tests state of FileNodes.
        """
        node = self.repo\
            .get_commit('e6ea6d16e2f26250124a1f4b4fe37a912f9d86a0')\
            .get_node('vcs/utils/diffs.py')
        assert node.state, NodeState.ADDED
        assert node.added
        assert not node.changed
        assert not node.not_changed
        assert not node.removed

        node = self.repo\
            .get_commit('33fa3223355104431402a888fa77a4e9956feb3e')\
            .get_node('.hgignore')
        assert node.state, NodeState.CHANGED
        assert not node.added
        assert node.changed
        assert not node.not_changed
        assert not node.removed

        node = self.repo\
            .get_commit('e29b67bd158580fc90fc5e9111240b90e6e86064')\
            .get_node('setup.py')
        assert node.state, NodeState.NOT_CHANGED
        assert not node.added
        assert not node.changed
        assert node.not_changed
        assert not node.removed

        # If node has REMOVED state then trying to fetch it would raise
        # CommitError exception
        commit = self.repo.get_commit(
            'fa6600f6848800641328adbf7811fd2372c02ab2')
        path = 'vcs/backends/BaseRepository.py'
        with pytest.raises(NodeDoesNotExistError):
            commit.get_node(path)
        # but it would be one of ``removed`` (commit's attribute)
        assert path in [rf.path for rf in commit.removed]

        commit = self.repo.get_commit(
            '54386793436c938cff89326944d4c2702340037d')
        changed = [
            'setup.py', 'tests/test_nodes.py', 'vcs/backends/hg.py',
            'vcs/nodes.py']
        assert set(changed) == set([f.path for f in commit.changed])

    def test_unicode_refs(self):
        unicode_branches = {
            'unicode': ['6c0ce52b229aa978889e91b38777f800e85f330b', 'H'],
            u'uniçö∂e': ['ürl', 'H']
        }
        with mock.patch(
            ("rhodecode.lib.vcs.backends.git.repository"
                ".GitRepository._parsed_refs"),
                unicode_branches):
            branches = self.repo.branches

        assert 'unicode' in branches
        assert u'uniçö∂e' in branches

    def test_commit_message_is_unicode(self):
        for commit in self.repo:
            assert type(commit.message) == unicode

    def test_commit_author_is_unicode(self):
        for commit in self.repo:
            assert type(commit.author) == unicode

    def test_repo_files_content_is_unicode(self):
        commit = self.repo.get_commit()
        for node in commit.get_node('/'):
            if node.is_file():
                assert type(node.content) == unicode

    def test_wrong_path(self):
        # There is 'setup.py' in the root dir but not there:
        path = 'foo/bar/setup.py'
        tip = self.repo.get_commit()
        with pytest.raises(VCSError):
            tip.get_node(path)

    @pytest.mark.parametrize("author_email, commit_id", [
        ('marcin@python-blog.com', 'c1214f7e79e02fc37156ff215cd71275450cffc3'),
        ('lukasz.balcerzak@python-center.pl',
         'ff7ca51e58c505fec0dd2491de52c622bb7a806b'),
        ('none@none', '8430a588b43b5d6da365400117c89400326e7992'),
    ])
    def test_author_email(self, author_email, commit_id):
        commit = self.repo.get_commit(commit_id)
        assert author_email == commit.author_email

    @pytest.mark.parametrize("author, commit_id", [
        ('Marcin Kuzminski', 'c1214f7e79e02fc37156ff215cd71275450cffc3'),
        ('Lukasz Balcerzak', 'ff7ca51e58c505fec0dd2491de52c622bb7a806b'),
        ('marcink', '8430a588b43b5d6da365400117c89400326e7992'),
    ])
    def test_author_username(self, author, commit_id):
        commit = self.repo.get_commit(commit_id)
        assert author == commit.author_name


class TestGitSpecificWithRepo(BackendTestMixin):

    @classmethod
    def _get_commits(cls):
        return [
            {
                'message': 'Initial',
                'author': 'Joe Doe <joe.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 20),
                'added': [
                    FileNode('foobar/static/js/admin/base.js', content='base'),
                    FileNode(
                        'foobar/static/admin', content='admin',
                        mode=0120000),  # this is a link
                    FileNode('foo', content='foo'),
                ],
            },
            {
                'message': 'Second',
                'author': 'Joe Doe <joe.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 22),
                'added': [
                    FileNode('foo2', content='foo2'),
                ],
            },
        ]

    def test_paths_slow_traversing(self):
        commit = self.repo.get_commit()
        assert commit.get_node('foobar').get_node('static').get_node('js')\
            .get_node('admin').get_node('base.js').content == 'base'

    def test_paths_fast_traversing(self):
        commit = self.repo.get_commit()
        assert (
            commit.get_node('foobar/static/js/admin/base.js').content ==
            'base')

    def test_get_diff_runs_git_command_with_hashes(self):
        self.repo.run_git_command = mock.Mock(return_value=['', ''])
        self.repo.get_diff(self.repo[0], self.repo[1])
        self.repo.run_git_command.assert_called_once_with(
            ['diff', '-U3', '--full-index', '--binary', '-p', '-M',
             '--abbrev=40', self.repo._get_commit_id(0),
             self.repo._get_commit_id(1)])

    def test_get_diff_runs_git_command_with_str_hashes(self):
        self.repo.run_git_command = mock.Mock(return_value=['', ''])
        self.repo.get_diff(self.repo.EMPTY_COMMIT, self.repo[1])
        self.repo.run_git_command.assert_called_once_with(
            ['show', '-U3', '--full-index', '--binary', '-p', '-M',
             '--abbrev=40', self.repo._get_commit_id(1)])

    def test_get_diff_runs_git_command_with_path_if_its_given(self):
        self.repo.run_git_command = mock.Mock(return_value=['', ''])
        self.repo.get_diff(self.repo[0], self.repo[1], 'foo')
        self.repo.run_git_command.assert_called_once_with(
            ['diff', '-U3', '--full-index', '--binary', '-p', '-M',
             '--abbrev=40', self.repo._get_commit_id(0),
             self.repo._get_commit_id(1), '--', 'foo'])


class TestGitRegression(BackendTestMixin):

    @classmethod
    def _get_commits(cls):
        return [
            {
                'message': 'Initial',
                'author': 'Joe Doe <joe.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 20),
                'added': [
                    FileNode('bot/__init__.py', content='base'),
                    FileNode('bot/templates/404.html', content='base'),
                    FileNode('bot/templates/500.html', content='base'),
                ],
            },
            {
                'message': 'Second',
                'author': 'Joe Doe <joe.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 22),
                'added': [
                    FileNode('bot/build/migrations/1.py', content='foo2'),
                    FileNode('bot/build/migrations/2.py', content='foo2'),
                    FileNode(
                        'bot/build/static/templates/f.html', content='foo2'),
                    FileNode(
                        'bot/build/static/templates/f1.html', content='foo2'),
                    FileNode('bot/build/templates/err.html', content='foo2'),
                    FileNode('bot/build/templates/err2.html', content='foo2'),
                ],
            },
        ]

    @pytest.mark.parametrize("path, expected_paths", [
        ('bot', [
            'bot/build',
            'bot/templates',
            'bot/__init__.py']),
        ('bot/build', [
            'bot/build/migrations',
            'bot/build/static',
            'bot/build/templates']),
        ('bot/build/static', [
            'bot/build/static/templates']),
        ('bot/build/static/templates', [
            'bot/build/static/templates/f.html',
            'bot/build/static/templates/f1.html']),
        ('bot/build/templates', [
            'bot/build/templates/err.html',
            'bot/build/templates/err2.html']),
        ('bot/templates/', [
            'bot/templates/404.html',
            'bot/templates/500.html']),
    ])
    def test_similar_paths(self, path, expected_paths):
        commit = self.repo.get_commit()
        paths = [n.path for n in commit.get_nodes(path)]
        assert paths == expected_paths


class TestDiscoverGitVersion:

    def test_returns_git_version(self, pylonsapp):
        version = discover_git_version()
        assert version

    def test_returns_empty_string_without_vcsserver(self):
        mock_connection = mock.Mock()
        mock_connection.discover_git_version = mock.Mock(
            side_effect=Exception)
        with mock.patch('rhodecode.lib.vcs.connection.Git', mock_connection):
            version = discover_git_version()
        assert version == ''


class TestGetSubmoduleUrl(object):
    def test_submodules_file_found(self):
        commit = GitCommit(repository=mock.Mock(), raw_id='abcdef12', idx=1)
        node = mock.Mock()
        with mock.patch.object(
                commit, 'get_node', return_value=node) as get_node_mock:
            node.content = (
                '[submodule "subrepo1"]\n'
                '\tpath = subrepo1\n'
                '\turl = https://code.rhodecode.com/dulwich\n'
            )
            result = commit._get_submodule_url('subrepo1')
        get_node_mock.assert_called_once_with('.gitmodules')
        assert result == 'https://code.rhodecode.com/dulwich'

    def test_complex_submodule_path(self):
        commit = GitCommit(repository=mock.Mock(), raw_id='abcdef12', idx=1)
        node = mock.Mock()
        with mock.patch.object(
                commit, 'get_node', return_value=node) as get_node_mock:
            node.content = (
                '[submodule "complex/subrepo/path"]\n'
                '\tpath = complex/subrepo/path\n'
                '\turl = https://code.rhodecode.com/dulwich\n'
            )
            result = commit._get_submodule_url('complex/subrepo/path')
        get_node_mock.assert_called_once_with('.gitmodules')
        assert result == 'https://code.rhodecode.com/dulwich'

    def test_submodules_file_not_found(self):
        commit = GitCommit(repository=mock.Mock(), raw_id='abcdef12', idx=1)
        with mock.patch.object(
                commit, 'get_node', side_effect=NodeDoesNotExistError):
            result = commit._get_submodule_url('complex/subrepo/path')
        assert result is None

    def test_path_not_found(self):
        commit = GitCommit(repository=mock.Mock(), raw_id='abcdef12', idx=1)
        node = mock.Mock()
        with mock.patch.object(
                commit, 'get_node', return_value=node) as get_node_mock:
            node.content = (
                '[submodule "subrepo1"]\n'
                '\tpath = subrepo1\n'
                '\turl = https://code.rhodecode.com/dulwich\n'
            )
            result = commit._get_submodule_url('subrepo2')
        get_node_mock.assert_called_once_with('.gitmodules')
        assert result is None

    def test_returns_cached_values(self):
        commit = GitCommit(repository=mock.Mock(), raw_id='abcdef12', idx=1)
        node = mock.Mock()
        with mock.patch.object(
                commit, 'get_node', return_value=node) as get_node_mock:
            node.content = (
                '[submodule "subrepo1"]\n'
                '\tpath = subrepo1\n'
                '\turl = https://code.rhodecode.com/dulwich\n'
            )
            for _ in range(3):
                commit._get_submodule_url('subrepo1')
        get_node_mock.assert_called_once_with('.gitmodules')

    def test_get_node_returns_a_link(self):
        repository = mock.Mock()
        repository.alias = 'git'
        commit = GitCommit(repository=repository, raw_id='abcdef12', idx=1)
        submodule_url = 'https://code.rhodecode.com/dulwich'
        get_id_patch = mock.patch.object(
            commit, '_get_id_for_path', return_value=(1, 'link'))
        get_submodule_patch = mock.patch.object(
            commit, '_get_submodule_url', return_value=submodule_url)

        with get_id_patch, get_submodule_patch as submodule_mock:
            node = commit.get_node('/abcde')

        submodule_mock.assert_called_once_with('/abcde')
        assert type(node) == SubModuleNode
        assert node.url == submodule_url

    def test_get_nodes_returns_links(self):
        repository = mock.MagicMock()
        repository.alias = 'git'
        repository._remote.tree_items.return_value = [
            ('subrepo', 'stat', 1, 'link')
        ]
        commit = GitCommit(repository=repository, raw_id='abcdef12', idx=1)
        submodule_url = 'https://code.rhodecode.com/dulwich'
        get_id_patch = mock.patch.object(
            commit, '_get_id_for_path', return_value=(1, 'tree'))
        get_submodule_patch = mock.patch.object(
            commit, '_get_submodule_url', return_value=submodule_url)

        with get_id_patch, get_submodule_patch as submodule_mock:
            nodes = commit.get_nodes('/abcde')

        submodule_mock.assert_called_once_with('/abcde/subrepo')
        assert len(nodes) == 1
        assert type(nodes[0]) == SubModuleNode
        assert nodes[0].url == submodule_url
