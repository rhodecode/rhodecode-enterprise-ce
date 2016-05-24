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

import datetime
import pytest

from dateutil.tz import tzutc

from rhodecode.lib.datelib import date_to_timestamp_plus_offset


class TestDateTotimestampPlusOffset:

    def test_raises_assertion_error_if_value_is_aware(self):
        value = datetime.datetime(2014, 11, 26, 10, 11, tzinfo=tzutc())
        with pytest.raises(AssertionError):
            date_to_timestamp_plus_offset(value)
