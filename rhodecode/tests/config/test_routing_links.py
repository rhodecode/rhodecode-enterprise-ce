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

from rhodecode.config import routing_links


def test_connect_redirection_links():
    link_config = [
        {"name": "example_link",
         "external_target": "http://example.com",
         "target": "https://rhodecode.com/r/v1/enterprise/example",
         },
    ]

    rmap = mock.Mock()
    with mock.patch.object(routing_links, 'link_config', link_config):
        routing_links.connect_redirection_links(rmap)

    rmap.connect.assert_called_with(
        link_config[0]['name'], link_config[0]['target'],
        _static=True)
