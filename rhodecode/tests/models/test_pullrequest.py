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
import textwrap

import rhodecode
from rhodecode.lib.utils2 import safe_unicode
from rhodecode.lib.vcs.backends import get_backend
from rhodecode.lib.vcs.backends.base import MergeResponse, MergeFailureReason
from rhodecode.lib.vcs.exceptions import RepositoryError
from rhodecode.lib.vcs.nodes import FileNode
from rhodecode.model.comment import ChangesetCommentsModel
from rhodecode.model.db import PullRequest, Session
from rhodecode.model.pull_request import PullRequestModel
from rhodecode.model.user import UserModel
from rhodecode.tests import TEST_USER_ADMIN_LOGIN


pytestmark = [
    pytest.mark.backends("git", "hg"),
]


class TestPullRequestModel:

    @pytest.fixture
    def pull_request(self, request, backend, pr_util):
        """
        A pull request combined with multiples patches.
        """
        BackendClass = get_backend(backend.alias)
        self.merge_patcher = mock.patch.object(BackendClass, 'merge')
        self.workspace_remove_patcher = mock.patch.object(
            BackendClass, 'cleanup_merge_workspace')

        self.workspace_remove_mock = self.workspace_remove_patcher.start()
        self.merge_mock = self.merge_patcher.start()
        self.comment_patcher = mock.patch(
            'rhodecode.model.changeset_status.ChangesetStatusModel.set_status')
        self.comment_patcher.start()
        self.notification_patcher = mock.patch(
            'rhodecode.model.notification.NotificationModel.create')
        self.notification_patcher.start()
        self.helper_patcher = mock.patch(
            'rhodecode.lib.helpers.url')
        self.helper_patcher.start()

        self.hook_patcher = mock.patch.object(PullRequestModel,
                                              '_trigger_pull_request_hook')
        self.hook_mock = self.hook_patcher.start()

        self.invalidation_patcher = mock.patch(
            'rhodecode.model.pull_request.ScmModel.mark_for_invalidation')
        self.invalidation_mock = self.invalidation_patcher.start()

        self.pull_request = pr_util.create_pull_request(
            mergeable=True, name_suffix=u'ąć')
        self.source_commit = self.pull_request.source_ref_parts.commit_id
        self.target_commit = self.pull_request.target_ref_parts.commit_id
        self.workspace_id = 'pr-%s' % self.pull_request.pull_request_id

        @request.addfinalizer
        def cleanup_pull_request():
            calls = [mock.call(
                self.pull_request, self.pull_request.author, 'create')]
            self.hook_mock.assert_has_calls(calls)

            self.workspace_remove_patcher.stop()
            self.merge_patcher.stop()
            self.comment_patcher.stop()
            self.notification_patcher.stop()
            self.helper_patcher.stop()
            self.hook_patcher.stop()
            self.invalidation_patcher.stop()

        return self.pull_request

    def test_get_all(self, pull_request):
        prs = PullRequestModel().get_all(pull_request.target_repo)
        assert isinstance(prs, list)
        assert len(prs) == 1

    def test_count_all(self, pull_request):
        pr_count = PullRequestModel().count_all(pull_request.target_repo)
        assert pr_count == 1

    def test_get_awaiting_review(self, pull_request):
        prs = PullRequestModel().get_awaiting_review(pull_request.target_repo)
        assert isinstance(prs, list)
        assert len(prs) == 1

    def test_count_awaiting_review(self, pull_request):
        pr_count = PullRequestModel().count_awaiting_review(
            pull_request.target_repo)
        assert pr_count == 1

    def test_get_awaiting_my_review(self, pull_request):
        PullRequestModel().update_reviewers(
            pull_request, [pull_request.author])
        prs = PullRequestModel().get_awaiting_my_review(
            pull_request.target_repo, user_id=pull_request.author.user_id)
        assert isinstance(prs, list)
        assert len(prs) == 1

    def test_count_awaiting_my_review(self, pull_request):
        PullRequestModel().update_reviewers(
            pull_request, [pull_request.author])
        pr_count = PullRequestModel().count_awaiting_my_review(
            pull_request.target_repo, user_id=pull_request.author.user_id)
        assert pr_count == 1

    def test_delete_calls_cleanup_merge(self, pull_request):
        PullRequestModel().delete(pull_request)

        self.workspace_remove_mock.assert_called_once_with(
            self.workspace_id)

    def test_close_calls_cleanup_and_hook(self, pull_request):
        PullRequestModel().close_pull_request(
            pull_request, pull_request.author)

        self.workspace_remove_mock.assert_called_once_with(
            self.workspace_id)
        self.hook_mock.assert_called_with(
            self.pull_request, self.pull_request.author, 'close')

    def test_merge_status(self, pull_request):
        self.merge_mock.return_value = MergeResponse(
            True, False, None, MergeFailureReason.NONE)

        assert pull_request._last_merge_source_rev is None
        assert pull_request._last_merge_target_rev is None
        assert pull_request._last_merge_status is None

        status, msg = PullRequestModel().merge_status(pull_request)
        assert status is True
        assert msg.eval() == 'This pull request can be automatically merged.'
        self.merge_mock.assert_called_once_with(
            pull_request.target_ref_parts,
            pull_request.source_repo.scm_instance(),
            pull_request.source_ref_parts, self.workspace_id, dry_run=True,
            use_rebase=False)

        assert pull_request._last_merge_source_rev == self.source_commit
        assert pull_request._last_merge_target_rev == self.target_commit
        assert pull_request._last_merge_status is MergeFailureReason.NONE

        self.merge_mock.reset_mock()
        status, msg = PullRequestModel().merge_status(pull_request)
        assert status is True
        assert msg.eval() == 'This pull request can be automatically merged.'
        assert self.merge_mock.called is False

    def test_merge_status_known_failure(self, pull_request):
        self.merge_mock.return_value = MergeResponse(
            False, False, None, MergeFailureReason.MERGE_FAILED)

        assert pull_request._last_merge_source_rev is None
        assert pull_request._last_merge_target_rev is None
        assert pull_request._last_merge_status is None

        status, msg = PullRequestModel().merge_status(pull_request)
        assert status is False
        assert (
            msg.eval() ==
            'This pull request cannot be merged because of conflicts.')
        self.merge_mock.assert_called_once_with(
            pull_request.target_ref_parts,
            pull_request.source_repo.scm_instance(),
            pull_request.source_ref_parts, self.workspace_id, dry_run=True,
            use_rebase=False)

        assert pull_request._last_merge_source_rev == self.source_commit
        assert pull_request._last_merge_target_rev == self.target_commit
        assert (
            pull_request._last_merge_status is MergeFailureReason.MERGE_FAILED)

        self.merge_mock.reset_mock()
        status, msg = PullRequestModel().merge_status(pull_request)
        assert status is False
        assert (
            msg.eval() ==
            'This pull request cannot be merged because of conflicts.')
        assert self.merge_mock.called is False

    def test_merge_status_unknown_failure(self, pull_request):
        self.merge_mock.return_value = MergeResponse(
            False, False, None, MergeFailureReason.UNKNOWN)

        assert pull_request._last_merge_source_rev is None
        assert pull_request._last_merge_target_rev is None
        assert pull_request._last_merge_status is None

        status, msg = PullRequestModel().merge_status(pull_request)
        assert status is False
        assert msg.eval() == (
            'This pull request cannot be merged because of an unhandled'
            ' exception.')
        self.merge_mock.assert_called_once_with(
            pull_request.target_ref_parts,
            pull_request.source_repo.scm_instance(),
            pull_request.source_ref_parts, self.workspace_id, dry_run=True,
            use_rebase=False)

        assert pull_request._last_merge_source_rev is None
        assert pull_request._last_merge_target_rev is None
        assert pull_request._last_merge_status is None

        self.merge_mock.reset_mock()
        status, msg = PullRequestModel().merge_status(pull_request)
        assert status is False
        assert msg.eval() == (
            'This pull request cannot be merged because of an unhandled'
            ' exception.')
        assert self.merge_mock.called is True

    def test_merge_status_when_target_is_locked(self, pull_request):
        pull_request.target_repo.locked = [1, u'12345.50', 'lock_web']
        status, msg = PullRequestModel().merge_status(pull_request)
        assert status is False
        assert msg.eval() == (
            'This pull request cannot be merged because the target repository'
            ' is locked.')

    def test_merge_status_requirements_check_target(self, pull_request):

        def has_largefiles(self, repo):
            return repo == pull_request.source_repo

        patcher = mock.patch.object(
            PullRequestModel, '_has_largefiles', has_largefiles)
        with patcher:
            status, msg = PullRequestModel().merge_status(pull_request)

        assert status is False
        assert msg == 'Target repository large files support is disabled.'

    def test_merge_status_requirements_check_source(self, pull_request):

        def has_largefiles(self, repo):
            return repo == pull_request.target_repo

        patcher = mock.patch.object(
            PullRequestModel, '_has_largefiles', has_largefiles)
        with patcher:
            status, msg = PullRequestModel().merge_status(pull_request)

        assert status is False
        assert msg == 'Source repository large files support is disabled.'

    def test_merge(self, pull_request, merge_extras):
        user = UserModel().get_by_username(TEST_USER_ADMIN_LOGIN)
        self.merge_mock.return_value = MergeResponse(
            True, True,
            '6126b7bfcc82ad2d3deaee22af926b082ce54cc6',
            MergeFailureReason.NONE)

        merge_extras['repository'] = pull_request.target_repo.repo_name
        PullRequestModel().merge(
            pull_request, pull_request.author, extras=merge_extras)

        message = (
            u'Merge pull request #{pr_id} from {source_repo} {source_ref_name}'
            u'\n\n {pr_title}'.format(
                pr_id=pull_request.pull_request_id,
                source_repo=safe_unicode(
                    pull_request.source_repo.scm_instance().name),
                source_ref_name=pull_request.source_ref_parts.name,
                pr_title=safe_unicode(pull_request.title)
            )
        )
        self.merge_mock.assert_called_once_with(
            pull_request.target_ref_parts,
            pull_request.source_repo.scm_instance(),
            pull_request.source_ref_parts, self.workspace_id,
            user_name=user.username, user_email=user.email, message=message,
            use_rebase=False
        )
        self.invalidation_mock.assert_called_once_with(
            pull_request.target_repo.repo_name)

        self.hook_mock.assert_called_with(
            self.pull_request, self.pull_request.author, 'merge')

        pull_request = PullRequest.get(pull_request.pull_request_id)
        assert (
            pull_request.merge_rev ==
            '6126b7bfcc82ad2d3deaee22af926b082ce54cc6')

    def test_merge_failed(self, pull_request, merge_extras):
        user = UserModel().get_by_username(TEST_USER_ADMIN_LOGIN)
        self.merge_mock.return_value = MergeResponse(
            False, False,
            '6126b7bfcc82ad2d3deaee22af926b082ce54cc6',
            MergeFailureReason.MERGE_FAILED)

        merge_extras['repository'] = pull_request.target_repo.repo_name
        PullRequestModel().merge(
            pull_request, pull_request.author, extras=merge_extras)

        message = (
            u'Merge pull request #{pr_id} from {source_repo} {source_ref_name}'
            u'\n\n {pr_title}'.format(
                pr_id=pull_request.pull_request_id,
                source_repo=safe_unicode(
                    pull_request.source_repo.scm_instance().name),
                source_ref_name=pull_request.source_ref_parts.name,
                pr_title=safe_unicode(pull_request.title)
            )
        )
        self.merge_mock.assert_called_once_with(
            pull_request.target_ref_parts,
            pull_request.source_repo.scm_instance(),
            pull_request.source_ref_parts, self.workspace_id,
            user_name=user.username, user_email=user.email, message=message,
            use_rebase=False
        )

        pull_request = PullRequest.get(pull_request.pull_request_id)
        assert self.invalidation_mock.called is False
        assert pull_request.merge_rev is None

    def test_get_commit_ids(self, pull_request):
        # The PR has been not merget yet, so expect an exception
        with pytest.raises(ValueError):
            PullRequestModel()._get_commit_ids(pull_request)

        # Merge revision is in the revisions list
        pull_request.merge_rev = pull_request.revisions[0]
        commit_ids = PullRequestModel()._get_commit_ids(pull_request)
        assert commit_ids == pull_request.revisions

        # Merge revision is not in the revisions list
        pull_request.merge_rev = 'f000' * 10
        commit_ids = PullRequestModel()._get_commit_ids(pull_request)
        assert commit_ids == pull_request.revisions + [pull_request.merge_rev]

    def test_get_diff_from_pr_version(self, pull_request):
        diff = PullRequestModel()._get_diff_from_pr_or_version(
            pull_request, context=6)
        assert 'file_1' in diff.raw


