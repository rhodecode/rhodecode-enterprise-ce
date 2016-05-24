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

from rhodecode.lib.vcs.nodes import FileNode
from rhodecode.tests.vcs.base import BackendTestMixin


class TestGetslice(BackendTestMixin):

    @classmethod
    def _get_commits(cls):
        start_date = datetime.datetime(2010, 1, 1, 20)
        for x in xrange(5):
            yield {
                'message': 'Commit %d' % x,
                'author': 'Joe Doe <joe.doe@example.com>',
                'date': start_date + datetime.timedelta(hours=12 * x),
                'added': [
                    FileNode('file_%d.txt' % x, content='Foobar %d' % x),
                ],
            }

    def test__getslice__last_item_is_tip(self):
        assert list(self.repo[-1:])[0] == self.repo.get_commit()

    def test__getslice__respects_start_index(self):
        assert list(self.repo[2:]) == \
            [self.repo.get_commit(commit_id)
             for commit_id in self.repo.commit_ids[2:]]

    def test__getslice__respects_negative_start_index(self):
        assert list(self.repo[-2:]) == \
            [self.repo.get_commit(commit_id)
             for commit_id in self.repo.commit_ids[-2:]]

    def test__getslice__respects_end_index(self):
        assert list(self.repo[:2]) == \
            [self.repo.get_commit(commit_id)
             for commit_id in self.repo.commit_ids[:2]]

    def test__getslice__respects_negative_end_index(self):
        assert list(self.repo[:-2]) == \
            [self.repo.get_commit(commit_id)
             for commit_id in self.repo.commit_ids[:-2]]

    def test__getslice__start_grater_than_end(self):
        assert list(self.repo[10:0]) == []

    def test__getslice__negative_iteration(self):
        assert list(self.repo[::-1]) == \
            [self.repo.get_commit(commit_id)
             for commit_id in self.repo.commit_ids[::-1]]

    def test__getslice__iterate_even(self):
        assert list(self.repo[0:10:2]) == \
            [self.repo.get_commit(commit_id)
             for commit_id in self.repo.commit_ids[0:10:2]]
