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
Package for testing various helper function for base controller
"""

import pytest

from rhodecode.lib import base


@pytest.mark.parametrize("input, expected", [
    ('127.0.0.1', '127.0.0.1'),
    ('127.0.0.1,127.0.0.2', '127.0.0.1'),
    ('127.0.0.1,127.0.0.2,127.0.0.2,127.0.0.2,,,,', '127.0.0.1'),
    (',', ''),
])
def test_filter_proxy(input, expected):
    assert base._filter_proxy(input) == expected


@pytest.mark.parametrize("input, expected", [
    ('', ''),
    # ipv4
    ('127.0.0.1', '127.0.0.1'),             # localhost IPv4 address
    ('127.0.0.1:80', '127.0.0.1'),          # localhost IPv4 address, +port (80)
    ('127.0.0.1:5000:51021', '127.0.0.1'),  # localhost with dual port
    ('192.168.0.1', '192.168.0.1'),         # private
    ('256.0.0.0', '256.0.0.0'),             # invalid, octet > 255 (currently not detected)
    # ipv6
    ('::1', '::1'),                         # localhost IPv6 address
    ('[::1]:80', '::1'),                    # localhost IPv6 address, +port (80)
    ('::', '::'),                           # unspecified aka 0.0.0.0
    ('2605:2700:0:3::4713:93e3', '2605:2700:0:3::4713:93e3'),                # public IPv6 address
    ('[2605:2700:0:3::4713:93e3]:80', '2605:2700:0:3::4713:93e3'),           # public IPv6 address, +port (80)
    ('2001:db8:85a3:0:0:8a2e:370:7334', '2001:db8:85a3:0:0:8a2e:370:7334'),  # doc, IPv6 for 555-1234
    ('2001:db8:85a3::8a2e:370:7334', '2001:db8:85a3::8a2e:370:7334'),        # doc
    ('[2001:db8:85a3:8d3:1319:8a2e:370:7348]:443', '2001:db8:85a3:8d3:1319:8a2e:370:7348'),  # doc +port
    # ipv6 transitional
    ('::ffff:192.168.0.1', '::ffff:192.168.0.1'),           # private ipv4 transitional
    ('[::ffff:192.168.0.1]:80', '::ffff:192.168.0.1'),      # private ipv4 transitional
])
def test_filter_port(input, expected):
    assert base._filter_port(input) == expected


@pytest.mark.parametrize("input, expected", [
    ({}, '0.0.0.0'),
    ({'REMOTE_ADDR': '127.0.0.0'}, '127.0.0.0'),
    ({'REMOTE_ADDR': '127.0.0.0:8080,127.0.0.2:5000'}, '127.0.0.0'),
])
def test_get_ip_addr(input, expected):
    assert base.get_ip_addr(input) == expected