class TestIntegrationMerge(object):
    @pytest.mark.parametrize('extra_config', (
        {'vcs.hooks.protocol': 'http', 'vcs.hooks.direct_calls': False},
        {'vcs.hooks.protocol': 'Pyro4', 'vcs.hooks.direct_calls': False},
    ))
    def test_merge_triggers_push_hooks(
            self, pr_util, user_admin, capture_rcextensions, merge_extras,
            extra_config):
        pull_request = pr_util.create_pull_request(
            approved=True, mergeable=True)
        # TODO: johbo: Needed for sqlite, try to find an automatic way for it
        merge_extras['repository'] = pull_request.target_repo.repo_name
        Session().commit()

        with mock.patch.dict(rhodecode.CONFIG, extra_config, clear=False):
            merge_state = PullRequestModel().merge(
                pull_request, user_admin, extras=merge_extras)

        assert merge_state.executed
        assert 'pre_push' in capture_rcextensions
        assert 'post_push' in capture_rcextensions

    def test_merge_can_be_rejected_by_pre_push_hook(
            self, pr_util, user_admin, capture_rcextensions, merge_extras):
        pull_request = pr_util.create_pull_request(
            approved=True, mergeable=True)
        # TODO: johbo: Needed for sqlite, try to find an automatic way for it
        merge_extras['repository'] = pull_request.target_repo.repo_name
        Session().commit()

        with mock.patch('rhodecode.EXTENSIONS.PRE_PUSH_HOOK') as pre_pull:
            pre_pull.side_effect = RepositoryError("Disallow push!")
            merge_status = PullRequestModel().merge(
                pull_request, user_admin, extras=merge_extras)

        assert not merge_status.executed
        assert 'pre_push' not in capture_rcextensions
        assert 'post_push' not in capture_rcextensions

    def test_merge_fails_if_target_is_locked(
            self, pr_util, user_regular, merge_extras):
        pull_request = pr_util.create_pull_request(
            approved=True, mergeable=True)
        locked_by = [user_regular.user_id + 1, 12345.50, 'lock_web']
        pull_request.target_repo.locked = locked_by
        # TODO: johbo: Check if this can work based on the database, currently
        # all data is pre-computed, that's why just updating the DB is not
        # enough.
        merge_extras['locked_by'] = locked_by
        merge_extras['repository'] = pull_request.target_repo.repo_name
        # TODO: johbo: Needed for sqlite, try to find an automatic way for it
        Session().commit()
        merge_status = PullRequestModel().merge(
            pull_request, user_regular, extras=merge_extras)
        assert not merge_status.executed


