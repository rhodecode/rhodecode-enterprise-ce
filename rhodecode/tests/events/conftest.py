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


def assert_fires_events(*expected_events):
    """ Testing decorator to check if the function fires events in order """
    def deco(func):
        def wrapper(func, *args, **kwargs):
            with mock.patch('rhodecode.events.trigger') as mock_trigger:
                result = func(*args, **kwargs)

            captured_events = []
            for call in mock_trigger.call_args_list:
                event = call[0][0]
                captured_events.append(type(event))

            assert set(captured_events) == set(expected_events)
            return result
        return decorator.decorator(wrapper, func)
    return deco