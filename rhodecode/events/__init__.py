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

from pyramid.threadlocal import get_current_registry


def trigger(event, registry=None):
    """
    Helper method to send an event. This wraps the pyramid logic to send an
    event.
    """
    # For the first step we are using pyramids thread locals here. If the
    # event mechanism works out as a good solution we should think about
    # passing the registry as an argument to get rid of it.
    registry = registry or get_current_registry()
    registry.notify(event)

    # Until we can work around the problem that VCS operations do not have a
    # pyramid context to work with, we send the events to integrations directly

    # Later it will be possible to use regular pyramid subscribers ie:
    #   config.add_subscriber(integrations_event_handler, RhodecodeEvent)
    from rhodecode.integrations import integrations_event_handler
    if isinstance(event, RhodecodeEvent):
        integrations_event_handler(event)


from rhodecode.events.base import RhodecodeEvent

from rhodecode.events.user import (
    UserPreCreate,
    UserPreUpdate,
    UserRegistered
)

from rhodecode.events.repo import (
    RepoEvent,
    RepoPreCreateEvent, RepoCreateEvent,
    RepoPreDeleteEvent, RepoDeleteEvent,
    RepoPrePushEvent,   RepoPushEvent,
    RepoPrePullEvent,   RepoPullEvent,
)

from rhodecode.events.pullrequest import (
    PullRequestEvent,
    PullRequestCreateEvent,
    PullRequestUpdateEvent,
    PullRequestReviewEvent,
    PullRequestMergeEvent,
    PullRequestCloseEvent,
)
