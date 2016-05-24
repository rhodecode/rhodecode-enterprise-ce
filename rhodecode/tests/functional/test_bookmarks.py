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

from rhodecode.model.db import Repository
from rhodecode.tests import *


class TestBookmarksController(TestController):

    def test_index(self, backend):
        self.log_user()
        if backend.alias == 'hg':
            response = self.app.get(url(controller='bookmarks',
                                        action='index',
                                        repo_name=backend.repo_name))

            repo = Repository.get_by_repo_name(backend.repo_name)
            for commit_id, obj_name in repo.scm_instance().bookmarks.items():
                assert commit_id in response
                assert obj_name in response
        else:
            self.app.get(url(controller='bookmarks',
                             action='index',
                             repo_name=backend.repo_name), status=404)