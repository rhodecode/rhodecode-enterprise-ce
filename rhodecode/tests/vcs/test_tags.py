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

from rhodecode.tests.vcs.base import BackendTestMixin
from rhodecode.lib.vcs.exceptions import (
    TagAlreadyExistError, TagDoesNotExistError)


pytestmark = pytest.mark.backends("git", "hg")


class TestTags(BackendTestMixin):

    def test_new_tag(self):
        tip = self.repo.get_commit()
        tagsize = len(self.repo.tags)
        tag = self.repo.tag('last-commit', 'joe', tip.raw_id)

        assert len(self.repo.tags) == tagsize + 1
        for top, __, __ in tip.walk():
            assert top == tag.get_node(top.path)

    def test_tag_already_exist(self):
        tip = self.repo.get_commit()
        self.repo.tag('last-commit', 'joe', tip.raw_id)

        with pytest.raises(TagAlreadyExistError):
            self.repo.tag('last-commit', 'joe', tip.raw_id)

        commit = self.repo.get_commit(commit_idx=0)
        with pytest.raises(TagAlreadyExistError):
            self.repo.tag('last-commit', 'jane', commit.raw_id)

    def test_remove_tag(self):
        tip = self.repo.get_commit()
        self.repo.tag('last-commit', 'joe', tip.raw_id)
        tagsize = len(self.repo.tags)

        self.repo.remove_tag('last-commit', user='evil joe')
        assert len(self.repo.tags) == tagsize - 1

    def test_remove_tag_which_does_not_exist(self):
        with pytest.raises(TagDoesNotExistError):
            self.repo.remove_tag('last-commit', user='evil joe')

    def test_name_with_slash(self):
        self.repo.tag('19/10/11', 'joe')
        assert '19/10/11' in self.repo.tags
        self.repo.tag('11', 'joe')
        assert '11' in self.repo.tags
