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

import pytest

from rhodecode.lib.vcs.exceptions import CommitDoesNotExistError
from rhodecode.lib.vcs.nodes import FileNode
from rhodecode.tests.vcs.base import BackendTestMixin


class TestGetitem(BackendTestMixin):

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

    def test_last_item_is_tip(self):
        assert self.repo[-1] == self.repo.get_commit()

    @pytest.mark.parametrize("offset, message", [
        (-1, 'Commit 4'),
        (-2, 'Commit 3'),
        (-5, 'Commit 0'),
    ])
    def test_negative_offset_fetches_correct_commit(self, offset, message):
        assert self.repo[offset].message == message

    def test_returns_correct_items(self):
        commits = [self.repo[x] for x in xrange(len(self.repo.commit_ids))]
        assert commits == list(self.repo.get_commits())

    def test_raises_for_next_commit(self):
        next_commit_idx = len(self.repo.commit_ids)
        with pytest.raises(CommitDoesNotExistError):
            self.repo[next_commit_idx]

    def test_raises_for_not_existing_commit_idx(self):
        not_existing_commit_idx = 1000
        with pytest.raises(CommitDoesNotExistError):
            self.repo[not_existing_commit_idx]
