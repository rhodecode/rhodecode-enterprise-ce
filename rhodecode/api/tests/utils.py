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


import random

from rhodecode.api.utils import get_origin
from rhodecode.lib.ext_json import json


API_URL = '/_admin/api'


def assert_ok(id_, expected, given):
    expected = jsonify({
        'id': id_,
        'error': None,
        'result': expected
    })
    given = json.loads(given)
    assert expected == given


def assert_error(id_, expected, given):
    expected = jsonify({
        'id': id_,
        'error': expected,
        'result': None
    })
    given = json.loads(given)
    assert expected == given


def jsonify(obj):
    return json.loads(json.dumps(obj))


def build_data(apikey, method, **kw):
    """
    Builds API data with given random ID

    :param random_id:
    """
    random_id = random.randrange(1, 9999)
    return random_id, json.dumps({
        "id": random_id,
        "api_key": apikey,
        "method": method,
        "args": kw
    })


def api_call(app, params, status=None):
    response = app.post(
        API_URL, content_type='application/json', params=params, status=status)
    return response


def crash(*args, **kwargs):
    raise Exception('Total Crash !')


def expected_permissions(object_with_permissions):
    """
    Returns the expected permissions structure for the given object.

    The object is expected to be a `Repository`, `RepositoryGroup`,
    or `UserGroup`. They all implement the same permission handling
    API.
    """
    permissions = []
    for _user in object_with_permissions.permissions():
        user_data = {
            'name': _user.username,
            'permission': _user.permission,
            'origin': get_origin(_user),
            'type': "user",
        }
        permissions.append(user_data)

    for _user_group in object_with_permissions.permission_user_groups():
        user_group_data = {
            'name': _user_group.users_group_name,
            'permission': _user_group.permission,
            'origin': get_origin(_user_group),
            'type': "user_group",
        }
        permissions.append(user_group_data)
    return permissions
