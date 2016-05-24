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

import os
import time
import logging
import datetime
import hashlib
import tempfile
from os.path import join as jn

from tempfile import _RandomNameSequence

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand

import pylons
import pylons.test
from pylons import config, url
from pylons.i18n.translation import _get_translator
from pylons.util import ContextObj

from routes.util import URLGenerator
from webtest import TestApp
from nose.plugins.skip import SkipTest
import pytest

from rhodecode import is_windows
from rhodecode.model.meta import Session
from rhodecode.model.db import User
from rhodecode.lib import auth
from rhodecode.lib.helpers import flash, link_to
from rhodecode.lib.utils2 import safe_unicode, safe_str

# TODO: johbo: Solve time zone related issues and remove this tweak
os.environ['TZ'] = 'UTC'
if not is_windows:
    time.tzset()

log = logging.getLogger(__name__)

__all__ = [
    'get_new_dir', 'TestController', 'SkipTest',
    'url', 'link_to', 'ldap_lib_installed', 'clear_all_caches',
    'assert_session_flash', 'login_user',
    'TESTS_TMP_PATH', 'HG_REPO', 'GIT_REPO', 'SVN_REPO',
    'NEW_HG_REPO', 'NEW_GIT_REPO',
    'HG_FORK', 'GIT_FORK', 'TEST_USER_ADMIN_LOGIN', 'TEST_USER_ADMIN_PASS',
    'TEST_USER_REGULAR_LOGIN', 'TEST_USER_REGULAR_PASS',
    'TEST_USER_REGULAR_EMAIL', 'TEST_USER_REGULAR2_LOGIN',
    'TEST_USER_REGULAR2_PASS', 'TEST_USER_REGULAR2_EMAIL', 'TEST_HG_REPO',
    'TEST_HG_REPO_CLONE', 'TEST_HG_REPO_PULL', 'TEST_GIT_REPO',
    'TEST_GIT_REPO_CLONE', 'TEST_GIT_REPO_PULL', 'SCM_TESTS',
]

# Invoke websetup with the current config file
# SetupCommand('setup-app').run([config_file])

# SOME GLOBALS FOR TESTS
TEST_DIR = tempfile.gettempdir()

TESTS_TMP_PATH = jn(TEST_DIR, 'rc_test_%s' % _RandomNameSequence().next())
TEST_USER_ADMIN_LOGIN = 'test_admin'
TEST_USER_ADMIN_PASS = 'test12'
TEST_USER_ADMIN_EMAIL = 'test_admin@mail.com'

TEST_USER_REGULAR_LOGIN = 'test_regular'
TEST_USER_REGULAR_PASS = 'test12'
TEST_USER_REGULAR_EMAIL = 'test_regular@mail.com'

TEST_USER_REGULAR2_LOGIN = 'test_regular2'
TEST_USER_REGULAR2_PASS = 'test12'
TEST_USER_REGULAR2_EMAIL = 'test_regular2@mail.com'

HG_REPO = 'vcs_test_hg'
GIT_REPO = 'vcs_test_git'
SVN_REPO = 'vcs_test_svn'

NEW_HG_REPO = 'vcs_test_hg_new'
NEW_GIT_REPO = 'vcs_test_git_new'

HG_FORK = 'vcs_test_hg_fork'
GIT_FORK = 'vcs_test_git_fork'

## VCS
SCM_TESTS = ['hg', 'git']
uniq_suffix = str(int(time.mktime(datetime.datetime.now().timetuple())))

TEST_GIT_REPO = jn(TESTS_TMP_PATH, GIT_REPO)
TEST_GIT_REPO_CLONE = jn(TESTS_TMP_PATH, 'vcsgitclone%s' % uniq_suffix)
TEST_GIT_REPO_PULL = jn(TESTS_TMP_PATH, 'vcsgitpull%s' % uniq_suffix)

TEST_HG_REPO = jn(TESTS_TMP_PATH, HG_REPO)
TEST_HG_REPO_CLONE = jn(TESTS_TMP_PATH, 'vcshgclone%s' % uniq_suffix)
TEST_HG_REPO_PULL = jn(TESTS_TMP_PATH, 'vcshgpull%s' % uniq_suffix)