@pytest.mark.parametrize('use_outdated, inlines_count, outdated_count', [
    (False, 1, 0),
    (True, 0, 1),
])
def test_outdated_comments(
        pr_util, use_outdated, inlines_count, outdated_count):
    pull_request = pr_util.create_pull_request()
    pr_util.create_inline_comment(file_path='not_in_updated_diff')

    with outdated_comments_patcher(use_outdated) as outdated_comment_mock:
        pr_util.add_one_commit()
        assert_inline_comments(
            pull_request, visible=inlines_count, outdated=outdated_count)
    outdated_comment_mock.assert_called_with(pull_request)


@pytest.fixture
def merge_extras(user_regular):
    """
    Context for the vcs operation when running a merge.
    """
    extras = {
        'ip': '127.0.0.1',
        'username': user_regular.username,
        'action': 'push',
        'repository': 'fake_target_repo_name',
        'scm': 'git',
        'config': 'fake_config_ini_path',
        'make_lock': None,
        'locked_by': [None, None, None],
        'server_url': 'http://test.example.com:5000',
        'hooks': ['push', 'pull'],
    }
    return extras


class TestUpdateCommentHandling(object):

    @pytest.fixture(autouse=True, scope='class')
    def enable_outdated_comments(self, request, pylonsapp):
        config_patch = mock.patch.dict(
            'rhodecode.CONFIG', {'rhodecode_use_outdated_comments': True})
        config_patch.start()

        @request.addfinalizer
        def cleanup():
            config_patch.stop()

    def test_comment_stays_unflagged_on_unchanged_diff(self, pr_util):
        commits = [
            {'message': 'a'},
            {'message': 'b', 'added': [FileNode('file_b', 'test_content\n')]},
            {'message': 'c', 'added': [FileNode('file_c', 'test_content\n')]},
        ]
        pull_request = pr_util.create_pull_request(
            commits=commits, target_head='a', source_head='b', revisions=['b'])
        pr_util.create_inline_comment(file_path='file_b')
        pr_util.add_one_commit(head='c')

        assert_inline_comments(pull_request, visible=1, outdated=0)

    def test_comment_stays_unflagged_on_change_above(self, pr_util):
        original_content = ''.join(
            ['line {}\n'.format(x) for x in range(1, 11)])
        updated_content = 'new_line_at_top\n' + original_content
        commits = [
            {'message': 'a'},
            {'message': 'b', 'added': [FileNode('file_b', original_content)]},
            {'message': 'c', 'changed': [FileNode('file_b', updated_content)]},
        ]
        pull_request = pr_util.create_pull_request(
            commits=commits, target_head='a', source_head='b', revisions=['b'])

        with outdated_comments_patcher():
            comment = pr_util.create_inline_comment(
                line_no=u'n8', file_path='file_b')
            pr_util.add_one_commit(head='c')

        assert_inline_comments(pull_request, visible=1, outdated=0)
        assert comment.line_no == u'n9'

    def test_comment_stays_unflagged_on_change_below(self, pr_util):
        original_content = ''.join(['line {}\n'.format(x) for x in range(10)])
        updated_content = original_content + 'new_line_at_end\n'
        commits = [
            {'message': 'a'},
            {'message': 'b', 'added': [FileNode('file_b', original_content)]},
            {'message': 'c', 'changed': [FileNode('file_b', updated_content)]},
        ]
        pull_request = pr_util.create_pull_request(
            commits=commits, target_head='a', source_head='b', revisions=['b'])
        pr_util.create_inline_comment(file_path='file_b')
        pr_util.add_one_commit(head='c')

        assert_inline_comments(pull_request, visible=1, outdated=0)

    @pytest.mark.parametrize('line_no', ['n4', 'o4', 'n10', 'o9'])
    def test_comment_flagged_on_change_around_context(self, pr_util, line_no):
        base_lines = ['line {}\n'.format(x) for x in range(1, 13)]
        change_lines = list(base_lines)
        change_lines.insert(6, 'line 6a added\n')

        # Changes on the last line of sight
        update_lines = list(change_lines)
        update_lines[0] = 'line 1 changed\n'
        update_lines[-1] = 'line 12 changed\n'

        def file_b(lines):
            return FileNode('file_b', ''.join(lines))

        commits = [
            {'message': 'a', 'added': [file_b(base_lines)]},
            {'message': 'b', 'changed': [file_b(change_lines)]},
            {'message': 'c', 'changed': [file_b(update_lines)]},
        ]

        pull_request = pr_util.create_pull_request(
            commits=commits, target_head='a', source_head='b', revisions=['b'])
        pr_util.create_inline_comment(line_no=line_no, file_path='file_b')

        with outdated_comments_patcher():
            pr_util.add_one_commit(head='c')
            assert_inline_comments(pull_request, visible=0, outdated=1)

    @pytest.mark.parametrize("change, content", [
        ('changed', 'changed\n'),
        ('removed', ''),
    ], ids=['changed', 'removed'])
    def test_comment_flagged_on_change(self, pr_util, change, content):
        commits = [
            {'message': 'a'},
            {'message': 'b', 'added': [FileNode('file_b', 'test_content\n')]},
            {'message': 'c', change: [FileNode('file_b', content)]},
        ]
        pull_request = pr_util.create_pull_request(
            commits=commits, target_head='a', source_head='b', revisions=['b'])
        pr_util.create_inline_comment(file_path='file_b')

        with outdated_comments_patcher():
            pr_util.add_one_commit(head='c')
            assert_inline_comments(pull_request, visible=0, outdated=1)


