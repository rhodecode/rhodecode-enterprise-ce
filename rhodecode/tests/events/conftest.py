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
import decorator


class EventCatcher(object):
    """ Testing context manager to check if events are fired """

    def __init__(self):
        self.events = [] # the actual events captured
        self.events_types = [] # the types of events captured

    def __enter__(self):
        self.event_trigger_patch = mock.patch('rhodecode.events.trigger')
        self.mocked_event_trigger = self.event_trigger_patch.start()
        return self

    def __exit__(self, type_, value, traceback):
        self.event_trigger_patch.stop()

        for call in self.mocked_event_trigger.call_args_list:
            event = call[0][0]
            self.events.append(event)
            self.events_types.append(type(event))
