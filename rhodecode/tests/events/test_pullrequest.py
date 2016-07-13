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

import pytest

from rhodecode.tests.events.conftest import EventCatcher

from rhodecode.model.comment import ChangesetCommentsModel
from rhodecode.model.pull_request import PullRequestModel
from rhodecode.events import (
    PullRequestCreateEvent,
    PullRequestUpdateEvent,
    PullRequestCommentEvent,
    PullRequestReviewEvent,
    PullRequestMergeEvent,
    PullRequestCloseEvent,
)

# TODO: dan: make the serialization tests complete json comparisons
@pytest.mark.backends("git", "hg")
@pytest.mark.parametrize('EventClass', [
    PullRequestCreateEvent,
    PullRequestUpdateEvent,
    PullRequestReviewEvent,
    PullRequestMergeEvent,
    PullRequestCloseEvent,
])
def test_pullrequest_events_serialized(pr_util, EventClass):
    pr = pr_util.create_pull_request()
    event = EventClass(pr)
    data = event.as_dict()
    assert data['name'] == EventClass.name
    assert data['repo']['repo_name'] == pr.target_repo.repo_name
    assert data['pullrequest']['pull_request_id'] == pr.pull_request_id
    assert data['pullrequest']['url']

@pytest.mark.backends("git", "hg")
def test_create_pull_request_events(pr_util):
    with EventCatcher() as event_catcher:
        pr_util.create_pull_request()

    assert PullRequestCreateEvent in event_catcher.events_types

@pytest.mark.backends("git", "hg")
def test_pullrequest_comment_events_serialized(pr_util):
    pr = pr_util.create_pull_request()
    comment = ChangesetCommentsModel().get_comments(
        pr.target_repo.repo_id, pull_request=pr)[0]
    event = PullRequestCommentEvent(pr, comment)
    data = event.as_dict()
    assert data['name'] == PullRequestCommentEvent.name
    assert data['repo']['repo_name'] == pr.target_repo.repo_name
    assert data['pullrequest']['pull_request_id'] == pr.pull_request_id
    assert data['pullrequest']['url']
    assert data['comment']['text'] == comment.text


@pytest.mark.backends("git", "hg")
def test_close_pull_request_events(pr_util, user_admin):
    pr = pr_util.create_pull_request()

    with EventCatcher() as event_catcher:
        PullRequestModel().close_pull_request(pr, user_admin)

    assert PullRequestCloseEvent in event_catcher.events_types


@pytest.mark.backends("git", "hg")
def test_close_pull_request_with_comment_events(pr_util, user_admin):
    pr = pr_util.create_pull_request()

    with EventCatcher() as event_catcher:
        PullRequestModel().close_pull_request_with_comment(
            pr, user_admin, pr.target_repo)

    assert PullRequestCloseEvent in event_catcher.events_types