class TestUpdateChangedFiles(object):

    def test_no_changes_on_unchanged_diff(self, pr_util):
        commits = [
            {'message': 'a'},
            {'message': 'b',
             'added': [FileNode('file_b', 'test_content b\n')]},
            {'message': 'c',
             'added': [FileNode('file_c', 'test_content c\n')]},
        ]
        # open a PR from a to b, adding file_b
        pull_request = pr_util.create_pull_request(
            commits=commits, target_head='a', source_head='b', revisions=['b'],
            name_suffix='per-file-review')

        # modify PR adding new file file_c
        pr_util.add_one_commit(head='c')

        assert_pr_file_changes(
            pull_request,
            added=['file_c'],
            modified=[],
            removed=[])

    def test_modify_and_undo_modification_diff(self, pr_util):
        commits = [
            {'message': 'a'},
            {'message': 'b',
             'added': [FileNode('file_b', 'test_content b\n')]},
            {'message': 'c',
             'changed': [FileNode('file_b', 'test_content b modified\n')]},
            {'message': 'd',
             'changed': [FileNode('file_b', 'test_content b\n')]},
        ]
        # open a PR from a to b, adding file_b
        pull_request = pr_util.create_pull_request(
            commits=commits, target_head='a', source_head='b', revisions=['b'],
            name_suffix='per-file-review')

        # modify PR modifying file file_b
        pr_util.add_one_commit(head='c')

        assert_pr_file_changes(
            pull_request,
            added=[],
            modified=['file_b'],
            removed=[])

        # move the head again to d, which rollbacks change,
        # meaning we should indicate no changes
        pr_util.add_one_commit(head='d')

        assert_pr_file_changes(
            pull_request,
            added=[],
            modified=[],
            removed=[])

    def test_updated_all_files_in_pr(self, pr_util):
        commits = [
            {'message': 'a'},
            {'message': 'b', 'added': [
                FileNode('file_a', 'test_content a\n'),
                FileNode('file_b', 'test_content b\n'),
                FileNode('file_c', 'test_content c\n')]},
            {'message': 'c', 'changed': [
                FileNode('file_a', 'test_content a changed\n'),
                FileNode('file_b', 'test_content b changed\n'),
                FileNode('file_c', 'test_content c changed\n')]},
        ]
        # open a PR from a to b, changing 3 files
        pull_request = pr_util.create_pull_request(
            commits=commits, target_head='a', source_head='b', revisions=['b'],
            name_suffix='per-file-review')

        pr_util.add_one_commit(head='c')

        assert_pr_file_changes(
            pull_request,
            added=[],
            modified=['file_a', 'file_b', 'file_c'],
            removed=[])

    def test_updated_and_removed_all_files_in_pr(self, pr_util):
        commits = [
            {'message': 'a'},
            {'message': 'b', 'added': [
                FileNode('file_a', 'test_content a\n'),
                FileNode('file_b', 'test_content b\n'),
                FileNode('file_c', 'test_content c\n')]},
            {'message': 'c', 'removed': [
                FileNode('file_a', 'test_content a changed\n'),
                FileNode('file_b', 'test_content b changed\n'),
                FileNode('file_c', 'test_content c changed\n')]},
        ]
        # open a PR from a to b, removing 3 files
        pull_request = pr_util.create_pull_request(
            commits=commits, target_head='a', source_head='b', revisions=['b'],
            name_suffix='per-file-review')

        pr_util.add_one_commit(head='c')

        assert_pr_file_changes(
            pull_request,
            added=[],
            modified=[],
            removed=['file_a', 'file_b', 'file_c'])