TEST_REPO_PREFIX = 'vcs-test'


# skip ldap tests if LDAP lib is not installed
ldap_lib_installed = False
try:
    import ldap
    ldap_lib_installed = True
except ImportError:
    # means that python-ldap is not installed
    pass


def clear_all_caches():
    from beaker.cache import cache_managers
    for _cache in cache_managers.values():
        _cache.clear()


def get_new_dir(title):
    """
    Returns always new directory path.
    """
    from rhodecode.tests.vcs.utils import get_normalized_path
    name_parts = [TEST_REPO_PREFIX]
    if title:
        name_parts.append(title)
    hex_str = hashlib.sha1('%s %s' % (os.getpid(), time.time())).hexdigest()
    name_parts.append(hex_str)
    name = '-'.join(name_parts)
    path = os.path.join(TEST_DIR, name)
    return get_normalized_path(path)


@pytest.mark.usefixtures('app', 'index_location')
class TestController(object):

    maxDiff = None

    def log_user(self, username=TEST_USER_ADMIN_LOGIN,
                 password=TEST_USER_ADMIN_PASS):
        self._logged_username = username
        self._session = login_user_session(self.app, username, password)
        self.csrf_token = auth.get_csrf_token(self._session)

        return self._session['rhodecode_user']

    def logout_user(self):
        logout_user_session(self.app, auth.get_csrf_token(self._session))
        self.csrf_token = None
        self._logged_username = None
        self._session = None

    def _get_logged_user(self):
        return User.get_by_username(self._logged_username)

    # TODO: remove, use plain assert in tests
    def assertEqual(self, a, b, msg=None):
        if msg:
            assert a == b, msg
        else:
            assert a == b


def login_user_session(
        app, username=TEST_USER_ADMIN_LOGIN, password=TEST_USER_ADMIN_PASS):
    response = app.post(url(controller='login', action='index'),
                        {'username': username,
                         'password': password})

    if 'invalid user name' in response.body:
        pytest.fail('could not login using %s %s' % (username, password))

    assert response.status == '302 Found'
    ses = response.session['rhodecode_user']
    assert ses.get('username') == username
    response = response.follow()
    assert ses.get('is_authenticated')

    return response.session


def logout_user_session(app, csrf_token):
    app.post(
        url(controller='login', action='logout'),
        {'csrf_token': csrf_token}, status=302)


def login_user(app, username=TEST_USER_ADMIN_LOGIN,
               password=TEST_USER_ADMIN_PASS):
    return login_user_session(app, username, password)['rhodecode_user']


def assert_session_flash(response=None, msg=None, category=None):
    """
    Assert on a flash message in the current session.

    :param msg: Required. The expected message. Will be evaluated if a
        :class:`LazyString` is passed in.
    :param response: Optional. For functional testing, pass in the response
        object. Otherwise don't pass in any value.
    :param category: Optional. If passed, the message category will be
        checked as well.
    """
    if msg is None:
        raise ValueError("Parameter msg is required.")

    messages = flash.pop_messages()
    message = messages[0]

    msg = _eval_if_lazy(msg)
    message_text = _eval_if_lazy(message.message)

    if msg not in message_text:
        msg = u'msg `%s` not found in session flash: got `%s` instead' % (
            msg, message_text)
        pytest.fail(safe_str(msg))
    if category:
        assert category == message.category


def _eval_if_lazy(value):
    return value.eval() if hasattr(value, 'eval') else value


def assert_not_in_session_flash(response, msg, category=None):
    assert 'flash' in response.session, 'Response session has no flash key'
    message_category, message_text = response.session['flash'][0]
    if msg in message_text:
        msg = u'msg `%s` found in session flash: got `%s` instead' % (
            msg, message_text)
        pytest.fail(safe_str(msg))
    if category:
        assert category == message_category


def assert_session_flash_is_empty(response):
    if 'flash' in response.session:
        msg = 'flash messages are present in session:%s' % \
              response.session['flash'][0]
        pytest.fail(safe_str(msg))
