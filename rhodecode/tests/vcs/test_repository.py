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
from urllib2 import URLError

import mock
import pytest

from rhodecode.lib.vcs import backends
from rhodecode.lib.vcs.backends.base import (
    Config, BaseInMemoryCommit, Reference, MergeResponse, MergeFailureReason)
from rhodecode.lib.vcs.exceptions import VCSError, RepositoryError
from rhodecode.lib.vcs.nodes import FileNode
from rhodecode.tests.vcs.base import BackendTestMixin


class TestRepositoryBase(BackendTestMixin):
    recreate_repo_per_test = False

    def test_init_accepts_unicode_path(self, tmpdir):
        path = unicode(tmpdir.join(u'unicode ä'))
        self.Backend(path, create=True)

    def test_init_accepts_str_path(self, tmpdir):
        path = str(tmpdir.join('str ä'))
        self.Backend(path, create=True)

    def test_init_fails_if_path_does_not_exist(self, tmpdir):
        path = unicode(tmpdir.join('i-do-not-exist'))
        with pytest.raises(VCSError):
            self.Backend(path)

    def test_init_fails_if_path_is_not_a_valid_repository(self, tmpdir):
        path = unicode(tmpdir.mkdir(u'unicode ä'))
        with pytest.raises(VCSError):
            self.Backend(path)

    def test_has_commits_attribute(self):
        self.repo.commit_ids

    def test_name(self):
        assert self.repo.name.startswith('vcs-test')

    @pytest.mark.backends("hg", "git")
    def test_has_default_branch_name(self):
        assert self.repo.DEFAULT_BRANCH_NAME is not None

    @pytest.mark.backends("svn")
    def test_has_no_default_branch_name(self):
        assert self.repo.DEFAULT_BRANCH_NAME is None

    def test_has_empty_commit(self):
        assert self.repo.EMPTY_COMMIT_ID is not None
        assert self.repo.EMPTY_COMMIT is not None

    def test_empty_changeset_is_deprecated(self):
        def get_empty_changeset(repo):
            return repo.EMPTY_CHANGESET
        pytest.deprecated_call(get_empty_changeset, self.repo)

    def test_bookmarks(self):
        assert len(self.repo.bookmarks) == 0

    # TODO: Cover two cases: Local repo path, remote URL
    def test_check_url(self):
        config = Config()
        assert self.Backend.check_url(self.repo.path, config)

    def test_check_url_invalid(self):
        config = Config()
        with pytest.raises(URLError):
            self.Backend.check_url(self.repo.path + "invalid", config)

    def test_get_contact(self):
        self.repo.contact

    def test_get_description(self):
        self.repo.description

    def test_get_hook_location(self):
        assert len(self.repo.get_hook_location()) != 0

    def test_last_change(self):
        assert self.repo.last_change >= datetime.datetime(2010, 1, 1, 21, 0)

    def test_last_change_in_empty_repository(self, vcsbackend):
        delta = datetime.timedelta(seconds=1)
        start = datetime.datetime.now()
        empty_repo = vcsbackend.create_repo()
        now = datetime.datetime.now()
        assert empty_repo.last_change >= start - delta
        assert empty_repo.last_change <= now + delta

    def test_repo_equality(self):
        assert self.repo == self.repo

    def test_repo_equality_broken_object(self):
        import copy
        _repo = copy.copy(self.repo)
        delattr(_repo, 'path')
        assert self.repo != _repo

    def test_repo_equality_other_object(self):
        class dummy(object):
            path = self.repo.path
        assert self.repo != dummy()

    def test_get_commit_is_implemented(self):
        self.repo.get_commit()

    def test_get_commits_is_implemented(self):
        commit_iter = iter(self.repo.get_commits())
        commit = next(commit_iter)
        assert commit.idx == 0

    def test_supports_iteration(self):
        repo_iter = iter(self.repo)
        commit = next(repo_iter)
        assert commit.idx == 0

    def test_in_memory_commit(self):
        imc = self.repo.in_memory_commit
        assert isinstance(imc, BaseInMemoryCommit)

    @pytest.mark.backends("hg")
    def test__get_url_unicode(self):
        url = u'/home/repos/malmö'
        assert self.repo._get_url(url)


class TestDeprecatedRepositoryAPI(BackendTestMixin):
    recreate_repo_per_test = False

    def test_revisions_is_deprecated(self):
        def get_revisions(repo):
            return repo.revisions
        pytest.deprecated_call(get_revisions, self.repo)

    def test_get_changeset_is_deprecated(self):
        pytest.deprecated_call(self.repo.get_changeset)

    def test_get_changesets_is_deprecated(self):
        pytest.deprecated_call(self.repo.get_changesets)

    def test_in_memory_changeset_is_deprecated(self):
        def get_imc(repo):
            return repo.in_memory_changeset
        pytest.deprecated_call(get_imc, self.repo)


