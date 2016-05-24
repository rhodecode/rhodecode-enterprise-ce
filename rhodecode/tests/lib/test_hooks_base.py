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

from rhodecode.lib import hooks_base, utils2


@mock.patch.multiple(
    hooks_base,
    action_logger=mock.Mock(),
    post_push_extension=mock.Mock(),
    Repository=mock.Mock())
def test_post_push_truncates_commits():
    extras = {
        'ip': '127.0.0.1',
        'username': 'test',
        'action': 'push_local',
        'repository': 'test',
        'scm': 'git',
        'config': '',
        'server_url': 'http://example.com',
        'make_lock': None,
        'locked_by': [None],
        'commit_ids': ['abcde12345' * 4] * 30000,
    }
    extras = utils2.AttributeDict(extras)

    hooks_base.post_push(extras)

    # Calculate appropriate action string here
    expected_action = 'push_local:%s' % ','.join(extras.commit_ids[:29000])

    hooks_base.action_logger.assert_called_with(
        extras.username, expected_action, extras.repository, extras.ip,
        commit=True)
