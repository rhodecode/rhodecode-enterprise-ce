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

from rhodecode.lib.db_manage import DbManage
from rhodecode.model import db


@pytest.fixture
def db_manage(pylonsapp):
    db_manage = DbManage(
        log_sql=True, dbconf='fake', root='fake', tests=False,
        cli_args={}, SESSION=db.Session())
    return db_manage


@pytest.fixture(autouse=True)
def session_rollback(pylonsapp, request):
    """
    Rollback the database session after the test run.

    Intended usage is for tests wich mess with the database but don't
    commit. In this case a rollback after the test run will leave the database
    in a clean state.

    This is still a workaround until we find a way to isolate the tests better
    from each other.
    """
    @request.addfinalizer
    def cleanup():
        db.Session().rollback()


def test_create_admin_and_prompt_uses_getpass(db_manage):
    db_manage.cli_args = {
        'username': 'test',
        'email': 'test@example.com'}
    with mock.patch('getpass.getpass', return_value='password') as getpass:
        db_manage.create_admin_and_prompt()
    assert getpass.called


def test_create_admin_and_prompt_sets_the_api_key(db_manage):
    db_manage.cli_args = {
        'username': 'test',
        'password': 'testpassword',
        'email': 'test@example.com',
        'api_key': 'testkey'}
    with mock.patch.object(db_manage, 'create_user') as create_user:
        db_manage.create_admin_and_prompt()

    assert create_user.call_args[1]['api_key'] == 'testkey'


def test_create_user_sets_the_api_key(db_manage):
    db_manage.create_user(
        'test', 'testpassword', 'test@example.com',
        api_key='testkey')

    user = db.User.get_by_username('test')
    assert user.api_key == 'testkey'


def test_create_user_without_api_key(db_manage):
    db_manage.create_user('test', 'testpassword', 'test@example.com')
    user = db.User.get_by_username('test')
    assert user.api_key
