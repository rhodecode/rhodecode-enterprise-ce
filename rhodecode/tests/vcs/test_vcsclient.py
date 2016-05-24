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

import mock
import Pyro4
import pytest
from Pyro4.errors import TimeoutError, ConnectionClosedError

from rhodecode.lib.vcs import client, create_vcsserver_proxy
from rhodecode.lib.vcs.conf import settings


@pytest.fixture
def short_timeout(request):
    old_timeout = Pyro4.config.COMMTIMEOUT
    Pyro4.config.COMMTIMEOUT = 0.5

    @request.addfinalizer
    def cleanup():
        Pyro4.config.COMMTIMEOUT = old_timeout

    return Pyro4.config.COMMTIMEOUT


@pytest.mark.timeout(20)
def test_vcs_connections_have_a_timeout_set(pylonsapp, short_timeout):
    server_and_port = pylonsapp.config['vcs.server']
    proxy_objects = []
    with pytest.raises(TimeoutError):
        # TODO: johbo: Find a better way to set this number
        while xrange(100):
            server = create_vcsserver_proxy(server_and_port)
            server.ping()
            proxy_objects.append(server)


def test_vcs_remote_calls_are_bound_by_timeout(pylonsapp, short_timeout):
    server_and_port = pylonsapp.config['vcs.server']
    with pytest.raises(TimeoutError):
        server = create_vcsserver_proxy(server_and_port)
        server.sleep(short_timeout + 1.0)


def test_wrap_remote_call_triggers_reconnect():
    # First call fails, the second is successful
    func = mock.Mock(side_effect=[ConnectionClosedError, None])
    proxy_mock = mock.Mock()

    wrapped_func = client._wrap_remote_call(proxy_mock, func)
    wrapped_func()
    proxy_mock._pyroReconnect.assert_called_with(
        tries=settings.PYRO_RECONNECT_TRIES)
