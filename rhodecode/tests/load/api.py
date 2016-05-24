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

import requests


class ApiError(Exception):
    """Error when accessing the API."""
    def __init__(self, response):
        super(ApiError, self).__init__(response.get('error'))
        self.response = response


class RCApi(object):
    """Helper class for accessing the RhodeCode API."""

    def __init__(self, api_key,
                 rc_endpoint='http://admin:qweqwe@localhost:5000'):
        self.api_key = api_key
        self.rc_endpoint = rc_endpoint.rstrip('/')
        self.api_endpoint = '%s/_admin/api' % self.rc_endpoint
        self._id = 1

    def _execute(self, data):
        data.update({
            'id': self._id,
            'api_key': self.api_key,
        })
        self._id += 1
        response = requests.post(self.api_endpoint, data=json.dumps(data))
        try:
            json_response = response.json()
        except Exception:
            json_response = {}
        if response.status_code != 200 or json_response.get('error'):
            raise ApiError(json_response)

        return json_response

    def create_repo(self, name, repo_type, description):
        data = {
            'method': 'create_repo',
            'args': {
                'repo_name': name,
                'repo_type': repo_type,
                'description': description,
            }
        }
        self._execute(data)

        return '%s/%s' % (self.rc_endpoint, name)

    def delete_repo(self, name):
        data = {
            'method': 'delete_repo',
            'args': {
                'repoid': name,
            }
        }

        return self._execute(data)