# TODO: these tests are incomplete, must check the resulting compare result for
# correcteness
class TestRepositoryCompare:

    @pytest.mark.parametrize('merge', [True, False])
    def test_compare_commits_of_same_repository(self, vcsbackend, merge):
        target_repo = vcsbackend.create_repo(number_of_commits=5)
        target_repo.compare(
            target_repo[1].raw_id, target_repo[3].raw_id, target_repo,
            merge=merge)

    @pytest.mark.xfail_backends('svn')
    @pytest.mark.parametrize('merge', [True, False])
    def test_compare_cloned_repositories(self, vcsbackend, merge):
        target_repo = vcsbackend.create_repo(number_of_commits=5)
        source_repo = vcsbackend.clone_repo(target_repo)
        assert target_repo != source_repo

        vcsbackend.add_file(source_repo, 'newfile', 'somecontent')
        source_commit = source_repo.get_commit()

        target_repo.compare(
            target_repo[1].raw_id, source_repo[3].raw_id, source_repo,
            merge=merge)

    @pytest.mark.xfail_backends('svn')
    @pytest.mark.parametrize('merge', [True, False])
    def test_compare_unrelated_repositories(self, vcsbackend, merge):
        orig = vcsbackend.create_repo(number_of_commits=5)
        unrelated = vcsbackend.create_repo(number_of_commits=5)
        assert orig != unrelated

        orig.compare(
            orig[1].raw_id, unrelated[3].raw_id, unrelated, merge=merge)


class TestRepositoryGetCommonAncestor:

    def test_get_common_ancestor_from_same_repo_existing(self, vcsbackend):
        target_repo = vcsbackend.create_repo(number_of_commits=5)

        expected_ancestor = target_repo[2].raw_id

        assert target_repo.get_common_ancestor(
            commit_id1=target_repo[2].raw_id,
            commit_id2=target_repo[4].raw_id,
            repo2=target_repo
        ) == expected_ancestor

        assert target_repo.get_common_ancestor(
            commit_id1=target_repo[4].raw_id,
            commit_id2=target_repo[2].raw_id,
            repo2=target_repo
        ) == expected_ancestor

    @pytest.mark.xfail_backends("svn")
    def test_get_common_ancestor_from_cloned_repo_existing(self, vcsbackend):
        target_repo = vcsbackend.create_repo(number_of_commits=5)
        source_repo = vcsbackend.clone_repo(target_repo)
        assert target_repo != source_repo

        vcsbackend.add_file(source_repo, 'newfile', 'somecontent')
        source_commit = source_repo.get_commit()

        expected_ancestor = target_repo[4].raw_id

        assert target_repo.get_common_ancestor(
            commit_id1=target_repo[4].raw_id,
            commit_id2=source_commit.raw_id,
            repo2=source_repo
        ) == expected_ancestor

        assert target_repo.get_common_ancestor(
            commit_id1=source_commit.raw_id,
            commit_id2=target_repo[4].raw_id,
            repo2=target_repo
        ) == expected_ancestor

    @pytest.mark.xfail_backends("svn")
    def test_get_common_ancestor_from_unrelated_repo_missing(self, vcsbackend):
        original = vcsbackend.create_repo(number_of_commits=5)
        unrelated = vcsbackend.create_repo(number_of_commits=5)
        assert original != unrelated

        assert original.get_common_ancestor(
            commit_id1=original[0].raw_id,
            commit_id2=unrelated[0].raw_id,
            repo2=unrelated
        ) == None

        assert original.get_common_ancestor(
            commit_id1=original[-1].raw_id,
            commit_id2=unrelated[-1].raw_id,
            repo2=unrelated
        ) == None


