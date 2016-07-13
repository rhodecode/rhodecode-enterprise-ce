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
import requests
from mock import Mock, patch

from rhodecode import events
from rhodecode.model.db import Session, Integration
from rhodecode.integrations.types.slack import SlackIntegrationType

@pytest.fixture
def repo_push_event(backend, user_regular):
    commits = [
        {'message': 'ancestor commit fixes #15'},
        {'message': 'quick fixes'},
        {'message': 'change that fixes #41, #2'},
        {'message': 'this is because 5b23c3532 broke stuff'},
        {'message': 'last commit'},
    ]
    commit_ids = backend.create_master_repo(commits).values()
    repo = backend.create_repo()
    scm_extras = {
        'ip': '127.0.0.1',
        'username': user_regular.username,
        'action': '',
        'repository': repo.repo_name,
        'scm': repo.scm_instance().alias,
        'config': '',
        'server_url': 'http://example.com',
        'make_lock': None,
        'locked_by': [None],
        'commit_ids': commit_ids,
    }

    return events.RepoPushEvent(repo_name=repo.repo_name,
                                pushed_commit_ids=commit_ids,
                                extras=scm_extras)


@pytest.fixture
def slack_settings():
    return {
        "service": "mock://slackintegration",
        "events": [
           "pullrequest-create",
           "repo-push",
        ],
        "channel": "#testing",
        "icon_emoji": ":recycle:",
        "username": "rhodecode-test"
    }


@pytest.fixture
def slack_integration(request, app, slack_settings):
    integration = Integration(
        name='test slack integration',
        enabled=True,
        integration_type=SlackIntegrationType.key
    )
    integration.settings = slack_settings
    Session().add(integration)
    Session().commit()
    request.addfinalizer(lambda: Session().delete(integration))
    return integration


def test_slack_push(slack_integration, repo_push_event):
    with patch('rhodecode.integrations.types.slack.post_text_to_slack') as call:
        events.trigger(repo_push_event)
    assert 'pushed to' in call.call_args[0][1]

    slack_integration.settings['events'] = []
    Session().commit()

    with patch('rhodecode.integrations.types.slack.post_text_to_slack') as call:
        events.trigger(repo_push_event)
    assert not call.call_args