def test_update_writes_snapshot_into_pull_request_version(pr_util):
    model = PullRequestModel()
    pull_request = pr_util.create_pull_request()
    pr_util.update_source_repository()

    model.update_commits(pull_request)

    # Expect that it has a version entry now
    assert len(model.get_versions(pull_request)) == 1


def test_update_skips_new_version_if_unchanged(pr_util):
    pull_request = pr_util.create_pull_request()
    model = PullRequestModel()
    model.update_commits(pull_request)

    # Expect that it still has no versions
    assert len(model.get_versions(pull_request)) == 0


def test_update_assigns_comments_to_the_new_version(pr_util):
    model = PullRequestModel()
    pull_request = pr_util.create_pull_request()
    comment = pr_util.create_comment()
    pr_util.update_source_repository()

    model.update_commits(pull_request)

    # Expect that the comment is linked to the pr version now
    assert comment.pull_request_version == model.get_versions(pull_request)[0]


def test_update_adds_a_comment_to_the_pull_request_about_the_change(pr_util):
    model = PullRequestModel()
    pull_request = pr_util.create_pull_request()
    pr_util.update_source_repository()
    pr_util.update_source_repository()

    model.update_commits(pull_request)

    # Expect to find a new comment about the change
    expected_message = textwrap.dedent(
        """\
        Auto status change to |under_review|

        .. role:: added
        .. role:: removed
        .. parsed-literal::

          Changed commits:
            * :added:`1 added`
            * :removed:`0 removed`

          Changed files:
            * `A file_2 <#a_c--92ed3b5f07b4>`_

        .. |under_review| replace:: *"Under Review"*"""
    )
    pull_request_comments = sorted(
        pull_request.comments, key=lambda c: c.modified_at)
    update_comment = pull_request_comments[-1]
    assert update_comment.text == expected_message


