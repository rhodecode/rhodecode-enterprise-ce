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
import decimal
import io
import textwrap

import pytest

from rhodecode.lib.ext_json import json
from rhodecode.lib.ext_json import formatted_json
from pylons.i18n.translation import _, ungettext


class Timezone(datetime.tzinfo):
    def __init__(self, hours):
        self.hours = hours

    def utcoffset(self, unused_dt):
        return datetime.timedelta(hours=self.hours)


def test_dumps_set():
    result = json.dumps(set((1, 2, 3)))
    # We cannot infer what the order of result is going to be
    result = json.loads(result)
    assert isinstance(result, list)
    assert [1, 2, 3] == sorted(result)


def test_dumps_decimal():
    assert '"1.5"' == json.dumps(decimal.Decimal('1.5'))


def test_dumps_complex():
    assert "[0.0, 1.0]" == json.dumps(1j)
    assert "[1.0, 0.0]" == json.dumps(1 + 0j)
    assert "[1.1, 1.2]" == json.dumps(1.1 + 1.2j)


def test_dumps_object_with_json_method():
    class SerializableObject(object):
        def __json__(self):
            return 'foo'

    assert '"foo"' == json.dumps(SerializableObject())


def test_dumps_object_with_json_attribute():
    class SerializableObject(object):
        __json__ = 'foo'

    assert '"foo"' == json.dumps(SerializableObject())


def test_dumps_time():
    assert '"03:14:15.926"' == json.dumps(datetime.time(3, 14, 15, 926535))


def test_dumps_time_no_microseconds():
    assert '"03:14:15"' == json.dumps(datetime.time(3, 14, 15))


def test_dumps_time_with_timezone():
    with pytest.raises(TypeError) as excinfo:
        json.dumps(datetime.time(3, 14, 15, 926535, Timezone(0)))

    error_msg = str(excinfo.value)
    assert 'Time-zone aware times are not JSON serializable' in error_msg


def test_dumps_date():
    assert '"1969-07-20"' == json.dumps(datetime.date(1969, 7, 20))


def test_dumps_datetime():
    json_data = json.dumps(datetime.datetime(1969, 7, 20, 3, 14, 15, 926535))
    assert '"1969-07-20T03:14:15.926"' == json_data


def test_dumps_datetime_no_microseconds():
    json_data = json.dumps(datetime.datetime(1969, 7, 20, 3, 14, 15))
    assert '"1969-07-20T03:14:15"' == json_data


def test_dumps_datetime_with_utc_timezone():
    json_data = json.dumps(
        datetime.datetime(1969, 7, 20, 3, 14, 15, 926535, Timezone(0)))
    assert '"1969-07-20T03:14:15.926Z"' == json_data


def test_dumps_datetime_with_plus1_timezone():
    json_data = json.dumps(
        datetime.datetime(1969, 7, 20, 3, 14, 15, 926535, Timezone(1)))
    assert '"1969-07-20T03:14:15.926+01:00"' == json_data


def test_dumps_unserializable_class():
    unserializable_obj = object()
    with pytest.raises(TypeError) as excinfo:
        json.dumps(unserializable_obj)

    assert repr(unserializable_obj) in str(excinfo.value)
    assert 'is not JSON serializable' in str(excinfo.value)


def test_dump_is_like_dumps():
    data = {
        'decimal': decimal.Decimal('1.5'),
        'set': set([1]),  # Just one element to guarantee the order
        'complex': 1 - 1j,
        'datetime': datetime.datetime(1969, 7, 20, 3, 14, 15, 926535),
        'time': datetime.time(3, 14, 15, 926535),
        'date': datetime.date(1969, 7, 20),
    }
    json_buffer = io.BytesIO()
    json.dump(data, json_buffer)

    assert json.dumps(data) == json_buffer.getvalue()


def test_formatted_json():
    data = {
        'b': {'2': 2, '1': 1},
        'a': {'3': 3, '4': 4},
    }

    expected_data = textwrap.dedent('''
    {
        "a": {
            "3": 3,
            "4": 4
        },
        "b": {
            "1": 1,
            "2": 2
        }
    }''').strip()

    assert formatted_json(data) == expected_data


def test_pylons_lazy_translation_string(pylonsapp):
    data = {'label': _('hello')}
    data2 = {'label2': ungettext('singular', 'plural', 1)}

    assert json.dumps(data) == '{"label": "hello"}'
    assert json.dumps(data2) == '{"label2": "singular"}'
