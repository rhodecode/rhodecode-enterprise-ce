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

from rhodecode.model.db import Repository, RepositoryField
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_ok, assert_error)


@pytest.mark.usefixtures("testuser_api", "app")
class TestAddFieldToRepo(object):
    def test_api_add_field_to_repo(self, backend):
        repo = backend.create_repo()
        repo_name = repo.repo_name
        id_, params = build_data(
            self.apikey, 'add_field_to_repo',
            repoid=repo_name,
            key='extra_field',
            label='extra_field_label',
            description='extra_field_desc')
        response = api_call(self.app, params)
        expected = {
            'msg': 'Added new repository field `extra_field`',
            'success': True,
        }
        assert_ok(id_, expected, given=response.body)

        repo = Repository.get_by_repo_name(repo_name)
        repo_field = RepositoryField.get_by_key_name('extra_field', repo)
        _data = repo_field.get_dict()
        assert _data['field_desc'] == 'extra_field_desc'
        assert _data['field_key'] == 'extra_field'
        assert _data['field_label'] == 'extra_field_label'

        id_, params = build_data(
            self.apikey, 'add_field_to_repo',
            repoid=repo_name,
            key='extra_field',
            label='extra_field_label',
            description='extra_field_desc')
        response = api_call(self.app, params)
        expected = 'Field with key `extra_field` exists for repo `%s`' % (
            repo_name)
        assert_error(id_, expected, given=response.body)