def test_create_version_from_snapshot_updates_attributes(pr_util):
    pull_request = pr_util.create_pull_request()

    # Avoiding default values
    pull_request.status = PullRequest.STATUS_CLOSED
    pull_request._last_merge_source_rev = "0" * 40
    pull_request._last_merge_target_rev = "1" * 40
    pull_request._last_merge_status = 1
    pull_request.merge_rev = "2" * 40

    # Remember automatic values
    created_on = pull_request.created_on
    updated_on = pull_request.updated_on

    # Create a new version of the pull request
    version = PullRequestModel()._create_version_from_snapshot(pull_request)

    # Check attributes
    assert version.title == pr_util.create_parameters['title']
    assert version.description == pr_util.create_parameters['description']
    assert version.status == PullRequest.STATUS_CLOSED
    assert version.created_on == created_on
    assert version.updated_on == updated_on
    assert version.user_id == pull_request.user_id
    assert version.revisions == pr_util.create_parameters['revisions']
    assert version.source_repo == pr_util.source_repository
    assert version.source_ref == pr_util.create_parameters['source_ref']
    assert version.target_repo == pr_util.target_repository
    assert version.target_ref == pr_util.create_parameters['target_ref']
    assert version._last_merge_source_rev == pull_request._last_merge_source_rev
    assert version._last_merge_target_rev == pull_request._last_merge_target_rev
    assert version._last_merge_status == pull_request._last_merge_status
    assert version.merge_rev == pull_request.merge_rev
    assert version.pull_request == pull_request


