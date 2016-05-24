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

from rhodecode.lib.middleware import appenlight


@pytest.mark.parametrize('environ_stub', [
    # Recent clients provide an empty dict inside of the request environment
    {'appenlight.extra': {}},
    # Case of old client or no client being active, it still should not break
    {},
    {'other.key': 'other data'},
])
def test_track_extra_information(environ_stub):
    expected = environ_stub.copy()
    expected.update({'appenlight.extra': {'test_section': 'test_value'}})
    appenlight.track_extra_information(
        environ_stub, 'test_section', 'test_value')
    assert environ_stub == expected
