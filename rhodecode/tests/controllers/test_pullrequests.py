# -*- coding: utf-8 -*-

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

import mock

from rhodecode.controllers import pullrequests
from rhodecode.lib.vcs.backends.base import (
    MergeFailureReason, MergeResponse)
from rhodecode.model.pull_request import PullRequestModel
from rhodecode.tests import assert_session_flash


def test_merge_pull_request_renders_failure_reason(user_regular):
    pull_request = mock.Mock()
    controller = pullrequests.PullrequestsController()
    model_patcher = mock.patch.multiple(
        PullRequestModel,
        merge=mock.Mock(return_value=MergeResponse(
            True, False, 'STUB_COMMIT_ID', MergeFailureReason.PUSH_FAILED)),
        merge_status=mock.Mock(return_value=(True, 'WRONG_MESSAGE')))
    with model_patcher:
        controller._merge_pull_request(pull_request, user_regular, extras={})

    assert_session_flash(msg=PullRequestModel.MERGE_STATUS_MESSAGES[
        MergeFailureReason.PUSH_FAILED])