def test_link_comments_to_version_only_updates_unlinked_comments(pr_util):
    version1 = pr_util.create_version_of_pull_request()
    comment_linked = pr_util.create_comment(linked_to=version1)
    comment_unlinked = pr_util.create_comment()
    version2 = pr_util.create_version_of_pull_request()

    PullRequestModel()._link_comments_to_version(version2)

    # Expect that only the new comment is linked to version2
    assert (
        comment_unlinked.pull_request_version_id ==
        version2.pull_request_version_id)
    assert (
        comment_linked.pull_request_version_id ==
        version1.pull_request_version_id)
    assert (
        comment_unlinked.pull_request_version_id !=
        comment_linked.pull_request_version_id)


def test_calculate_commits():
    change = PullRequestModel()._calculate_commit_id_changes(
        set([1, 2, 3]), set([1, 3, 4, 5]))
    assert (set([4, 5]), set([1, 3]), set([2])) == (
        change.added, change.common, change.removed)


def assert_inline_comments(pull_request, visible=None, outdated=None):
    if visible is not None:
        inline_comments = ChangesetCommentsModel().get_inline_comments(
            pull_request.target_repo.repo_id, pull_request=pull_request)
        assert len(inline_comments) == visible
    if outdated is not None:
        outdated_comments = ChangesetCommentsModel().get_outdated_comments(
            pull_request.target_repo.repo_id, pull_request)
        assert len(outdated_comments) == outdated


def assert_pr_file_changes(
        pull_request, added=None, modified=None, removed=None):
    pr_versions = PullRequestModel().get_versions(pull_request)
    # always use first version, ie original PR to calculate changes
    pull_request_version = pr_versions[0]
    old_diff_data, new_diff_data = PullRequestModel()._generate_update_diffs(
        pull_request, pull_request_version)
    file_changes = PullRequestModel()._calculate_file_changes(
        old_diff_data, new_diff_data)

    assert added == file_changes.added, \
        'expected added:%s vs value:%s' % (added, file_changes.added)
    assert modified == file_changes.modified, \
        'expected modified:%s vs value:%s' % (modified, file_changes.modified)
    assert removed == file_changes.removed, \
        'expected removed:%s vs value:%s' % (removed, file_changes.removed)


def outdated_comments_patcher(use_outdated=True):
    return mock.patch.object(
        ChangesetCommentsModel, 'use_outdated_comments',
        return_value=use_outdated)