@pytest.mark.backends("git", "hg")
class TestRepositoryMerge:
    def prepare_for_success(self, vcsbackend):
        self.target_repo = vcsbackend.create_repo(number_of_commits=1)
        self.source_repo = vcsbackend.clone_repo(self.target_repo)
        vcsbackend.add_file(self.target_repo, 'README_MERGE1', 'Version 1')
        vcsbackend.add_file(self.source_repo, 'README_MERGE2', 'Version 2')
        imc = self.source_repo.in_memory_commit
        imc.add(FileNode('file_x', content=self.source_repo.name))
        imc.commit(
            message=u'Automatic commit from repo merge test',
            author=u'Automatic')
        self.target_commit = self.target_repo.get_commit()
        self.source_commit = self.source_repo.get_commit()
        # This only works for Git and Mercurial
        default_branch = self.target_repo.DEFAULT_BRANCH_NAME
        self.target_ref = Reference(
            'branch', default_branch, self.target_commit.raw_id)
        self.source_ref = Reference(
            'branch', default_branch, self.source_commit.raw_id)
        self.workspace = 'test-merge'

    def prepare_for_conflict(self, vcsbackend):
        self.target_repo = vcsbackend.create_repo(number_of_commits=1)
        self.source_repo = vcsbackend.clone_repo(self.target_repo)
        vcsbackend.add_file(self.target_repo, 'README_MERGE', 'Version 1')
        vcsbackend.add_file(self.source_repo, 'README_MERGE', 'Version 2')
        self.target_commit = self.target_repo.get_commit()
        self.source_commit = self.source_repo.get_commit()
        # This only works for Git and Mercurial
        default_branch = self.target_repo.DEFAULT_BRANCH_NAME
        self.target_ref = Reference(
            'branch', default_branch, self.target_commit.raw_id)
        self.source_ref = Reference(
            'branch', default_branch, self.source_commit.raw_id)
        self.workspace = 'test-merge'

    def test_merge_success(self, vcsbackend):
        self.prepare_for_success(vcsbackend)

        merge_response = self.target_repo.merge(
            self.target_ref, self.source_repo, self.source_ref, self.workspace,
            'test user', 'test@rhodecode.com', 'merge message 1',
            dry_run=False)
        expected_merge_response = MergeResponse(
            True, True, merge_response.merge_commit_id,
            MergeFailureReason.NONE)
        assert merge_response == expected_merge_response

        target_repo = backends.get_backend(vcsbackend.alias)(
            self.target_repo.path)
        target_commits = list(target_repo.get_commits())
        commit_ids = [c.raw_id for c in target_commits[:-1]]
        assert self.source_ref.commit_id in commit_ids
        assert self.target_ref.commit_id in commit_ids

        merge_commit = target_commits[-1]
        assert merge_commit.raw_id == merge_response.merge_commit_id
        assert merge_commit.message.strip() == 'merge message 1'
        assert merge_commit.author == 'test user <test@rhodecode.com>'

        # We call it twice so to make sure we can handle updates
        target_ref = Reference(
            self.target_ref.type, self.target_ref.name,
            merge_response.merge_commit_id)

        merge_response = target_repo.merge(
            target_ref, self.source_repo, self.source_ref, self.workspace,
            'test user', 'test@rhodecode.com', 'merge message 2',
            dry_run=False)
        expected_merge_response = MergeResponse(
            True, True, merge_response.merge_commit_id,
            MergeFailureReason.NONE)
        assert merge_response == expected_merge_response

        target_repo = backends.get_backend(
            vcsbackend.alias)(self.target_repo.path)
        merge_commit = target_repo.get_commit(merge_response.merge_commit_id)
        assert merge_commit.message.strip() == 'merge message 1'
        assert merge_commit.author == 'test user <test@rhodecode.com>'

    def test_merge_success_dry_run(self, vcsbackend):
        self.prepare_for_success(vcsbackend)
        expected_merge_response = MergeResponse(
            True, False, None, MergeFailureReason.NONE)

        merge_response = self.target_repo.merge(
            self.target_ref, self.source_repo, self.source_ref, self.workspace,
            dry_run=True)
        assert merge_response == expected_merge_response

        # We call it twice so to make sure we can handle updates
        merge_response = self.target_repo.merge(
            self.target_ref, self.source_repo, self.source_ref, self.workspace,
            dry_run=True)
        assert merge_response == expected_merge_response

    @pytest.mark.parametrize('dry_run', [True, False])
    def test_merge_conflict(self, vcsbackend, dry_run):
        self.prepare_for_conflict(vcsbackend)
        expected_merge_response = MergeResponse(
            False, False, None, MergeFailureReason.MERGE_FAILED)

        merge_response = self.target_repo.merge(
            self.target_ref, self.source_repo, self.source_ref, self.workspace,
            'test_user', 'test@rhodecode.com', 'test message', dry_run=dry_run)
        assert merge_response == expected_merge_response

        # We call it twice so to make sure we can handle updates
        merge_response = self.target_repo.merge(
            self.target_ref, self.source_repo, self.source_ref, self.workspace,
            'test_user', 'test@rhodecode.com', 'test message', dry_run=dry_run)
        assert merge_response == expected_merge_response

    def test_merge_target_is_not_head(self, vcsbackend):
        self.prepare_for_success(vcsbackend)
        expected_merge_response = MergeResponse(
            False, False, None, MergeFailureReason.TARGET_IS_NOT_HEAD)

        target_ref = Reference(
            self.target_ref.type, self.target_ref.name, '0' * 40)

        merge_response = self.target_repo.merge(
            target_ref, self.source_repo, self.source_ref, self.workspace,
            dry_run=True)

        assert merge_response == expected_merge_response

    def test_merge_missing_commit(self, vcsbackend):
        self.prepare_for_success(vcsbackend)
        expected_merge_response = MergeResponse(
            False, False, None, MergeFailureReason.MISSING_COMMIT)

        source_ref = Reference(
            self.source_ref.type, 'not_existing', self.source_ref.commit_id)

        merge_response = self.target_repo.merge(
            self.target_ref, self.source_repo, source_ref, self.workspace,
            dry_run=True)

        assert merge_response == expected_merge_response

    def test_merge_raises_exception(self, vcsbackend):
        self.prepare_for_success(vcsbackend)
        expected_merge_response = MergeResponse(
            False, False, None, MergeFailureReason.UNKNOWN)

        with mock.patch.object(self.target_repo, '_merge_repo',
                               side_effect=RepositoryError()):
            merge_response = self.target_repo.merge(
                self.target_ref, self.source_repo, self.source_ref,
                self.workspace, dry_run=True)

        assert merge_response == expected_merge_response

    def test_merge_invalid_user_name(self, vcsbackend):
        repo = vcsbackend.create_repo(number_of_commits=1)
        ref = Reference('branch', 'master', 'not_used')
        with pytest.raises(ValueError):
            repo.merge(ref, self, ref, 'workspace_id')

    def test_merge_invalid_user_email(self, vcsbackend):
        repo = vcsbackend.create_repo(number_of_commits=1)
        ref = Reference('branch', 'master', 'not_used')
        with pytest.raises(ValueError):
            repo.merge(ref, self, ref, 'workspace_id', 'user name')

    def test_merge_invalid_message(self, vcsbackend):
        repo = vcsbackend.create_repo(number_of_commits=1)
        ref = Reference('branch', 'master', 'not_used')
        with pytest.raises(ValueError):
            repo.merge(
                ref, self, ref, 'workspace_id', 'user name', 'user@email.com')


