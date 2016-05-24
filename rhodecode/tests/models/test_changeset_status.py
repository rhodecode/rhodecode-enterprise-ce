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

from rhodecode.model import db
from rhodecode.model.changeset_status import ChangesetStatusModel
from rhodecode.model.pull_request import PullRequestModel


pytestmark = [
    pytest.mark.backends("git", "hg"),
]


def test_new_pull_request_is_under_review(pr_util):
    pull_request = pr_util.create_pull_request()

    # Expect that review status "Under Review"
    expected_review_status = db.ChangesetStatus.STATUS_UNDER_REVIEW
    assert pull_request.calculated_review_status() == expected_review_status


@pytest.mark.parametrize("voted_status", [
    db.ChangesetStatus.STATUS_APPROVED,
    db.ChangesetStatus.STATUS_REJECTED,
    db.ChangesetStatus.STATUS_UNDER_REVIEW,
])
def test_pull_request_under_review_if_one_reviewer_voted(
        pr_util, voted_status):
    pull_request = pr_util.create_pull_request()
    pr_util.create_status_votes(
        voted_status, pull_request.reviewers[0])

    # Expect that review status "Under Review"
    expected_review_status = db.ChangesetStatus.STATUS_UNDER_REVIEW
    assert pull_request.calculated_review_status() == expected_review_status


@pytest.mark.parametrize("voted_status", [
    db.ChangesetStatus.STATUS_APPROVED,
    db.ChangesetStatus.STATUS_REJECTED,
    db.ChangesetStatus.STATUS_UNDER_REVIEW,
])
def test_pull_request_has_voted_status_if_all_voted(pr_util, voted_status):
    pull_request = pr_util.create_pull_request()
    pr_util.create_status_votes(
        voted_status, *pull_request.reviewers)

    # Expect that review status is the voted_status
    expected_review_status = voted_status
    assert pull_request.calculated_review_status() == expected_review_status


@pytest.mark.parametrize("voted_status", [
    db.ChangesetStatus.STATUS_APPROVED,
    db.ChangesetStatus.STATUS_REJECTED,
    db.ChangesetStatus.STATUS_UNDER_REVIEW,
])
def test_pull_request_stays_if_update_without_change(pr_util, voted_status):
    pull_request = pr_util.create_pull_request()
    pr_util.create_status_votes(
        voted_status, *pull_request.reviewers)

    # Update, without change
    PullRequestModel().update_commits(pull_request)

    # Expect that review status is the voted_status
    expected_review_status = voted_status
    assert pull_request.calculated_review_status() == expected_review_status


@pytest.mark.parametrize("voted_status", [
    db.ChangesetStatus.STATUS_APPROVED,
    db.ChangesetStatus.STATUS_REJECTED,
    db.ChangesetStatus.STATUS_UNDER_REVIEW,
])
def test_pull_request_under_review_if_update(pr_util, voted_status):
    pull_request = pr_util.create_pull_request()
    pr_util.create_status_votes(
        voted_status, *pull_request.reviewers)

    # Update, with change
    pr_util.update_source_repository()
    PullRequestModel().update_commits(pull_request)

    # Expect that review status is the voted_status
    expected_review_status = db.ChangesetStatus.STATUS_UNDER_REVIEW
    assert pull_request.calculated_review_status() == expected_review_status


def test_commit_under_review_if_part_of_new_pull_request(pr_util):
    pull_request = pr_util.create_pull_request()
    for commit_id in pull_request.revisions:
        status = ChangesetStatusModel().get_status(
            repo=pr_util.source_repository, revision=commit_id)
        assert status == db.ChangesetStatus.STATUS_UNDER_REVIEW


@pytest.mark.parametrize("voted_status", [
    db.ChangesetStatus.STATUS_APPROVED,
    db.ChangesetStatus.STATUS_REJECTED,
    db.ChangesetStatus.STATUS_UNDER_REVIEW,
])
def test_commit_has_voted_status_after_vote_on_pull_request(
        pr_util, voted_status):
    pull_request = pr_util.create_pull_request()
    pr_util.create_status_votes(
        voted_status, pull_request.reviewers[0])
    for commit_id in pull_request.revisions:
        status = ChangesetStatusModel().get_status(
            repo=pr_util.source_repository, revision=commit_id)
        assert status == voted_status


def test_commit_under_review_if_added_to_pull_request(pr_util):
    pull_request = pr_util.create_pull_request()
    pr_util.create_status_votes(
        db.ChangesetStatus.STATUS_APPROVED, pull_request.reviewers[0])
    added_commit_id = pr_util.add_one_commit()

    status = ChangesetStatusModel().get_status(
        repo=pr_util.source_repository, revision=added_commit_id)
    assert status == db.ChangesetStatus.STATUS_UNDER_REVIEW


@pytest.mark.parametrize("voted_status", [
    db.ChangesetStatus.STATUS_APPROVED,
    db.ChangesetStatus.STATUS_REJECTED,
    db.ChangesetStatus.STATUS_UNDER_REVIEW,
])
def test_commit_keeps_status_if_removed_from_pull_request(
        pr_util, voted_status):
    pull_request = pr_util.create_pull_request()
    pr_util.add_one_commit()
    pr_util.create_status_votes(voted_status, pull_request.reviewers[0])

    removed_commit_id = pr_util.remove_one_commit()

    status = ChangesetStatusModel().get_status(
        repo=pr_util.source_repository, revision=removed_commit_id)
    assert status == voted_status


@pytest.mark.parametrize("voted_status", [
    db.ChangesetStatus.STATUS_APPROVED,
    db.ChangesetStatus.STATUS_REJECTED,
    db.ChangesetStatus.STATUS_UNDER_REVIEW,
])
def test_commit_keeps_status_if_unchanged_after_update_of_pull_request(
        pr_util, voted_status):
    pull_request = pr_util.create_pull_request()
    commit_id = pull_request.revisions[-1]
    pr_util.create_status_votes(voted_status, pull_request.reviewers[0])
    pr_util.update_source_repository()
    PullRequestModel().update_commits(pull_request)
    assert pull_request.revisions[-1] == commit_id

    status = ChangesetStatusModel().get_status(
        repo=pr_util.source_repository, revision=commit_id)
    assert status == voted_status
