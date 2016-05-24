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
import urlparse
import uuid

import requests


class RhodeCodeAPI(object):
    """
    Make generic calls to RCE API.

    To call any API method, instanciate the API with the URL of your
    RCE instance and your user token.
    Then use a method call with the name of your API method, and pass the
    correct parameters.

    Will return a dict with the response from the API call

    eg.:
    api = RhodeCodeAPI('http://my.rhodecode.com');
    response = api.comment_pull_request(
        repoid=args.repoid,
        pullrequestid=int(args.prid),
        message=args.message,
        status=args.status
    )
    if response['error']:
        raise Exception(resp['error'])
    else:
        print resp
    """
    headers = {'content-type': 'application/json'}

    def __init__(self, instance_url, user_token):
        self.url = instance_url
        self.key = user_token

    def __getattr__(self, name):
        return lambda **kwargs: self._call(name, **kwargs)

    def _call(self, method, **kwargs):
        payload = {
            'id': str(uuid.uuid4()),
            'api_key': self.key,
            'method': method,
            'args': kwargs
        }
        url = urlparse.urljoin(self.url, '_admin/api')
        resp = requests.post(
            url, data=json.dumps(payload), headers=self.headers)

        if resp.ok:
            return resp.json()
        else:
            resp.raise_for_status()