class TestRepositoryStrip(BackendTestMixin):
    recreate_repo_per_test = True

    @classmethod
    def _get_commits(cls):
        commits = [
            {
                'message': 'Initial commit',
                'author': 'Joe Doe <joe.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 20),
                'branch': 'master',
                'added': [
                    FileNode('foobar', content='foobar'),
                    FileNode('foobar2', content='foobar2'),
                ],
            },
        ]
        for x in xrange(10):
            commit_data = {
                'message': 'Changed foobar - commit%s' % x,
                'author': 'Jane Doe <jane.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 21, x),
                'branch': 'master',
                'changed': [
                    FileNode('foobar', 'FOOBAR - %s' % x),
                ],
            }
            commits.append(commit_data)
        return commits

    @pytest.mark.backends("git", "hg")
    def test_strip_commit(self):
        tip = self.repo.get_commit()
        assert tip.idx == 10
        self.repo.strip(tip.raw_id, self.repo.DEFAULT_BRANCH_NAME)

        tip = self.repo.get_commit()
        assert tip.idx == 9

    @pytest.mark.backends("git", "hg")
    def test_strip_multiple_commits(self):
        tip = self.repo.get_commit()
        assert tip.idx == 10

        old = self.repo.get_commit(commit_idx=5)
        self.repo.strip(old.raw_id, self.repo.DEFAULT_BRANCH_NAME)

        tip = self.repo.get_commit()
        assert tip.idx == 4


@pytest.mark.backends('hg', 'git')
class TestRepositoryPull:

    def test_pull(self, vcsbackend):
        source_repo = vcsbackend.repo
        target_repo = vcsbackend.create_repo()
        assert len(source_repo.commit_ids) > len(target_repo.commit_ids)

        target_repo.pull(source_repo.path)
        # Note: Get a fresh instance, avoids caching trouble
        target_repo = vcsbackend.backend(target_repo.path)
        assert len(source_repo.commit_ids) == len(target_repo.commit_ids)

    def test_pull_wrong_path(self, vcsbackend):
        target_repo = vcsbackend.create_repo()
        with pytest.raises(RepositoryError):
            target_repo.pull(target_repo.path + "wrong")

    def test_pull_specific_commits(self, vcsbackend):
        source_repo = vcsbackend.repo
        target_repo = vcsbackend.create_repo()

        second_commit = source_repo[1].raw_id
        if vcsbackend.alias == 'git':
            second_commit_ref = 'refs/test-refs/a'
            source_repo.set_refs(second_commit_ref, second_commit)

        target_repo.pull(source_repo.path, commit_ids=[second_commit])
        target_repo = vcsbackend.backend(target_repo.path)
        assert 2 == len(target_repo.commit_ids)
        assert second_commit == target_repo.get_commit().raw_id
