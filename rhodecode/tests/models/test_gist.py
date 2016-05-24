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

from rhodecode.model.gist import GistModel
from rhodecode.model.repo import RepoModel


class TestGistModel(object):
    def test_create_uses_global_config(self, user_util, backend_hg):
        model = GistModel()
        owner = user_util.create_user()
        repo = backend_hg.create_repo()

        create_repo_patch = mock.patch.object(
            RepoModel, '_create_filesystem_repo',
            return_value=repo.scm_instance())
        with create_repo_patch as create_repo_mock:
            gist_mapping = {
                'filename.txt': {
                    'content': 'Test content'
                }
            }
            model.create('Test description', owner, gist_mapping)
        _, kwargs = create_repo_mock.call_args
        assert kwargs['use_global_config'] is True
