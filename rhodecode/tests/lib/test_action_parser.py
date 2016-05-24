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

from rhodecode.lib.action_parser import ActionParser
from rhodecode.model.db import UserLog


@pytest.mark.parametrize('pr_key', [
    'user_commented_pull_request',
    'user_closed_pull_request',
    'user_merged_pull_request'
])
def test_action_map_pr_values(pylonsapp, pr_key):
    parser = ActionParser(UserLog(action="test:test"))
    assert pr_key in parser.action_map
