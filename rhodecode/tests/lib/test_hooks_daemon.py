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

import json
import logging
from StringIO import StringIO

import mock
import pytest

from rhodecode.lib import hooks_daemon
from rhodecode.tests.utils import assert_message_in_log


class TestDummyHooksCallbackDaemon(object):
    def test_hooks_module_path_set_properly(self):
        daemon = hooks_daemon.DummyHooksCallbackDaemon()
        assert daemon.hooks_module == 'rhodecode.lib.hooks_daemon'

    def test_logs_entering_the_hook(self):
        daemon = hooks_daemon.DummyHooksCallbackDaemon()
        with mock.patch.object(hooks_daemon.log, 'debug') as log_mock:
            with daemon as return_value:
                log_mock.assert_called_once_with(
                    'Running dummy hooks callback daemon')
        assert return_value == daemon

    def test_logs_exiting_the_hook(self):
        daemon = hooks_daemon.DummyHooksCallbackDaemon()
        with mock.patch.object(hooks_daemon.log, 'debug') as log_mock:
            with daemon:
                pass
        log_mock.assert_called_with('Exiting dummy hooks callback daemon')


class TestHooks(object):
    def test_hooks_can_be_used_as_a_context_processor(self):
        hooks = hooks_daemon.Hooks()
        with hooks as return_value:
            pass
        assert hooks == return_value


class TestHooksHttpHandler(object):
    def test_read_request_parses_method_name_and_arguments(self):
        data = {
            'method': 'test',
            'extras': {
                'param1': 1,
                'param2': 'a'
            }
        }
        request = self._generate_post_request(data)
        hooks_patcher = mock.patch.object(
            hooks_daemon.Hooks, data['method'], create=True, return_value=1)

        with hooks_patcher as hooks_mock:
            MockServer(hooks_daemon.HooksHttpHandler, request)

        hooks_mock.assert_called_once_with(data['extras'])

    def test_hooks_serialized_result_is_returned(self):
        request = self._generate_post_request({})
        rpc_method = 'test'
        hook_result = {
            'first': 'one',
            'second': 2
        }
        read_patcher = mock.patch.object(
            hooks_daemon.HooksHttpHandler, '_read_request',
            return_value=(rpc_method, {}))
        hooks_patcher = mock.patch.object(
            hooks_daemon.Hooks, rpc_method, create=True,
            return_value=hook_result)

        with read_patcher, hooks_patcher:
            server = MockServer(hooks_daemon.HooksHttpHandler, request)

        expected_result = json.dumps(hook_result)
        assert server.request.output_stream.buflist[-1] == expected_result

    def test_exception_is_returned_in_response(self):
        request = self._generate_post_request({})
        rpc_method = 'test'
        read_patcher = mock.patch.object(
            hooks_daemon.HooksHttpHandler, '_read_request',
            return_value=(rpc_method, {}))
        hooks_patcher = mock.patch.object(
            hooks_daemon.Hooks, rpc_method, create=True,
            side_effect=Exception('Test exception'))

        with read_patcher, hooks_patcher:
            server = MockServer(hooks_daemon.HooksHttpHandler, request)

        expected_result = json.dumps({
            'exception': 'Exception',
            'exception_args': ('Test exception', )
        })
        assert server.request.output_stream.buflist[-1] == expected_result

    def test_log_message_writes_to_debug_log(self, caplog):
        ip_port = ('0.0.0.0', 8888)
        handler = hooks_daemon.HooksHttpHandler(
            MockRequest('POST /'), ip_port, mock.Mock())
        fake_date = '1/Nov/2015 00:00:00'
        date_patcher = mock.patch.object(
            handler, 'log_date_time_string', return_value=fake_date)
        with date_patcher, caplog.atLevel(logging.DEBUG):
            handler.log_message('Some message %d, %s', 123, 'string')

        expected_message = '{} - - [{}] Some message 123, string'.format(
            ip_port[0], fake_date)
        assert_message_in_log(
            caplog.records(), expected_message,
            levelno=logging.DEBUG, module='hooks_daemon')

    def _generate_post_request(self, data):
        payload = json.dumps(data)
        return 'POST / HTTP/1.0\nContent-Length: {}\n\n{}'.format(
            len(payload), payload)


