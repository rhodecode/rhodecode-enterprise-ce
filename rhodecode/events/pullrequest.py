# Copyright (C) 2016-2016  RhodeCode GmbH
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


from rhodecode.translation import lazy_ugettext
from rhodecode.events.repo import RepoEvent


class PullRequestEvent(RepoEvent):
    """
    Base class for pull request events.

    :param pullrequest: a :class:`PullRequest` instance
    """

    def __init__(self, pullrequest):
        super(PullRequestEvent, self).__init__(pullrequest.target_repo)
        self.pullrequest = pullrequest

    def as_dict(self):
        from rhodecode.model.pull_request import PullRequestModel
        data = super(PullRequestEvent, self).as_dict()

        commits = self._commits_as_dict(self.pullrequest.revisions)
        issues = self._issues_as_dict(commits)

        data.update({
            'pullrequest': {
                'title': self.pullrequest.title,
                'issues': issues,
                'pull_request_id': self.pullrequest.pull_request_id,
                'url': PullRequestModel().get_url(self.pullrequest),
                'status': self.pullrequest.calculated_review_status(),
            }
        })
        return data


class PullRequestCreateEvent(PullRequestEvent):
    """
    An instance of this class is emitted as an :term:`event` after a pull
    request is created.
    """
    name = 'pullrequest-create'
    display_name = lazy_ugettext('pullrequest created')


class PullRequestCloseEvent(PullRequestEvent):
    """
    An instance of this class is emitted as an :term:`event` after a pull
    request is closed.
    """
    name = 'pullrequest-close'
    display_name = lazy_ugettext('pullrequest closed')


class PullRequestUpdateEvent(PullRequestEvent):
    """
    An instance of this class is emitted as an :term:`event` after a pull
    request's commits have been updated.
    """
    name = 'pullrequest-update'
    display_name = lazy_ugettext('pullrequest commits updated')


class PullRequestReviewEvent(PullRequestEvent):
    """
    An instance of this class is emitted as an :term:`event` after a pull
    request review has changed.
    """
    name = 'pullrequest-review'
    display_name = lazy_ugettext('pullrequest review changed')


class PullRequestMergeEvent(PullRequestEvent):
    """
    An instance of this class is emitted as an :term:`event` after a pull
    request is merged.
    """
    name = 'pullrequest-merge'
    display_name = lazy_ugettext('pullrequest merged')


class PullRequestCommentEvent(PullRequestEvent):
    """
    An instance of this class is emitted as an :term:`event` after a pull
    request comment is created.
    """
    name = 'pullrequest-comment'
    display_name = lazy_ugettext('pullrequest commented')

    def __init__(self, pullrequest, comment):
        super(PullRequestCommentEvent, self).__init__(pullrequest)
        self.comment = comment

    def as_dict(self):
        from rhodecode.model.comment import ChangesetCommentsModel
        data = super(PullRequestCommentEvent, self).as_dict()

        status = None
        if self.comment.status_change:
            status = self.comment.status_change[0].status

        data.update({
            'comment': {
                'status': status,
                'text': self.comment.text,
                'url': ChangesetCommentsModel().get_url(self.comment)
            }
        })
        return data
