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

import base64

import mock
import pytest
import webtest.app

from rhodecode.lib.caching_query import FromCache
from rhodecode.lib.hooks_daemon import (
    Pyro4HooksCallbackDaemon, DummyHooksCallbackDaemon,
    HttpHooksCallbackDaemon)
from rhodecode.lib.middleware import simplevcs
from rhodecode.lib.middleware.https_fixup import HttpsFixup
from rhodecode.lib.middleware.utils import scm_app
from rhodecode.model.db import User, _hash_key
from rhodecode.model.meta import Session
from rhodecode.tests import (
    HG_REPO, TEST_USER_ADMIN_LOGIN, TEST_USER_ADMIN_PASS)
from rhodecode.tests.lib.middleware import mock_scm_app
from rhodecode.tests.utils import set_anonymous_access


class StubVCSController(simplevcs.SimpleVCS):

    SCM = 'hg'
    stub_response_body = tuple()

    def _get_repository_name(self, environ):
        return HG_REPO

    def _get_action(self, environ):
        return "pull"

    def _create_wsgi_app(self, repo_path, repo_name, config):
        def fake_app(environ, start_response):
            start_response('200 OK', [])
            return self.stub_response_body
        return fake_app

    def _create_config(self, extras, repo_name):
        return None


@pytest.fixture
def vcscontroller(pylonsapp, config_stub):
    config_stub.testing_securitypolicy()
    config_stub.include('rhodecode.authentication')

    set_anonymous_access(True)
    controller = StubVCSController(pylonsapp, pylonsapp.config)
    app = HttpsFixup(controller, pylonsapp.config)
    app = webtest.app.TestApp(app)

    _remove_default_user_from_query_cache()

    # Sanity checks that things are set up correctly
    app.get('/' + HG_REPO, status=200)

    app.controller = controller
    return app


def _remove_default_user_from_query_cache():
    user = User.get_default_user(cache=True)
    query = Session().query(User).filter(User.username == user.username)
    query = query.options(FromCache(
        "sql_cache_short", "get_user_%s" % _hash_key(user.username)))
    query.invalidate()
    Session().expire(user)


@pytest.fixture
def disable_anonymous_user(request, pylonsapp):
    set_anonymous_access(False)

    @request.addfinalizer
    def cleanup():
        set_anonymous_access(True)


def test_handles_exceptions_during_permissions_checks(
        vcscontroller, disable_anonymous_user):
    user_and_pass = '%s:%s' % (TEST_USER_ADMIN_LOGIN, TEST_USER_ADMIN_PASS)
    auth_password = base64.encodestring(user_and_pass).strip()
    extra_environ = {
        'AUTH_TYPE': 'Basic',
        'HTTP_AUTHORIZATION': 'Basic %s' % auth_password,
        'REMOTE_USER': TEST_USER_ADMIN_LOGIN,
    }

    # Verify that things are hooked up correctly
    vcscontroller.get('/', status=200, extra_environ=extra_environ)

    # Simulate trouble during permission checks
    with mock.patch('rhodecode.model.db.User.get_by_username',
                    side_effect=Exception) as get_user:
        # Verify that a correct 500 is returned and check that the expected
        # code path was hit.
        vcscontroller.get('/', status=500, extra_environ=extra_environ)
        assert get_user.called


def test_returns_forbidden_if_no_anonymous_access(
        vcscontroller, disable_anonymous_user):
    vcscontroller.get('/', status=401)


class StubFailVCSController(simplevcs.SimpleVCS):
    def _handle_request(self, environ, start_response):
        raise Exception("BOOM")


@pytest.fixture(scope='module')
def fail_controller(pylonsapp):
    controller = StubFailVCSController(pylonsapp, pylonsapp.config)
    controller = HttpsFixup(controller, pylonsapp.config)
    controller = webtest.app.TestApp(controller)
    return controller


def test_handles_exceptions_as_internal_server_error(fail_controller):
    fail_controller.get('/', status=500)


def test_provides_traceback_for_appenlight(fail_controller):
    response = fail_controller.get(
        '/', status=500, extra_environ={'appenlight.client': 'fake'})
    assert 'appenlight.__traceback' in response.request.environ


def test_provides_utils_scm_app_as_scm_app_by_default(pylonsapp):
    controller = StubVCSController(pylonsapp, pylonsapp.config)
    assert controller.scm_app is scm_app


def test_allows_to_override_scm_app_via_config(pylonsapp):
    config = pylonsapp.config.copy()
    config['vcs.scm_app_implementation'] = (
        'rhodecode.tests.lib.middleware.mock_scm_app')
    controller = StubVCSController(pylonsapp, config)
    assert controller.scm_app is mock_scm_app


@pytest.mark.parametrize('query_string, expected', [
    ('cmd=stub_command', True),
    ('cmd=listkeys', False),
])
def test_should_check_locking(query_string, expected):
    result = simplevcs._should_check_locking(query_string)
    assert result == expected


