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

from rhodecode.model.meta import Session
from rhodecode.model.user import UserModel
from rhodecode.tests import TEST_USER_ADMIN_LOGIN


@pytest.fixture(scope="class")
def testuser_api(request, pylonsapp):
    cls = request.cls
    cls.usr = UserModel().get_by_username(TEST_USER_ADMIN_LOGIN)
    cls.apikey = cls.usr.api_key
    cls.test_user = UserModel().create_or_update(
        username='test-api',
        password='test',
        email='test@api.rhodecode.org',
        firstname='first',
        lastname='last'
    )
    Session().commit()
    cls.TEST_USER_LOGIN = cls.test_user.username
    cls.apikey_regular = cls.test_user.api_key
