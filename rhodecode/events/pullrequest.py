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

from marshmallow import Schema, fields

from rhodecode.events.repo import RepoEvent


def get_pull_request_url(pull_request):
    from rhodecode.model.pull_request import PullRequestModel
    return PullRequestModel().get_url(pull_request)


class PullRequestSchema(Schema):
    """
    Marshmallow schema for a pull request
    """
    pull_request_id = fields.Integer()
    url = fields.Function(get_pull_request_url)
    title = fields.Str()


class PullRequestEventSchema(RepoEvent.MarshmallowSchema):
    """
    Marshmallow schema for a pull request event
    """
    pullrequest = fields.Nested(PullRequestSchema)


class PullRequestEvent(RepoEvent):
    """
    Base class for pull request events.

    :param pullrequest: a :class:`PullRequest` instance
    """
    MarshmallowSchema = PullRequestEventSchema

    def __init__(self, pullrequest):
        super(PullRequestEvent, self).__init__(pullrequest.target_repo)
        self.pullrequest = pullrequest


class PullRequestCreateEvent(PullRequestEvent):
    """
    An instance of this class is emitted as an :term:`event` after a pull
    request is created.
    """
    name = 'pullrequest-create'


class PullRequestCloseEvent(PullRequestEvent):
    """
    An instance of this class is emitted as an :term:`event` after a pull
    request is closed.
    """
    name = 'pullrequest-close'


class PullRequestUpdateEvent(PullRequestEvent):
    """
    An instance of this class is emitted as an :term:`event` after a pull
    request is updated.
    """
    name = 'pullrequest-update'


class PullRequestMergeEvent(PullRequestEvent):
    """
    An instance of this class is emitted as an :term:`event` after a pull
    request is merged.
    """
    name = 'pullrequest-merge'


class PullRequestReviewEvent(PullRequestEvent):
    """
    An instance of this class is emitted as an :term:`event` after a pull
    request is reviewed.
    """
    name = 'pullrequest-review'