@mock.patch.multiple(
    'Pyro4.config', SERVERTYPE='multiplex', POLLTIMEOUT=0.01)
class TestGenerateVcsResponse:

    def test_ensures_that_start_response_is_called_early_enough(self):
        self.call_controller_with_response_body(iter(['a', 'b']))
        assert self.start_response.called

    def test_invalidates_cache_after_body_is_consumed(self):
        result = self.call_controller_with_response_body(iter(['a', 'b']))
        assert not self.was_cache_invalidated()
        # Consume the result
        list(result)
        assert self.was_cache_invalidated()

    @mock.patch('rhodecode.lib.middleware.simplevcs.HTTPLockedRC')
    def test_handles_locking_exception(self, http_locked_rc):
        result = self.call_controller_with_response_body(
            self.raise_result_iter(vcs_kind='repo_locked'))
        assert not http_locked_rc.called
        # Consume the result
        list(result)
        assert http_locked_rc.called

    @mock.patch('rhodecode.lib.middleware.simplevcs.HTTPRequirementError')
    def test_handles_requirement_exception(self, http_requirement):
        result = self.call_controller_with_response_body(
            self.raise_result_iter(vcs_kind='requirement'))
        assert not http_requirement.called
        # Consume the result
        list(result)
        assert http_requirement.called

    @mock.patch('rhodecode.lib.middleware.simplevcs.HTTPLockedRC')
    def test_handles_locking_exception_in_app_call(self, http_locked_rc):
        app_factory_patcher = mock.patch.object(
            StubVCSController, '_create_wsgi_app')
        with app_factory_patcher as app_factory:
            app_factory().side_effect = self.vcs_exception()
            result = self.call_controller_with_response_body(['a'])
            list(result)
        assert http_locked_rc.called

    def test_raises_unknown_exceptions(self):
        result = self.call_controller_with_response_body(
            self.raise_result_iter(vcs_kind='unknown'))
        with pytest.raises(Exception):
            list(result)

    def test_prepare_callback_daemon_is_called(self):
        def side_effect(extras):
            return DummyHooksCallbackDaemon(), extras

        prepare_patcher = mock.patch.object(
            StubVCSController, '_prepare_callback_daemon')
        with prepare_patcher as prepare_mock:
            prepare_mock.side_effect = side_effect
            self.call_controller_with_response_body(iter(['a', 'b']))
        assert prepare_mock.called
        assert prepare_mock.call_count == 1

    def call_controller_with_response_body(self, response_body):
        controller = StubVCSController(None, {'base_path': 'fake_base_path'})
        controller._invalidate_cache = mock.Mock()
        controller.stub_response_body = response_body
        self.start_response = mock.Mock()
        result = controller._generate_vcs_response(
            environ={}, start_response=self.start_response,
            repo_path='fake_repo_path',
            repo_name='fake_repo_name',
            extras={}, action='push')
        self.controller = controller
        return result

    def raise_result_iter(self, vcs_kind='repo_locked'):
        """
        Simulates an exception due to a vcs raised exception if kind vcs_kind
        """
        raise self.vcs_exception(vcs_kind=vcs_kind)
        yield "never_reached"

    def vcs_exception(self, vcs_kind='repo_locked'):
        locked_exception = Exception('TEST_MESSAGE')
        locked_exception._vcs_kind = vcs_kind
        return locked_exception

    def was_cache_invalidated(self):
        return self.controller._invalidate_cache.called


class TestInitializeGenerator:

    def test_drains_first_element(self):
        gen = self.factory(['__init__', 1, 2])
        result = list(gen)
        assert result == [1, 2]

    @pytest.mark.parametrize('values', [
        [],
        [1, 2],
    ])
    def test_raises_value_error(self, values):
        with pytest.raises(ValueError):
            self.factory(values)

    @simplevcs.initialize_generator
    def factory(self, iterable):
        for elem in iterable:
            yield elem


class TestPrepareHooksDaemon(object):
    def test_calls_imported_prepare_callback_daemon(self):
        config = {
            'base_path': 'fake_base_path',
            'vcs.hooks.direct_calls': False,
            'vcs.hooks.protocol': 'http'
        }
        expected_extras = {'extra1': 'value1'}
        daemon = DummyHooksCallbackDaemon()

        controller = StubVCSController(None, config)
        prepare_patcher = mock.patch.object(
            simplevcs, 'prepare_callback_daemon',
            return_value=(daemon, expected_extras))
        with prepare_patcher as prepare_mock:
            callback_daemon, extras = controller._prepare_callback_daemon(
                expected_extras.copy())
        prepare_mock.assert_called_once_with(
            expected_extras, protocol='http', use_direct_calls=False)

        assert callback_daemon == daemon
        assert extras == extras
