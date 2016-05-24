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

import mock
import pytest

from rhodecode.model.scm import ScmModel
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_ok, assert_error, crash)
from rhodecode.model.repo import RepoModel


@pytest.mark.usefixtures("testuser_api", "app")
class TestInvalidateCache(object):

    def _set_cache(self, repo_name):
        repo = RepoModel().get_by_repo_name(repo_name)
        repo.scm_instance(cache=True)

    def test_api_invalidate_cache(self, backend):
        self._set_cache(backend.repo_name)

        id_, params = build_data(
            self.apikey, 'invalidate_cache', repoid=backend.repo_name)
        response = api_call(self.app, params)

        expected = {
            'msg': "Cache for repository `%s` was invalidated" % (
                backend.repo_name,),
            'repository': backend.repo_name,
        }
        assert_ok(id_, expected, given=response.body)

    @mock.patch.object(ScmModel, 'mark_for_invalidation', crash)
    def test_api_invalidate_cache_error(self, backend):
        id_, params = build_data(
            self.apikey, 'invalidate_cache', repoid=backend.repo_name)
        response = api_call(self.app, params)

        expected = 'Error occurred during cache invalidation action'
        assert_error(id_, expected, given=response.body)

    def test_api_invalidate_cache_regular_user_no_permission(self, backend):
        self._set_cache(backend.repo_name)

        id_, params = build_data(
            self.apikey_regular, 'invalidate_cache', repoid=backend.repo_name)
        response = api_call(self.app, params)

        expected = "repository `%s` does not exist" % (backend.repo_name,)
        assert_error(id_, expected, given=response.body)
