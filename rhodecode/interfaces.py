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

from zope.interface import Attribute, Interface


class IUserRegistered(Interface):
    """
    An event type that is emitted whenever a new user registers a user
    account.
    """
    user = Attribute('The user object.')
    session = Attribute('The session while processing the register form post.')


class IUserPreCreate(Interface):
    """
    An event type that is emitted before a new user object is persisted.
    """
    active = Attribute('Value for user.active')


class IUserPreUpdate(Interface):
    """
    An event type that is emitted before a user object is updated.
    """
    user = Attribute('The not yet updated user object')
    active = Attribute('New value for user.active')
