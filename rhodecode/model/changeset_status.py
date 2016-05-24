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

"""
Changeset status conttroller
"""

import itertools
import logging
from collections import defaultdict

from rhodecode.model import BaseModel
from rhodecode.model.db import ChangesetStatus, ChangesetComment, PullRequest
from rhodecode.lib.exceptions import StatusChangeOnClosedPullRequestError
from rhodecode.lib.markup_renderer import (
    DEFAULT_COMMENTS_RENDERER, RstTemplateRenderer)

log = logging.getLogger(__name__)


class ChangesetStatusModel(BaseModel):

    cls = ChangesetStatus

    def __get_changeset_status(self, changeset_status):
        return self._get_instance(ChangesetStatus, changeset_status)

    def __get_pull_request(self, pull_request):
        return self._get_instance(PullRequest, pull_request)

    def _get_status_query(self, repo, revision, pull_request,
                          with_revisions=False):
        repo = self._get_repo(repo)

        q = ChangesetStatus.query()\
            .filter(ChangesetStatus.repo == repo)
        if not with_revisions:
            q = q.filter(ChangesetStatus.version == 0)

        if revision:
            q = q.filter(ChangesetStatus.revision == revision)
        elif pull_request:
            pull_request = self.__get_pull_request(pull_request)
            # TODO: johbo: Think about the impact of this join, there must
            # be a reason why ChangesetStatus and ChanagesetComment is linked
            # to the pull request. Might be that we want to do the same for
            # the pull_request_version_id.
            q = q.join(ChangesetComment).filter(
                ChangesetStatus.pull_request == pull_request,
                ChangesetComment.pull_request_version_id == None)
        else:
            raise Exception('Please specify revision or pull_request')
        q = q.order_by(ChangesetStatus.version.asc())
        return q

    def calculate_status(self, statuses_by_reviewers):
        """
        Given the approval statuses from reviewers, calculates final approval
        status. There can only be 3 results, all approved, all rejected. If
        there is no consensus the PR is under review.

        :param statuses_by_reviewers:
        """
        votes = defaultdict(int)
        reviewers_number = len(statuses_by_reviewers)
        for user, statuses in statuses_by_reviewers:
            if statuses:
                ver, latest = statuses[0]
                votes[latest.status] += 1
            else:
                votes[ChangesetStatus.DEFAULT] += 1

        # all approved
        if votes.get(ChangesetStatus.STATUS_APPROVED) == reviewers_number:
            return ChangesetStatus.STATUS_APPROVED

        # all rejected
        if votes.get(ChangesetStatus.STATUS_REJECTED) == reviewers_number:
            return ChangesetStatus.STATUS_REJECTED

        return ChangesetStatus.STATUS_UNDER_REVIEW

    def get_statuses(self, repo, revision=None, pull_request=None,
                     with_revisions=False):
        q = self._get_status_query(repo, revision, pull_request,
                                   with_revisions)
        return q.all()

    def get_status(self, repo, revision=None, pull_request=None, as_str=True):
        """
        Returns latest status of changeset for given revision or for given
        pull request. Statuses are versioned inside a table itself and
        version == 0 is always the current one

        :param repo:
        :param revision: 40char hash or None
        :param pull_request: pull_request reference
        :param as_str: return status as string not object
        """
        q = self._get_status_query(repo, revision, pull_request)

        # need to use first here since there can be multiple statuses
        # returned from pull_request
        status = q.first()
        if as_str:
            status = status.status if status else status
            st = status or ChangesetStatus.DEFAULT
            return str(st)
        return status

    def _render_auto_status_message(
            self, status, commit_id=None, pull_request=None):
        """
        render the message using DEFAULT_COMMENTS_RENDERER (RST renderer),
        so it's always looking the same disregarding on which default
        renderer system is using.

        :param status: status text to change into
        :param commit_id: the commit_id we change the status for
        :param pull_request: the pull request we change the status for
        """

        new_status = ChangesetStatus.get_status_lbl(status)

        params = {
            'new_status_label': new_status,
            'pull_request': pull_request,
            'commit_id': commit_id,
        }
        renderer = RstTemplateRenderer()
        return renderer.render('auto_status_change.mako', **params)

    def set_status(self, repo, status, user, comment=None, revision=None,
                   pull_request=None, dont_allow_on_closed_pull_request=False):
        """
        Creates new status for changeset or updates the old ones bumping their
        version, leaving the current status at

        :param repo:
        :param revision:
        :param status:
        :param user:
        :param comment:
        :param dont_allow_on_closed_pull_request: don't allow a status change
            if last status was for pull request and it's closed. We shouldn't
            mess around this manually
        """
        repo = self._get_repo(repo)

        q = ChangesetStatus.query()

        if revision:
            q = q.filter(ChangesetStatus.repo == repo)
            q = q.filter(ChangesetStatus.revision == revision)
        elif pull_request:
            pull_request = self.__get_pull_request(pull_request)
            q = q.filter(ChangesetStatus.repo == pull_request.source_repo)
            q = q.filter(ChangesetStatus.revision.in_(pull_request.revisions))
        cur_statuses = q.all()

        # if statuses exists and last is associated with a closed pull request
        # we need to check if we can allow this status change
        if (dont_allow_on_closed_pull_request and cur_statuses
            and getattr(cur_statuses[0].pull_request, 'status', '')
                == PullRequest.STATUS_CLOSED):
            raise StatusChangeOnClosedPullRequestError(
                'Changing status on closed pull request is not allowed'
            )

        # update all current statuses with older version
        if cur_statuses:
            for st in cur_statuses:
                st.version += 1
                self.sa.add(st)

        def _create_status(user, repo, status, comment, revision, pull_request):
            new_status = ChangesetStatus()
            new_status.author = self._get_user(user)
            new_status.repo = self._get_repo(repo)
            new_status.status = status
            new_status.comment = comment
            new_status.revision = revision
            new_status.pull_request = pull_request
            return new_status

        if not comment:
            from rhodecode.model.comment import ChangesetCommentsModel
            comment = ChangesetCommentsModel().create(
                text=self._render_auto_status_message(
                    status, commit_id=revision, pull_request=pull_request),
                repo=repo,
                user=user,
                pull_request=pull_request,
                send_email=False, renderer=DEFAULT_COMMENTS_RENDERER
            )

        if revision:
            new_status = _create_status(
                user=user, repo=repo, status=status, comment=comment,
                revision=revision, pull_request=pull_request)
            self.sa.add(new_status)
            return new_status
        elif pull_request:
            # pull request can have more than one revision associated to it
            # we need to create new version for each one
            new_statuses = []
            repo = pull_request.source_repo
            for rev in pull_request.revisions:
                new_status = _create_status(
                    user=user, repo=repo, status=status, comment=comment,
                    revision=rev, pull_request=pull_request)
                new_statuses.append(new_status)
                self.sa.add(new_status)
            return new_statuses

    def reviewers_statuses(self, pull_request):
        _commit_statuses = self.get_statuses(
            pull_request.source_repo,
            pull_request=pull_request,
            with_revisions=True)

        commit_statuses = defaultdict(list)
        for st in _commit_statuses:
            commit_statuses[st.author.username] += [st]

        pull_request_reviewers = []

        def version(commit_status):
            return commit_status.version

        for o in pull_request.reviewers:
            if not o.user:
                continue
            st = commit_statuses.get(o.user.username, None)
            if st:
                st = [(x, list(y)[0])
                      for x, y in (itertools.groupby(sorted(st, key=version),
                                                     version))]

            pull_request_reviewers.append([o.user, st])
        return pull_request_reviewers

    def calculated_review_status(self, pull_request, reviewers_statuses=None):
        """
        calculate pull request status based on reviewers, it should be a list
        of two element lists.

        :param reviewers_statuses:
        """
        reviewers = reviewers_statuses or self.reviewers_statuses(pull_request)
        return self.calculate_status(reviewers)
