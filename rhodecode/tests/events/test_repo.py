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

from rhodecode.tests.events.conftest import assert_fires_events

from rhodecode.lib import hooks_base, utils2
from rhodecode.model.repo import RepoModel
from rhodecode.events.repo import (
    RepoPrePullEvent, RepoPullEvent,
    RepoPrePushEvent, RepoPushEvent,
    RepoPreCreateEvent, RepoCreatedEvent,
    RepoPreDeleteEvent, RepoDeletedEvent,
)


@pytest.fixture
def scm_extras(user_regular, repo_stub):
    extras = utils2.AttributeDict({
        'ip': '127.0.0.1',
        'username': user_regular.username,
        'action': '',
        'repository': repo_stub.repo_name,
        'scm': repo_stub.scm_instance().alias,
        'config': '',
        'server_url': 'http://example.com',
        'make_lock': None,
        'locked_by': [None],
        'commit_ids': ['a' * 40] * 3,
    })
    return extras


@assert_fires_events(
    RepoPreCreateEvent, RepoCreatedEvent, RepoPreDeleteEvent, RepoDeletedEvent)
def test_create_delete_repo_fires_events(backend):
    repo = backend.create_repo()
    RepoModel().delete(repo)


@assert_fires_events(RepoPrePushEvent, RepoPushEvent)
def test_pull_fires_events(scm_extras):
    hooks_base.pre_push(scm_extras)
    hooks_base.post_push(scm_extras)


@assert_fires_events(RepoPrePullEvent, RepoPullEvent)
def test_push_fires_events(scm_extras):
    hooks_base.pre_pull(scm_extras)
    hooks_base.post_pull(scm_extras)
