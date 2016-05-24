# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016  RhodeCode GmbH
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


"""
pull request model for RhodeCode
"""

from collections import namedtuple
import json
import logging
import datetime

from pylons.i18n.translation import _
from pylons.i18n.translation import lazy_ugettext

import rhodecode
from rhodecode.lib import helpers as h, hooks_utils, diffs
from rhodecode.lib.compat import OrderedDict
from rhodecode.lib.hooks_daemon import prepare_callback_daemon
from rhodecode.lib.markup_renderer import (
    DEFAULT_COMMENTS_RENDERER, RstTemplateRenderer)
from rhodecode.lib.utils import action_logger
from rhodecode.lib.utils2 import safe_unicode, safe_str, md5_safe
from rhodecode.lib.vcs.backends.base import (
    Reference, MergeResponse, MergeFailureReason)
from rhodecode.lib.vcs.exceptions import (
    CommitDoesNotExistError, EmptyRepositoryError)
from rhodecode.model import BaseModel
from rhodecode.model.changeset_status import ChangesetStatusModel
from rhodecode.model.comment import ChangesetCommentsModel
from rhodecode.model.db import (
    PullRequest, PullRequestReviewers, Notification, ChangesetStatus,
    PullRequestVersion, ChangesetComment)
from rhodecode.model.meta import Session
from rhodecode.model.notification import NotificationModel, \
    EmailNotificationModel
from rhodecode.model.scm import ScmModel
from rhodecode.model.settings import VcsSettingsModel


log = logging.getLogger(__name__)


