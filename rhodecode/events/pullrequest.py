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
                'url': PullRequestModel().get_url(self.pullrequest)
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
    request is updated.
    """
    name = 'pullrequest-update'
    display_name = lazy_ugettext('pullrequest updated')


class PullRequestMergeEvent(PullRequestEvent):
    """
    An instance of this class is emitted as an :term:`event` after a pull
    request is merged.
    """
    name = 'pullrequest-merge'
    display_name = lazy_ugettext('pullrequest merged')


class PullRequestReviewEvent(PullRequestEvent):
    """
    An instance of this class is emitted as an :term:`event` after a pull
    request is reviewed.
    """
    name = 'pullrequest-review'
    display_name = lazy_ugettext('pullrequest reviewed')