class ThreadedHookCallbackDaemon(object):
    def test_constructor_calls_prepare(self):
        prepare_daemon_patcher = mock.patch.object(
            hooks_daemon.ThreadedHookCallbackDaemon, '_prepare')
        with prepare_daemon_patcher as prepare_daemon_mock:
            hooks_daemon.ThreadedHookCallbackDaemon()
        prepare_daemon_mock.assert_called_once_with()

    def test_run_is_called_on_context_start(self):
        patchers = mock.patch.multiple(
            hooks_daemon.ThreadedHookCallbackDaemon,
            _run=mock.DEFAULT, _prepare=mock.DEFAULT, __exit__=mock.DEFAULT)

        with patchers as mocks:
            daemon = hooks_daemon.ThreadedHookCallbackDaemon()
            with daemon as daemon_context:
                pass
            mocks['_run'].assert_called_once_with()
        assert daemon_context == daemon

    def test_stop_is_called_on_context_exit(self):
        patchers = mock.patch.multiple(
            hooks_daemon.ThreadedHookCallbackDaemon,
            _run=mock.DEFAULT, _prepare=mock.DEFAULT, _stop=mock.DEFAULT)

        with patchers as mocks:
            daemon = hooks_daemon.ThreadedHookCallbackDaemon()
            with daemon as daemon_context:
                assert mocks['_stop'].call_count == 0

            mocks['_stop'].assert_called_once_with()
        assert daemon_context == daemon


class TestPyro4HooksCallbackDaemon(object):
    def test_prepare_inits_pyro4_and_registers_hooks(self, caplog):
        pyro4_daemon = mock.Mock()

        with self._pyro4_patcher(pyro4_daemon), caplog.atLevel(logging.DEBUG):
            daemon = hooks_daemon.Pyro4HooksCallbackDaemon()

        assert daemon._daemon == pyro4_daemon

        assert pyro4_daemon.register.call_count == 1
        args, kwargs = pyro4_daemon.register.call_args
        assert len(args) == 1
        assert isinstance(args[0], hooks_daemon.Hooks)

        assert_message_in_log(
            caplog.records(),
            'Preparing callback daemon and registering hook object',
            levelno=logging.DEBUG, module='hooks_daemon')

    def test_run_creates_a_thread(self):
        thread = mock.Mock()
        pyro4_daemon = mock.Mock()

        with self._pyro4_patcher(pyro4_daemon):
            daemon = hooks_daemon.Pyro4HooksCallbackDaemon()

        with self._thread_patcher(thread) as thread_mock:
            daemon._run()

        assert thread_mock.call_count == 1
        args, kwargs = thread_mock.call_args
        assert args == ()
        assert kwargs['target'] == pyro4_daemon.requestLoop
        assert kwargs['kwargs']['loopCondition']() is True

    def test_stop_cleans_up_the_connection(self, caplog):
        thread = mock.Mock()
        pyro4_daemon = mock.Mock()

        with self._pyro4_patcher(pyro4_daemon):
            daemon = hooks_daemon.Pyro4HooksCallbackDaemon()

        with self._thread_patcher(thread), caplog.atLevel(logging.DEBUG):
            with daemon:
                assert daemon._daemon == pyro4_daemon
                assert daemon._callback_thread == thread

        assert daemon._daemon is None
        assert daemon._callback_thread is None
        pyro4_daemon.close.assert_called_with()
        thread.join.assert_called_once_with()

        assert_message_in_log(
            caplog.records(), 'Waiting for background thread to finish.',
            levelno=logging.DEBUG, module='hooks_daemon')

    def _pyro4_patcher(self, daemon):
        return mock.patch.object(
            hooks_daemon.Pyro4, 'Daemon', return_value=daemon)

    def _thread_patcher(self, thread):
        return mock.patch.object(
            hooks_daemon.threading, 'Thread', return_value=thread)


