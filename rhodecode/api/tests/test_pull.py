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

import os

import pytest

from rhodecode.tests import TESTS_TMP_PATH
from rhodecode.api.tests.utils import (
    build_data, api_call, assert_ok, assert_error)


@pytest.mark.usefixtures("testuser_api", "app")
class TestPull(object):
    @pytest.mark.backends("git", "hg")
    def test_api_pull(self, backend):
        r = backend.create_repo()
        repo_name = r.repo_name
        r.clone_uri = os.path.join(TESTS_TMP_PATH, backend.repo_name)

        id_, params = build_data(self.apikey, 'pull', repoid=repo_name,)
        response = api_call(self.app, params)

        expected = {'msg': 'Pulled from `%s`' % (repo_name,),
                    'repository': repo_name}
        assert_ok(id_, expected, given=response.body)

    def test_api_pull_error(self, backend):
        id_, params = build_data(
            self.apikey, 'pull', repoid=backend.repo_name)
        response = api_call(self.app, params)

        expected = 'Unable to pull changes from `%s`' % (backend.repo_name,)
        assert_error(id_, expected, given=response.body)
