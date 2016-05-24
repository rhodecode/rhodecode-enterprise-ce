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
Users profile controller
"""

from pylons import tmpl_context as c
from webob.exc import HTTPNotFound

from rhodecode.lib.auth import LoginRequired, NotAnonymous
from rhodecode.lib.base import BaseController, render
from rhodecode.model.db import User
from rhodecode.model.user import UserModel


class UsersController(BaseController):
    @LoginRequired()
    @NotAnonymous()
    def user_profile(self, username):
        c.user = UserModel().get_by_username(username)
        if not c.user or c.user.username == User.DEFAULT_USER:
            raise HTTPNotFound()

        c.active = 'user_profile'
        return render('users/user.html')
