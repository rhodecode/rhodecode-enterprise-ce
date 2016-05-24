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
import random

from rhodecode.model import db


@pytest.mark.parametrize("DBModel, id_attr", [
    (db.ChangesetComment, 'comment_id'),
    (db.PullRequest, 'pull_request_id'),
    (db.PullRequestVersion, 'pull_request_version_id'),
])
class TestModelReprImplementation:

    def test_repr_without_id(self, DBModel, id_attr):
        instance = DBModel()
        expected_repr = '<DB:%s at %#x>' % (DBModel.__name__, id(instance))
        assert repr(instance) == expected_repr

    def test_repr_with_id(self, DBModel, id_attr):
        test_id = random.randint(1, 10)
        instance = DBModel()
        setattr(instance, id_attr, test_id)
        expected_repr = (
            '<DB:%s #%d>' % (DBModel.__name__, test_id))
        assert repr(instance) == expected_repr


def test_get_locking_state_invalid_action(user_regular):
    repo = db.Repository()
    action = 'not_push_neither_pull'
    with pytest.raises(ValueError):
        repo.get_locking_state(action, user_id=user_regular.user_id)


def test_get_locking_state_valid_action(user_regular):
    repo = db.Repository()
    action = 'push'
    make_lock, locked, lock_info = repo.get_locking_state(
        action, user_id=user_regular.user_id)
    assert not make_lock
    assert not locked
    assert lock_info == [None, None, None]
