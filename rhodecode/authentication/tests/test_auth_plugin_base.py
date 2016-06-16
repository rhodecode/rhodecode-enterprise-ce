# Copyright (C) 2016  RhodeCode GmbH
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

"""
Checks around the API of the class RhodeCodeAuthPluginBase.
"""

from rhodecode.authentication.base import RhodeCodeAuthPluginBase


def test_str_returns_plugin_id():
    plugin = RhodeCodeAuthPluginBase(plugin_id='stub_plugin_id')
    assert str(plugin) == 'stub_plugin_id'
