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

"""
Provides utilities around date and time handling
"""

import datetime
import time


def makedate():
    lt = time.localtime()
    if lt[8] == 1 and time.daylight:
        tz = time.altzone
    else:
        tz = time.timezone
    return time.mktime(lt), tz


def date_fromtimestamp(unixts, tzoffset=0):
    """
    Makes a local datetime object out of unix timestamp

    :param unixts:
    :param tzoffset:
    """

    return datetime.datetime.fromtimestamp(float(unixts))


def date_astimestamp(value):
    """
    Convert a given `datetime.datetime` into a `float` like `time.time`
    """
    return time.mktime(value.timetuple()) + value.microsecond / 1E6


def date_to_timestamp_plus_offset(value):
    """
    Convert a given `datetime.datetime` into a unix timestamp and offset.
    """
    # TODO: johbo: The time handling looks quite fragile here since we mix
    # system time zones with naive datetime instances.
    if value is None:
        value = time.time()
    elif isinstance(value, datetime.datetime):
        assert not is_aware(value), (
            "This code is not prepared to handle aware datetime instances")
        value = date_astimestamp(value)
    return (value, time.timezone)


def is_aware(value):
    """
    Determines if a given datetime.time is aware.

    The logic is described in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo
    """
    return (value.tzinfo is not None
            and value.tzinfo.utcoffset(value) is not None)
