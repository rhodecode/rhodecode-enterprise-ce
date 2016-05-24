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

import datetime
from rhodecode.tests import TestController, url
from rhodecode.model.db import UserFollowing, Repository


class TestJournalController(TestController):

    def test_index(self):
        self.log_user()
        response = self.app.get(url(controller='journal', action='index'))
        response.mustcontain(
            """<div class="journal_day">%s</div>""" % datetime.date.today())

    def test_toggle_following_repository(self, backend):
        user = self.log_user()
        repo = Repository.get_by_repo_name(backend.repo_name)
        repo_id = repo.repo_id
        self.app.post(url('toggle_following'), {'follows_repo_id': repo_id,
                                                'csrf_token': self.csrf_token})

        followings = UserFollowing.query()\
            .filter(UserFollowing.user_id == user['user_id'])\
            .filter(UserFollowing.follows_repo_id == repo_id).all()

        assert len(followings) == 0

        self.app.post(url('toggle_following'), {'follows_repo_id': repo_id,
                                                'csrf_token': self.csrf_token})

        followings = UserFollowing.query()\
            .filter(UserFollowing.user_id == user['user_id'])\
            .filter(UserFollowing.follows_repo_id == repo_id).all()

        assert len(followings) == 1

    def test_public_journal_atom(self):
        self.log_user()
        response = self.app.get(url(controller='journal',
                                    action='public_journal_atom'),)

    def test_public_journal_rss(self):
        self.log_user()
        response = self.app.get(url(controller='journal',
                                    action='public_journal_rss'),)