class TestHttpHooksCallbackDaemon(object):
    def test_prepare_inits_daemon_variable(self, tcp_server, caplog):
        with self._tcp_patcher(tcp_server), caplog.atLevel(logging.DEBUG):
            daemon = hooks_daemon.HttpHooksCallbackDaemon()
        assert daemon._daemon == tcp_server

        assert_message_in_log(
            caplog.records(),
            'Preparing callback daemon and registering hook object',
            levelno=logging.DEBUG, module='hooks_daemon')

    def test_prepare_inits_hooks_uri_and_logs_it(
            self, tcp_server, caplog):
        with self._tcp_patcher(tcp_server), caplog.atLevel(logging.DEBUG):
            daemon = hooks_daemon.HttpHooksCallbackDaemon()

        _, port = tcp_server.server_address
        expected_uri = '{}:{}'.format(daemon.IP_ADDRESS, port)
        assert daemon.hooks_uri == expected_uri

        assert_message_in_log(
            caplog.records(), 'Hooks uri is: {}'.format(expected_uri),
            levelno=logging.DEBUG, module='hooks_daemon')

    def test_run_creates_a_thread(self, tcp_server):
        thread = mock.Mock()

        with self._tcp_patcher(tcp_server):
            daemon = hooks_daemon.HttpHooksCallbackDaemon()

        with self._thread_patcher(thread) as thread_mock:
            daemon._run()

        thread_mock.assert_called_once_with(
            target=tcp_server.serve_forever,
            kwargs={'poll_interval': daemon.POLL_INTERVAL})
        assert thread.daemon is True
        thread.start.assert_called_once_with()

    def test_run_logs(self, tcp_server, caplog):

        with self._tcp_patcher(tcp_server):
            daemon = hooks_daemon.HttpHooksCallbackDaemon()

        with self._thread_patcher(mock.Mock()), caplog.atLevel(logging.DEBUG):
            daemon._run()

        assert_message_in_log(
            caplog.records(),
            'Running event loop of callback daemon in background thread',
            levelno=logging.DEBUG, module='hooks_daemon')

    def test_stop_cleans_up_the_connection(self, tcp_server, caplog):
        thread = mock.Mock()

        with self._tcp_patcher(tcp_server):
            daemon = hooks_daemon.HttpHooksCallbackDaemon()

        with self._thread_patcher(thread), caplog.atLevel(logging.DEBUG):
            with daemon:
                assert daemon._daemon == tcp_server
                assert daemon._callback_thread == thread

        assert daemon._daemon is None
        assert daemon._callback_thread is None
        tcp_server.shutdown.assert_called_with()
        thread.join.assert_called_once_with()

        assert_message_in_log(
            caplog.records(), 'Waiting for background thread to finish.',
            levelno=logging.DEBUG, module='hooks_daemon')

    def _tcp_patcher(self, tcp_server):
        return mock.patch.object(
            hooks_daemon, 'TCPServer', return_value=tcp_server)

    def _thread_patcher(self, thread):
        return mock.patch.object(
            hooks_daemon.threading, 'Thread', return_value=thread)


class TestPrepareHooksDaemon(object):
    def test_returns_dummy_hooks_callback_daemon_when_using_direct_calls(self):
        expected_extras = {'extra1': 'value1'}
        callback, extras = hooks_daemon.prepare_callback_daemon(
            expected_extras.copy(), use_direct_calls=True)
        assert isinstance(callback, hooks_daemon.DummyHooksCallbackDaemon)
        expected_extras['hooks_module'] = 'rhodecode.lib.hooks_daemon'
        assert extras == expected_extras

    @pytest.mark.parametrize('protocol, expected_class', (
        ('pyro4', hooks_daemon.Pyro4HooksCallbackDaemon),
        ('Pyro4', hooks_daemon.Pyro4HooksCallbackDaemon),
        ('HTTP', hooks_daemon.HttpHooksCallbackDaemon),
        ('http', hooks_daemon.HttpHooksCallbackDaemon)
    ))
    def test_returns_real_hooks_callback_daemon_when_protocol_is_specified(
            self, protocol, expected_class):
        expected_extras = {
            'extra1': 'value1',
            'hooks_protocol': protocol.lower()
        }
        callback, extras = hooks_daemon.prepare_callback_daemon(
            expected_extras.copy(), protocol=protocol)
        assert isinstance(callback, expected_class)
        hooks_uri = extras.pop('hooks_uri')
        assert extras == expected_extras
        if protocol.lower() == 'pyro4':
            assert hooks_uri.startswith('PYRO')


class MockRequest(object):
    def __init__(self, request):
        self.request = request
        self.input_stream = StringIO(b'{}'.format(self.request))
        self.output_stream = StringIO()

    def makefile(self, mode, *args, **kwargs):
        return self.output_stream if mode == 'wb' else self.input_stream


class MockServer(object):
    def __init__(self, Handler, request):
        ip_port = ('0.0.0.0', 8888)
        self.request = MockRequest(request)
        self.handler = Handler(self.request, ip_port, self)


@pytest.fixture
def tcp_server():
    server = mock.Mock()
    server.server_address = ('127.0.0.1', 8881)
    return server
