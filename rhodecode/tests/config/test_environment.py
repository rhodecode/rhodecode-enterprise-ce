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
import pytest

from rhodecode.config import environment


class TestUseDirectHookCalls(object):
    @pytest.mark.parametrize('config', [
        {
            'vcs.hooks.direct_calls': 'true',
            'base_path': 'fake_base_path'
        }
    ])
    def test_returns_true_when_conditions_are_met(self, config):
        result = environment._use_direct_hook_calls(config)
        assert result is True

    @pytest.mark.parametrize('config', [
        {
            'vcs.hooks.direct_calls': 'false',
            'base_path': 'fake_base_path'
        },
        {
            'base_path': 'fake_base_path'
        }
    ])
    def test_returns_false_when_conditions_are_not_met(self, config):
        result = environment._use_direct_hook_calls(config)
        assert result is False


class TestGetVcsHooksProtocol(object):
    def test_returns_pyro4_by_default(self):
        config = {}
        result = environment._get_vcs_hooks_protocol(config)
        assert result == 'pyro4'

    @pytest.mark.parametrize('protocol', ['PYRO4', 'HTTP', 'Pyro4', 'Http'])
    def test_returns_lower_case_value(self, protocol):
        config = {
            'vcs.hooks.protocol': protocol
        }
        result = environment._get_vcs_hooks_protocol(config)
        assert result == protocol.lower()


class TestLoadEnvironment(object):
    def test_calls_use_direct_hook_calls(self, _external_calls_patcher):
        global_conf = {
            'here': '',
            'vcs.connection_timeout': '0',
            'vcs.server.enable': 'false'
        }
        app_conf = {
            'cache_dir': '/tmp/',
            '__file__': '/tmp/abcde.ini'
        }
        direct_calls_patcher = mock.patch.object(
            environment, '_use_direct_hook_calls', return_value=True)
        protocol_patcher = mock.patch.object(
            environment, '_get_vcs_hooks_protocol', return_value='http')
        with direct_calls_patcher as direct_calls_mock, \
                protocol_patcher as protocol_mock:
            environment.load_environment(global_conf, app_conf)
        direct_calls_mock.call_count == 1
        protocol_mock.call_count == 1


@pytest.fixture
def _external_calls_patcher(request):
    # TODO: mikhail: This is a temporary solution. Ideally load_environment
    # should be split into multiple small testable functions.
    utils_patcher = mock.patch.object(environment, 'utils')

    rhodecode_patcher = mock.patch.object(environment, 'rhodecode')

    db_config = mock.Mock()
    db_config.items.return_value = {
        'paths': [['/tmp/abc', '/tmp/def']]
    }
    db_config_patcher = mock.patch.object(
        environment, 'make_db_config', return_value=db_config)

    set_config_patcher = mock.patch.object(environment, 'set_rhodecode_config')

    utils_patcher.start()
    rhodecode_patcher.start()
    db_config_patcher.start()
    set_config_patcher.start()

    request.addfinalizer(utils_patcher.stop)
    request.addfinalizer(rhodecode_patcher.stop)
    request.addfinalizer(db_config_patcher.stop)
    request.addfinalizer(set_config_patcher.stop)