class PullRequestModel(BaseModel):

    cls = PullRequest

    DIFF_CONTEXT = 3

    MERGE_STATUS_MESSAGES = {
        MergeFailureReason.NONE: lazy_ugettext(
            'This pull request can be automatically merged.'),
        MergeFailureReason.UNKNOWN: lazy_ugettext(
            'This pull request cannot be merged because of an unhandled'
            ' exception.'),
        MergeFailureReason.MERGE_FAILED: lazy_ugettext(
            'This pull request cannot be merged because of conflicts.'),
        MergeFailureReason.PUSH_FAILED: lazy_ugettext(
            'This pull request could not be merged because push to target'
            ' failed.'),
        MergeFailureReason.TARGET_IS_NOT_HEAD: lazy_ugettext(
            'This pull request cannot be merged because the target is not a'
            ' head.'),
        MergeFailureReason.HG_SOURCE_HAS_MORE_BRANCHES: lazy_ugettext(
            'This pull request cannot be merged because the source contains'
            ' more branches than the target.'),
        MergeFailureReason.HG_TARGET_HAS_MULTIPLE_HEADS: lazy_ugettext(
            'This pull request cannot be merged because the target has'
            ' multiple heads.'),
        MergeFailureReason.TARGET_IS_LOCKED: lazy_ugettext(
            'This pull request cannot be merged because the target repository'
            ' is locked.'),
        MergeFailureReason.MISSING_COMMIT: lazy_ugettext(
            'This pull request cannot be merged because the target or the '
            'source reference is missing.'),
    }

    def __get_pull_request(self, pull_request):
        return self._get_instance(PullRequest, pull_request)

    def _check_perms(self, perms, pull_request, user, api=False):
        if not api:
            return h.HasRepoPermissionAny(*perms)(
                user=user, repo_name=pull_request.target_repo.repo_name)
        else:
            return h.HasRepoPermissionAnyApi(*perms)(
                user=user, repo_name=pull_request.target_repo.repo_name)

    def check_user_read(self, pull_request, user, api=False):
        _perms = ('repository.admin', 'repository.write', 'repository.read',)
        return self._check_perms(_perms, pull_request, user, api)

    def check_user_merge(self, pull_request, user, api=False):
        _perms = ('repository.admin', 'repository.write', 'hg.admin',)
        return self._check_perms(_perms, pull_request, user, api)

    def check_user_update(self, pull_request, user, api=False):
        owner = user.user_id == pull_request.user_id
        return self.check_user_merge(pull_request, user, api) or owner

    def check_user_change_status(self, pull_request, user, api=False):
        reviewer = user.user_id in [x.user_id for x in
                                    pull_request.reviewers]
        return self.check_user_update(pull_request, user, api) or reviewer

    def get(self, pull_request):
        return self.__get_pull_request(pull_request)

    def _prepare_get_all_query(self, repo_name, source=False, statuses=None,
                               opened_by=None, order_by=None,
                               order_dir='desc'):
        repo = self._get_repo(repo_name)
        q = PullRequest.query()
        # source or target
        if source:
            q = q.filter(PullRequest.source_repo == repo)
        else:
            q = q.filter(PullRequest.target_repo == repo)

        # closed,opened
        if statuses:
            q = q.filter(PullRequest.status.in_(statuses))

        # opened by filter
        if opened_by:
            q = q.filter(PullRequest.user_id.in_(opened_by))

        if order_by:
            order_map = {
                'name_raw': PullRequest.pull_request_id,
                'title': PullRequest.title,
                'updated_on_raw': PullRequest.updated_on
            }
            if order_dir == 'asc':
                q = q.order_by(order_map[order_by].asc())
            else:
                q = q.order_by(order_map[order_by].desc())

        return q

    def count_all(self, repo_name, source=False, statuses=None,
                  opened_by=None):
        """
        Count the number of pull requests for a specific repository.

        :param repo_name: target or source repo
        :param source: boolean flag to specify if repo_name refers to source
        :param statuses: list of pull request statuses
        :param opened_by: author user of the pull request
        :returns: int number of pull requests
        """
        q = self._prepare_get_all_query(
            repo_name, source=source, statuses=statuses, opened_by=opened_by)

        return q.count()

    def get_all(self, repo_name, source=False, statuses=None, opened_by=None,
                offset=0, length=None, order_by=None, order_dir='desc'):
        """
        Get all pull requests for a specific repository.

        :param repo_name: target or source repo
        :param source: boolean flag to specify if repo_name refers to source
        :param statuses: list of pull request statuses
        :param opened_by: author user of the pull request
        :param offset: pagination offset
        :param length: length of returned list
        :param order_by: order of the returned list
        :param order_dir: 'asc' or 'desc' ordering direction
        :returns: list of pull requests
        """
        q = self._prepare_get_all_query(
            repo_name, source=source, statuses=statuses, opened_by=opened_by,
            order_by=order_by, order_dir=order_dir)

        if length:
            pull_requests = q.limit(length).offset(offset).all()
        else:
            pull_requests = q.all()

        return pull_requests

    def count_awaiting_review(self, repo_name, source=False, statuses=None,
                              opened_by=None):
        """
        Count the number of pull requests for a specific repository that are
        awaiting review.

        :param repo_name: target or source repo
        :param source: boolean flag to specify if repo_name refers to source
        :param statuses: list of pull request statuses
        :param opened_by: author user of the pull request
        :returns: int number of pull requests
        """
        pull_requests = self.get_awaiting_review(
            repo_name, source=source, statuses=statuses, opened_by=opened_by)

        return len(pull_requests)

    def get_awaiting_review(self, repo_name, source=False, statuses=None,
                            opened_by=None, offset=0, length=None,
                            order_by=None, order_dir='desc'):
        """
        Get all pull requests for a specific repository that are awaiting
        review.

        :param repo_name: target or source repo
        :param source: boolean flag to specify if repo_name refers to source
        :param statuses: list of pull request statuses
        :param opened_by: author user of the pull request
        :param offset: pagination offset
        :param length: length of returned list
        :param order_by: order of the returned list
        :param order_dir: 'asc' or 'desc' ordering direction
        :returns: list of pull requests
        """
        pull_requests = self.get_all(
            repo_name, source=source, statuses=statuses, opened_by=opened_by,
            order_by=order_by, order_dir=order_dir)

        _filtered_pull_requests = []
        for pr in pull_requests:
            status = pr.calculated_review_status()
            if status in [ChangesetStatus.STATUS_NOT_REVIEWED,
                          ChangesetStatus.STATUS_UNDER_REVIEW]:
                _filtered_pull_requests.append(pr)
        if length:
            return _filtered_pull_requests[offset:offset+length]
        else:
            return _filtered_pull_requests

    def count_awaiting_my_review(self, repo_name, source=False, statuses=None,
                                 opened_by=None, user_id=None):
        """
        Count the number of pull requests for a specific repository that are
        awaiting review from a specific user.

        :param repo_name: target or source repo
        :param source: boolean flag to specify if repo_name refers to source
        :param statuses: list of pull request statuses
        :param opened_by: author user of the pull request
        :param user_id: reviewer user of the pull request
        :returns: int number of pull requests
        """
        pull_requests = self.get_awaiting_my_review(
            repo_name, source=source, statuses=statuses, opened_by=opened_by,
            user_id=user_id)

        return len(pull_requests)

    def get_awaiting_my_review(self, repo_name, source=False, statuses=None,
                               opened_by=None, user_id=None, offset=0,
                               length=None, order_by=None, order_dir='desc'):
        """
        Get all pull requests for a specific repository that are awaiting
        review from a specific user.

        :param repo_name: target or source repo
        :param source: boolean flag to specify if repo_name refers to source
        :param statuses: list of pull request statuses
        :param opened_by: author user of the pull request
        :param user_id: reviewer user of the pull request
        :param offset: pagination offset
        :param length: length of returned list
        :param order_by: order of the returned list
        :param order_dir: 'asc' or 'desc' ordering direction
        :returns: list of pull requests
        """
        pull_requests = self.get_all(
            repo_name, source=source, statuses=statuses, opened_by=opened_by,
            order_by=order_by, order_dir=order_dir)

        _my = PullRequestModel().get_not_reviewed(user_id)
        my_participation = []
        for pr in pull_requests:
            if pr in _my:
                my_participation.append(pr)
        _filtered_pull_requests = my_participation
        if length:
            return _filtered_pull_requests[offset:offset+length]
        else:
            return _filtered_pull_requests

    def get_not_reviewed(self, user_id):
        return [
            x.pull_request for x in PullRequestReviewers.query().filter(
                PullRequestReviewers.user_id == user_id).all()
        ]

    def get_versions(self, pull_request):
        """
        returns version of pull request sorted by ID descending
        """
        return PullRequestVersion.query()\
            .filter(PullRequestVersion.pull_request == pull_request)\
            .order_by(PullRequestVersion.pull_request_version_id.asc())\
            .all()

    def create(self, created_by, source_repo, source_ref, target_repo,
        target_ref, revisions, reviewers, title, description=None):
        created_by_user = self._get_user(created_by)
        source_repo = self._get_repo(source_repo)
        target_repo = self._get_repo(target_repo)

        pull_request = PullRequest()
        pull_request.source_repo = source_repo
        pull_request.source_ref = source_ref
        pull_request.target_repo = target_repo
        pull_request.target_ref = target_ref
        pull_request.revisions = revisions
        pull_request.title = title
        pull_request.description = description
        pull_request.author = created_by_user

        Session().add(pull_request)
        Session().flush()

        # members / reviewers
        for user_id in set(reviewers):
            user = self._get_user(user_id)
            reviewer = PullRequestReviewers(user, pull_request)
            Session().add(reviewer)

        # Set approval status to "Under Review" for all commits which are
        # part of this pull request.
        ChangesetStatusModel().set_status(
            repo=target_repo,
            status=ChangesetStatus.STATUS_UNDER_REVIEW,
            user=created_by_user,
            pull_request=pull_request
        )

        self.notify_reviewers(pull_request, reviewers)
        self._trigger_pull_request_hook(
            pull_request, created_by_user, 'create')

        return pull_request

    def _trigger_pull_request_hook(self, pull_request, user, action):
        pull_request = self.__get_pull_request(pull_request)
        target_scm = pull_request.target_repo.scm_instance()
        if action == 'create':
            trigger_hook = hooks_utils.trigger_log_create_pull_request_hook
        elif action == 'merge':
            trigger_hook = hooks_utils.trigger_log_merge_pull_request_hook
        elif action == 'close':
            trigger_hook = hooks_utils.trigger_log_close_pull_request_hook
        elif action == 'review_status_change':
            trigger_hook = hooks_utils.trigger_log_review_pull_request_hook
        elif action == 'update':
            trigger_hook = hooks_utils.trigger_log_update_pull_request_hook
        else:
            return

        trigger_hook(
            username=user.username,
            repo_name=pull_request.target_repo.repo_name,
            repo_alias=target_scm.alias,
            pull_request=pull_request)

    def _get_commit_ids(self, pull_request):
        """
        Return the commit ids of the merged pull request.

        This method is not dealing correctly yet with the lack of autoupdates
        nor with the implicit target updates.
        For example: if a commit in the source repo is already in the target it
        will be reported anyways.
        """
        merge_rev = pull_request.merge_rev
        if merge_rev is None:
            raise ValueError('This pull request was not merged yet')

        commit_ids = list(pull_request.revisions)
        if merge_rev not in commit_ids:
            commit_ids.append(merge_rev)

        return commit_ids

    def merge(self, pull_request, user, extras):
        merge_state = self._merge_pull_request(pull_request, user, extras)
        if merge_state.executed:
            self._comment_and_close_pr(pull_request, user, merge_state)
            self._log_action('user_merged_pull_request', user, pull_request)
        return merge_state

    def _merge_pull_request(self, pull_request, user, extras):
        target_vcs = pull_request.target_repo.scm_instance()
        source_vcs = pull_request.source_repo.scm_instance()
        target_ref = self._refresh_reference(
            pull_request.target_ref_parts, target_vcs)

        message = _(
            'Merge pull request #%(pr_id)s from '
            '%(source_repo)s %(source_ref_name)s\n\n %(pr_title)s') % {
                'pr_id': pull_request.pull_request_id,
                'source_repo': source_vcs.name,
                'source_ref_name': pull_request.source_ref_parts.name,
                'pr_title': pull_request.title
            }

        workspace_id = self._workspace_id(pull_request)
        protocol = rhodecode.CONFIG.get('vcs.hooks.protocol')
        use_direct_calls = rhodecode.CONFIG.get('vcs.hooks.direct_calls')

        callback_daemon, extras = prepare_callback_daemon(
            extras, protocol=protocol, use_direct_calls=use_direct_calls)

        with callback_daemon:
            # TODO: johbo: Implement a clean way to run a config_override
            # for a single call.
            target_vcs.config.set(
                'rhodecode', 'RC_SCM_DATA', json.dumps(extras))
            merge_state = target_vcs.merge(
                target_ref, source_vcs, pull_request.source_ref_parts,
                workspace_id, user_name=user.username,
                user_email=user.email, message=message)
        return merge_state

    def _comment_and_close_pr(self, pull_request, user, merge_state):
        pull_request.merge_rev = merge_state.merge_commit_id
        pull_request.updated_on = datetime.datetime.now()

        ChangesetCommentsModel().create(
            text=unicode(_('Pull request merged and closed')),
            repo=pull_request.target_repo.repo_id,
            user=user.user_id,
            pull_request=pull_request.pull_request_id,
            f_path=None,
            line_no=None,
            closing_pr=True
        )

        Session().add(pull_request)
        Session().flush()
        # TODO: paris: replace invalidation with less radical solution
        ScmModel().mark_for_invalidation(
            pull_request.target_repo.repo_name)
        self._trigger_pull_request_hook(pull_request, user, 'merge')

    def has_valid_update_type(self, pull_request):
        source_ref_type = pull_request.source_ref_parts.type
        return source_ref_type in ['book', 'branch', 'tag']

    def update_commits(self, pull_request):
        """
        Get the updated list of commits for the pull request
        and return the new pull request version and the list
        of commits processed by this update action
        """

        pull_request = self.__get_pull_request(pull_request)
        source_ref_type = pull_request.source_ref_parts.type
        source_ref_name = pull_request.source_ref_parts.name
        source_ref_id = pull_request.source_ref_parts.commit_id

        if not self.has_valid_update_type(pull_request):
            log.debug(
                "Skipping update of pull request %s due to ref type: %s",
                pull_request, source_ref_type)
            return (None, None)

        source_repo = pull_request.source_repo.scm_instance()
        source_commit = source_repo.get_commit(commit_id=source_ref_name)
        if source_ref_id == source_commit.raw_id:
            log.debug("Nothing changed in pull request %s", pull_request)
            return (None, None)

        # Finally there is a need for an update
        pull_request_version = self._create_version_from_snapshot(pull_request)
        self._link_comments_to_version(pull_request_version)

        target_ref_type = pull_request.target_ref_parts.type
        target_ref_name = pull_request.target_ref_parts.name
        target_ref_id = pull_request.target_ref_parts.commit_id
        target_repo = pull_request.target_repo.scm_instance()

        if target_ref_type in ('tag', 'branch', 'book'):
            target_commit = target_repo.get_commit(target_ref_name)
        else:
            target_commit = target_repo.get_commit(target_ref_id)

        # re-compute commit ids
        old_commit_ids = set(pull_request.revisions)
        pre_load = ["author", "branch", "date", "message"]
        commit_ranges = target_repo.compare(
            target_commit.raw_id, source_commit.raw_id, source_repo, merge=True,
            pre_load=pre_load)

        ancestor = target_repo.get_common_ancestor(
            target_commit.raw_id, source_commit.raw_id, source_repo)

        pull_request.source_ref = '%s:%s:%s' % (
            source_ref_type, source_ref_name, source_commit.raw_id)
        pull_request.target_ref = '%s:%s:%s' % (
            target_ref_type, target_ref_name, ancestor)
        pull_request.revisions = [
            commit.raw_id for commit in reversed(commit_ranges)]
        pull_request.updated_on = datetime.datetime.now()
        Session().add(pull_request)
        new_commit_ids = set(pull_request.revisions)

        changes = self._calculate_commit_id_changes(
            old_commit_ids, new_commit_ids)

        old_diff_data, new_diff_data = self._generate_update_diffs(
            pull_request, pull_request_version)

        ChangesetCommentsModel().outdate_comments(
            pull_request, old_diff_data=old_diff_data,
            new_diff_data=new_diff_data)

        file_changes = self._calculate_file_changes(
            old_diff_data, new_diff_data)

        # Add an automatic comment to the pull request
        update_comment = ChangesetCommentsModel().create(
            text=self._render_update_message(changes, file_changes),
            repo=pull_request.target_repo,
            user=pull_request.author,
            pull_request=pull_request,
            send_email=False, renderer=DEFAULT_COMMENTS_RENDERER)

        # Update status to "Under Review" for added commits
        for commit_id in changes.added:
            ChangesetStatusModel().set_status(
                repo=pull_request.source_repo,
                status=ChangesetStatus.STATUS_UNDER_REVIEW,
                comment=update_comment,
                user=pull_request.author,
                pull_request=pull_request,
                revision=commit_id)

        log.debug(
            'Updated pull request %s, added_ids: %s, common_ids: %s, '
            'removed_ids: %s', pull_request.pull_request_id,
            changes.added, changes.common, changes.removed)
        log.debug('Updated pull request with the following file changes: %s',
                  file_changes)

        log.info(
            "Updated pull request %s from commit %s to commit %s, "
            "stored new version %s of this pull request.",
            pull_request.pull_request_id, source_ref_id,
            pull_request.source_ref_parts.commit_id,
            pull_request_version.pull_request_version_id)
        Session().commit()
        self._trigger_pull_request_hook(pull_request, pull_request.author,
                                        'update')
        return (pull_request_version, changes)

    def _create_version_from_snapshot(self, pull_request):
        version = PullRequestVersion()
        version.title = pull_request.title
        version.description = pull_request.description
        version.status = pull_request.status
        version.created_on = pull_request.created_on
        version.updated_on = pull_request.updated_on
        version.user_id = pull_request.user_id
        version.source_repo = pull_request.source_repo
        version.source_ref = pull_request.source_ref
        version.target_repo = pull_request.target_repo
        version.target_ref = pull_request.target_ref

        version._last_merge_source_rev = pull_request._last_merge_source_rev
        version._last_merge_target_rev = pull_request._last_merge_target_rev
        version._last_merge_status = pull_request._last_merge_status
        version.merge_rev = pull_request.merge_rev

        version.revisions = pull_request.revisions
        version.pull_request = pull_request
        Session().add(version)
        Session().flush()

        return version

    def _generate_update_diffs(self, pull_request, pull_request_version):
        diff_context = (
            self.DIFF_CONTEXT +
            ChangesetCommentsModel.needed_extra_diff_context())
        old_diff = self._get_diff_from_pr_or_version(
            pull_request_version, context=diff_context)
        new_diff = self._get_diff_from_pr_or_version(
            pull_request, context=diff_context)

        old_diff_data = diffs.DiffProcessor(old_diff)
        old_diff_data.prepare()
        new_diff_data = diffs.DiffProcessor(new_diff)
        new_diff_data.prepare()

        return old_diff_data, new_diff_data

    def _link_comments_to_version(self, pull_request_version):
        """
        Link all unlinked comments of this pull request to the given version.

        :param pull_request_version: The `PullRequestVersion` to which
            the comments shall be linked.

        """
        pull_request = pull_request_version.pull_request
        comments = ChangesetComment.query().filter(
            # TODO: johbo: Should we query for the repo at all here?
            # Pending decision on how comments of PRs are to be related
            # to either the source repo, the target repo or no repo at all.
            ChangesetComment.repo_id == pull_request.target_repo.repo_id,
            ChangesetComment.pull_request == pull_request,
            ChangesetComment.pull_request_version == None)

        # TODO: johbo: Find out why this breaks if it is done in a bulk
        # operation.
        for comment in comments:
            comment.pull_request_version_id = (
                pull_request_version.pull_request_version_id)
            Session().add(comment)

    def _calculate_commit_id_changes(self, old_ids, new_ids):
        added = new_ids.difference(old_ids)
        common = old_ids.intersection(new_ids)
        removed = old_ids.difference(new_ids)
        return ChangeTuple(added, common, removed)

    def _calculate_file_changes(self, old_diff_data, new_diff_data):

        old_files = OrderedDict()
        for diff_data in old_diff_data.parsed_diff:
            old_files[diff_data['filename']] = md5_safe(diff_data['raw_diff'])

        added_files = []
        modified_files = []
        removed_files = []
        for diff_data in new_diff_data.parsed_diff:
            new_filename = diff_data['filename']
            new_hash = md5_safe(diff_data['raw_diff'])

            old_hash = old_files.get(new_filename)
            if not old_hash:
                # file is not present in old diff, means it's added
                added_files.append(new_filename)
            else:
                if new_hash != old_hash:
                    modified_files.append(new_filename)
                # now remove a file from old, since we have seen it already
                del old_files[new_filename]

        # removed files is when there are present in old, but not in NEW,
        # since we remove old files that are present in new diff, left-overs
        # if any should be the removed files
        removed_files.extend(old_files.keys())

        return FileChangeTuple(added_files, modified_files, removed_files)

    def _render_update_message(self, changes, file_changes):
        """
        render the message using DEFAULT_COMMENTS_RENDERER (RST renderer),
        so it's always looking the same disregarding on which default
        renderer system is using.

        :param changes: changes named tuple
        :param file_changes: file changes named tuple

        """
        new_status = ChangesetStatus.get_status_lbl(
            ChangesetStatus.STATUS_UNDER_REVIEW)

        changed_files = (
            file_changes.added + file_changes.modified + file_changes.removed)

        params = {
            'under_review_label': new_status,
            'added_commits': changes.added,
            'removed_commits': changes.removed,
            'changed_files': changed_files,
            'added_files': file_changes.added,
            'modified_files': file_changes.modified,
            'removed_files': file_changes.removed,
        }
        renderer = RstTemplateRenderer()
        return renderer.render('pull_request_update.mako', **params)

    def edit(self, pull_request, title, description):
        pull_request = self.__get_pull_request(pull_request)
        if pull_request.is_closed():
            raise ValueError('This pull request is closed')
        if title:
            pull_request.title = title
        pull_request.description = description
        pull_request.updated_on = datetime.datetime.now()
        Session().add(pull_request)

    def update_reviewers(self, pull_request, reviewers_ids):
        reviewers_ids = set(reviewers_ids)
        pull_request = self.__get_pull_request(pull_request)
        current_reviewers = PullRequestReviewers.query()\
            .filter(PullRequestReviewers.pull_request ==
                    pull_request).all()
        current_reviewers_ids = set([x.user.user_id for x in current_reviewers])

        ids_to_add = reviewers_ids.difference(current_reviewers_ids)
        ids_to_remove = current_reviewers_ids.difference(reviewers_ids)

        log.debug("Adding %s reviewers", ids_to_add)
        log.debug("Removing %s reviewers", ids_to_remove)
        changed = False
        for uid in ids_to_add:
            changed = True
            _usr = self._get_user(uid)
            reviewer = PullRequestReviewers(_usr, pull_request)
            Session().add(reviewer)

        self.notify_reviewers(pull_request, ids_to_add)

        for uid in ids_to_remove:
            changed = True
            reviewer = PullRequestReviewers.query()\
                .filter(PullRequestReviewers.user_id == uid,
                        PullRequestReviewers.pull_request == pull_request)\
                .scalar()
            if reviewer:
                Session().delete(reviewer)
        if changed:
            pull_request.updated_on = datetime.datetime.now()
            Session().add(pull_request)

        return ids_to_add, ids_to_remove

    def notify_reviewers(self, pull_request, reviewers_ids):
        # notification to reviewers
        if not reviewers_ids:
            return

        pull_request_obj = pull_request
        # get the current participants of this pull request
        recipients = reviewers_ids
        notification_type = EmailNotificationModel.TYPE_PULL_REQUEST

        pr_source_repo = pull_request_obj.source_repo
        pr_target_repo = pull_request_obj.target_repo

        pr_url = h.url(
            'pullrequest_show',
            repo_name=pr_target_repo.repo_name,
            pull_request_id=pull_request_obj.pull_request_id,
            qualified=True,)

        # set some variables for email notification
        pr_target_repo_url = h.url(
            'summary_home',
            repo_name=pr_target_repo.repo_name,
            qualified=True)

        pr_source_repo_url = h.url(
            'summary_home',
            repo_name=pr_source_repo.repo_name,
            qualified=True)

        # pull request specifics
        pull_request_commits = [
            (x.raw_id, x.message)
            for x in map(pr_source_repo.get_commit, pull_request.revisions)]

        kwargs = {
            'user': pull_request.author,
            'pull_request': pull_request_obj,
            'pull_request_commits': pull_request_commits,

            'pull_request_target_repo': pr_target_repo,
            'pull_request_target_repo_url': pr_target_repo_url,

            'pull_request_source_repo': pr_source_repo,
            'pull_request_source_repo_url': pr_source_repo_url,

            'pull_request_url': pr_url,
        }

        # pre-generate the subject for notification itself
        (subject,
         _h, _e,  # we don't care about those
         body_plaintext) = EmailNotificationModel().render_email(
            notification_type, **kwargs)

        # create notification objects, and emails
        NotificationModel().create(
            created_by=pull_request.author,
            notification_subject=subject,
            notification_body=body_plaintext,
            notification_type=notification_type,
            recipients=recipients,
            email_kwargs=kwargs,
        )

    def delete(self, pull_request):
        pull_request = self.__get_pull_request(pull_request)
        self._cleanup_merge_workspace(pull_request)
        Session().delete(pull_request)

    def close_pull_request(self, pull_request, user):
        pull_request = self.__get_pull_request(pull_request)
        self._cleanup_merge_workspace(pull_request)
        pull_request.status = PullRequest.STATUS_CLOSED
        pull_request.updated_on = datetime.datetime.now()
        Session().add(pull_request)
        self._trigger_pull_request_hook(
            pull_request, pull_request.author, 'close')
        self._log_action('user_closed_pull_request', user, pull_request)

    def close_pull_request_with_comment(self, pull_request, user, repo,
                                        message=None):
        status = ChangesetStatus.STATUS_REJECTED

        if not message:
            message = (
                _('Status change %(transition_icon)s %(status)s') % {
                    'transition_icon': '>',
                    'status': ChangesetStatus.get_status_lbl(status)})

        internal_message = _('Closing with') + ' ' + message

        comm = ChangesetCommentsModel().create(
            text=internal_message,
            repo=repo.repo_id,
            user=user.user_id,
            pull_request=pull_request.pull_request_id,
            f_path=None,
            line_no=None,
            status_change=ChangesetStatus.get_status_lbl(status),
            closing_pr=True
        )

        ChangesetStatusModel().set_status(
            repo.repo_id,
            status,
            user.user_id,
            comm,
            pull_request=pull_request.pull_request_id
        )
        Session().flush()

        PullRequestModel().close_pull_request(
            pull_request.pull_request_id, user)

    def merge_status(self, pull_request):
        if not self._is_merge_enabled(pull_request):
            return False, _('Server-side pull request merging is disabled.')
        if pull_request.is_closed():
            return False, _('This pull request is closed.')
        merge_possible, msg = self._check_repo_requirements(
            target=pull_request.target_repo, source=pull_request.source_repo)
        if not merge_possible:
            return merge_possible, msg

        try:
            resp = self._try_merge(pull_request)
            status = resp.possible, self.merge_status_message(
                resp.failure_reason)
        except NotImplementedError:
            status = False, _('Pull request merging is not supported.')

        return status

    def _check_repo_requirements(self, target, source):
        """
        Check if `target` and `source` have compatible requirements.

        Currently this is just checking for largefiles.
        """
        target_has_largefiles = self._has_largefiles(target)
        source_has_largefiles = self._has_largefiles(source)
        merge_possible = True
        message = u''

        if target_has_largefiles != source_has_largefiles:
            merge_possible = False
            if source_has_largefiles:
                message = _(
                    'Target repository large files support is disabled.')
            else:
                message = _(
                    'Source repository large files support is disabled.')

        return merge_possible, message

    def _has_largefiles(self, repo):
        largefiles_ui = VcsSettingsModel(repo=repo).get_ui_settings(
            'extensions', 'largefiles')
        return largefiles_ui and largefiles_ui[0].active

    def _try_merge(self, pull_request):
        """
        Try to merge the pull request and return the merge status.
        """
        target_vcs = pull_request.target_repo.scm_instance()
        target_ref = self._refresh_reference(
            pull_request.target_ref_parts, target_vcs)

        target_locked = pull_request.target_repo.locked
        if target_locked and target_locked[0]:
            merge_state = MergeResponse(
                False, False, None, MergeFailureReason.TARGET_IS_LOCKED)
        elif self._needs_merge_state_refresh(pull_request, target_ref):
            merge_state = self._refresh_merge_state(
                pull_request, target_vcs, target_ref)
        else:
            possible = pull_request.\
                _last_merge_status == MergeFailureReason.NONE
            merge_state = MergeResponse(
                possible, False, None, pull_request._last_merge_status)
        return merge_state

    def _refresh_reference(self, reference, vcs_repository):
        if reference.type in ('branch', 'book'):
            name_or_id = reference.name
        else:
            name_or_id = reference.commit_id
        refreshed_commit = vcs_repository.get_commit(name_or_id)
        refreshed_reference = Reference(
            reference.type, reference.name, refreshed_commit.raw_id)
        return refreshed_reference

    def _needs_merge_state_refresh(self, pull_request, target_reference):
        return not(
            pull_request.revisions and
            pull_request.revisions[0] == pull_request._last_merge_source_rev and
            target_reference.commit_id == pull_request._last_merge_target_rev)

    def _refresh_merge_state(self, pull_request, target_vcs, target_reference):
        workspace_id = self._workspace_id(pull_request)
        source_vcs = pull_request.source_repo.scm_instance()
        merge_state = target_vcs.merge(
            target_reference, source_vcs, pull_request.source_ref_parts,
            workspace_id, dry_run=True)

        # Do not store the response if there was an unknown error.
        if merge_state.failure_reason != MergeFailureReason.UNKNOWN:
            pull_request._last_merge_source_rev = pull_request.\
                source_ref_parts.commit_id
            pull_request._last_merge_target_rev = target_reference.commit_id
            pull_request._last_merge_status = (
                merge_state.failure_reason)
            Session().add(pull_request)
            Session().flush()

        return merge_state

    def _workspace_id(self, pull_request):
        workspace_id = 'pr-%s' % pull_request.pull_request_id
        return workspace_id

    def merge_status_message(self, status_code):
        """
        Return a human friendly error message for the given merge status code.
        """
        return self.MERGE_STATUS_MESSAGES[status_code]

    def generate_repo_data(self, repo, commit_id=None, branch=None,
                           bookmark=None):
        all_refs, selected_ref = \
            self._get_repo_pullrequest_sources(
                repo.scm_instance(), commit_id=commit_id,
                branch=branch, bookmark=bookmark)

        refs_select2 = []
        for element in all_refs:
            children = [{'id': x[0], 'text': x[1]} for x in element[0]]
            refs_select2.append({'text': element[1], 'children': children})

        return {
            'user': {
                'user_id': repo.user.user_id,
                'username': repo.user.username,
                'firstname': repo.user.firstname,
                'lastname': repo.user.lastname,
                'gravatar_link': h.gravatar_url(repo.user.email, 14),
            },
            'description': h.chop_at_smart(repo.description, '\n'),
            'refs': {
                'all_refs': all_refs,
                'selected_ref': selected_ref,
                'select2_refs': refs_select2
            }
        }

    def generate_pullrequest_title(self, source, source_ref, target):
        return '{source}#{at_ref} to {target}'.format(
            source=source,
            at_ref=source_ref,
            target=target,
        )

    def _cleanup_merge_workspace(self, pull_request):
        # Merging related cleanup
        target_scm = pull_request.target_repo.scm_instance()
        workspace_id = 'pr-%s' % pull_request.pull_request_id

        try:
            target_scm.cleanup_merge_workspace(workspace_id)
        except NotImplementedError:
            pass

    def _get_repo_pullrequest_sources(
            self, repo, commit_id=None, branch=None, bookmark=None):
        """
        Return a structure with repo's interesting commits, suitable for
        the selectors in pullrequest controller

        :param commit_id: a commit that must be in the list somehow
            and selected by default
        :param branch: a branch that must be in the list and selected
            by default - even if closed
        :param bookmark: a bookmark that must be in the list and selected
        """

        commit_id = safe_str(commit_id) if commit_id else None
        branch = safe_str(branch) if branch else None
        bookmark = safe_str(bookmark) if bookmark else None

        selected = None

        # order matters: first source that has commit_id in it will be selected
        sources = []
        sources.append(('book', repo.bookmarks.items(), _('Bookmarks'), bookmark))
        sources.append(('branch', repo.branches.items(), _('Branches'), branch))

        if commit_id:
            ref_commit = (h.short_id(commit_id), commit_id)
            sources.append(('rev', [ref_commit], _('Commit IDs'), commit_id))

        sources.append(
            ('branch', repo.branches_closed.items(), _('Closed Branches'), branch),
        )

        groups = []
        for group_key, ref_list, group_name, match in sources:
            group_refs = []
            for ref_name, ref_id in ref_list:
                ref_key = '%s:%s:%s' % (group_key, ref_name, ref_id)
                group_refs.append((ref_key, ref_name))

                if not selected and match in (ref_id, ref_name):
                    selected = ref_key
            if group_refs:
                groups.append((group_refs, group_name))

        if not selected:
            ref = commit_id or branch or bookmark
            if ref:
                raise CommitDoesNotExistError(
                    'No commit refs could be found matching: %s' % ref)
            elif repo.DEFAULT_BRANCH_NAME in repo.branches:
                selected = 'branch:%s:%s' % (
                    repo.DEFAULT_BRANCH_NAME,
                    repo.branches[repo.DEFAULT_BRANCH_NAME]
                )
            elif repo.commit_ids:
                rev = repo.commit_ids[0]
                selected = 'rev:%s:%s' % (rev, rev)
            else:
                raise EmptyRepositoryError()
        return groups, selected

    def get_diff(self, pull_request, context=DIFF_CONTEXT):
        pull_request = self.__get_pull_request(pull_request)
        return self._get_diff_from_pr_or_version(pull_request, context=context)

    def _get_diff_from_pr_or_version(self, pr_or_version, context):
        source_repo = pr_or_version.source_repo

        # we swap org/other ref since we run a simple diff on one repo
        target_ref_id = pr_or_version.target_ref_parts.commit_id
        source_ref_id = pr_or_version.source_ref_parts.commit_id
        target_commit = source_repo.get_commit(
            commit_id=safe_str(target_ref_id))
        source_commit = source_repo.get_commit(commit_id=safe_str(source_ref_id))
        vcs_repo = source_repo.scm_instance()

        # TODO: johbo: In the context of an update, we cannot reach
        # the old commit anymore with our normal mechanisms. It needs
        # some sort of special support in the vcs layer to avoid this
        # workaround.
        if (source_commit.raw_id == vcs_repo.EMPTY_COMMIT_ID and
                vcs_repo.alias == 'git'):
            source_commit.raw_id = safe_str(source_ref_id)

        log.debug('calculating diff between '
                  'source_ref:%s and target_ref:%s for repo `%s`',
                  target_ref_id, source_ref_id,
                  safe_unicode(vcs_repo.path))

        vcs_diff = vcs_repo.get_diff(
            commit1=target_commit, commit2=source_commit, context=context)
        return vcs_diff

    def _is_merge_enabled(self, pull_request):
        settings_model = VcsSettingsModel(repo=pull_request.target_repo)
        settings = settings_model.get_general_settings()
        return settings.get('rhodecode_pr_merge_enabled', False)

    def _log_action(self, action, user, pull_request):
        action_logger(
            user,
            '{action}:{pr_id}'.format(
                action=action, pr_id=pull_request.pull_request_id),
            pull_request.target_repo)


ChangeTuple = namedtuple('ChangeTuple',
                         ['added', 'common', 'removed'])

FileChangeTuple = namedtuple('FileChangeTuple',
                             ['added', 'modified', 'removed'])
