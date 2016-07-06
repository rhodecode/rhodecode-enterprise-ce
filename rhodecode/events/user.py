# Copyright (C) 2016-2016  RhodeCode GmbH
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

from zope.interface import implementer

from rhodecode.events.base import RhodecodeEvent
from rhodecode.events.interfaces import (
    IUserRegistered, IUserPreCreate, IUserPreUpdate)


@implementer(IUserRegistered)
class UserRegistered(RhodecodeEvent):
    """
    An instance of this class is emitted as an :term:`event` whenever a user
    account is registered.
    """
    def __init__(self, user, session):
        self.user = user
        self.session = session


@implementer(IUserPreCreate)
class UserPreCreate(RhodecodeEvent):
    """
    An instance of this class is emitted as an :term:`event` before a new user
    object is created.
    """
    def __init__(self, user_data):
        self.user_data = user_data


@implementer(IUserPreUpdate)
class UserPreUpdate(RhodecodeEvent):
    """
    An instance of this class is emitted as an :term:`event` before a user
    object is updated.
    """
    def __init__(self, user, user_data):
        self.user = user
        self.user_data = user_data
