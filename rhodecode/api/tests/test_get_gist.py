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

from rhodecode.model.db import Gist
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_error, assert_ok)


@pytest.mark.usefixtures("testuser_api", "app")
class TestApiGetGist(object):
    def test_api_get_gist(self, gist_util):
        gist = gist_util.create_gist()
        gist_id = gist.gist_access_id
        gist_created_on = gist.created_on
        gist_modified_at = gist.modified_at
        id_, params = build_data(
            self.apikey, 'get_gist', gistid=gist_id, )
        response = api_call(self.app, params)

        expected = {
            'access_id': gist_id,
            'created_on': gist_created_on,
            'modified_at': gist_modified_at,
            'description': 'new-gist',
            'expires': -1.0,
            'gist_id': int(gist_id),
            'type': 'public',
            'url': 'http://test.example.com:80/_admin/gists/%s' % (gist_id,),
            'acl_level': Gist.ACL_LEVEL_PUBLIC,
            'content': None,
        }

        assert_ok(id_, expected, given=response.body)

    def test_api_get_gist_with_content(self, gist_util):
        mapping = {
            u'filename1.txt': {'content': u'hello world'},
            u'filename1ą.txt': {'content': u'hello worldę'}
        }
        gist = gist_util.create_gist(gist_mapping=mapping)
        gist_id = gist.gist_access_id
        gist_created_on = gist.created_on
        gist_modified_at = gist.modified_at
        id_, params = build_data(
            self.apikey, 'get_gist', gistid=gist_id, content=True)
        response = api_call(self.app, params)

        expected = {
            'access_id': gist_id,
            'created_on': gist_created_on,
            'modified_at': gist_modified_at,
            'description': 'new-gist',
            'expires': -1.0,
            'gist_id': int(gist_id),
            'type': 'public',
            'url': 'http://test.example.com:80/_admin/gists/%s' % (gist_id,),
            'acl_level': Gist.ACL_LEVEL_PUBLIC,
            'content': {
                u'filename1.txt': u'hello world',
                u'filename1ą.txt': u'hello worldę'
            },
        }

        assert_ok(id_, expected, given=response.body)

    def test_api_get_gist_not_existing(self):
        id_, params = build_data(
            self.apikey_regular, 'get_gist', gistid='12345', )
        response = api_call(self.app, params)
        expected = 'gist `%s` does not exist' % ('12345',)
        assert_error(id_, expected, given=response.body)

    def test_api_get_gist_private_gist_without_permission(self, gist_util):
        gist = gist_util.create_gist()
        gist_id = gist.gist_access_id
        id_, params = build_data(
            self.apikey_regular, 'get_gist', gistid=gist_id, )
        response = api_call(self.app, params)

        expected = 'gist `%s` does not exist' % (gist_id,)
        assert_error(id_, expected, given=response.body)
