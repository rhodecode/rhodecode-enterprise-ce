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

from rhodecode.lib.utils2 import (
    obfuscate_url_pw, get_routes_generator_for_server_url)


def test_obfuscate_url_pw():
    engine = u'/home/repos/malmö'
    assert obfuscate_url_pw(engine)


@pytest.mark.parametrize('scheme', ['https', 'http'])
@pytest.mark.parametrize('domain', [
    'www.test.com', 'test.com', 'test.co.uk', '192.168.1.3'])
@pytest.mark.parametrize('port', [None, '80', '443', '999'])
@pytest.mark.parametrize('script_path', [None, '/', '/prefix', '/prefix/more'])
def test_routes_generator(pylonsapp, scheme, domain, port, script_path):
    server_url = '%s://%s' % (scheme, domain)
    if port is not None:
        server_url += ':' + port
    if script_path:
        server_url += script_path


    expected_url = '%s://%s' % (scheme, domain)
    if scheme == 'https':
        if port not in (None, '443'):
            expected_url += ':' + port
    elif scheme == 'http':
        if port not in ('80', None):
            expected_url += ':' + port

    if script_path:
        expected_url = (expected_url + script_path).rstrip('/')

    url_generator = get_routes_generator_for_server_url(server_url)
    assert url_generator(
        '/a_test_path', qualified=True) == expected_url + '/a_test_path'
