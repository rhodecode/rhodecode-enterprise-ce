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

from datetime import datetime
from marshmallow import Schema, fields
from pyramid.threadlocal import get_current_request
from rhodecode.lib.utils2 import AttributeDict


SYSTEM_USER = AttributeDict(dict(
    username='__SYSTEM__'
))


class UserSchema(Schema):
    """
    Marshmallow schema for a user
    """
    username = fields.Str()


class RhodecodeEventSchema(Schema):
    """
    Marshmallow schema for a rhodecode event
    """
    utc_timestamp = fields.DateTime()
    actor = fields.Nested(UserSchema)
    actor_ip = fields.Str()
    name = fields.Str(attribute='name')


class RhodecodeEvent(object):
    """
    Base event class for all Rhodecode events
    """
    MarshmallowSchema = RhodecodeEventSchema

    def __init__(self):
        self.request = get_current_request()
        self.utc_timestamp = datetime.utcnow()

    @property
    def actor(self):
        if self.request:
            return self.request.user.get_instance()
        return SYSTEM_USER

    @property
    def actor_ip(self):
        if self.request:
            return self.request.user.ip_addr
        return '<no ip available>'

    def as_dict(self):
        return self.MarshmallowSchema().dump(self).data