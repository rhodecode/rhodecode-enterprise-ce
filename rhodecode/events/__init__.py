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


class RhodecodeEvent(object):
    """
    Base event class for all Rhodecode events
    """


def trigger(event):
    """
    Helper method to send an event. This wraps the pyramid logic to send an
    event.
    """
    # For the first step we are using pyramids thread locals here. If the
    # event mechanism works out as a good solution we should think about
    # passing the registry as an argument to get rid of it.
    registry = get_current_registry()
    registry.notify(event)


from rhodecode.events.user import (
    UserPreCreate, UserPreUpdate, UserRegistered
)

from rhodecode.events.repo import (
    RepoPreCreateEvent, RepoCreatedEvent,
    RepoPreDeleteEvent, RepoDeletedEvent,
    RepoPrePushEvent,   RepoPushEvent,
    RepoPrePullEvent,   RepoPullEvent,
)