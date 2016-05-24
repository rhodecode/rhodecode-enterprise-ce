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

"""
Single source for redirection links.

Goal of this module is to provide a single source of truth regarding external
links. The data inside this module is used to configure the routing
system of Enterprise and it is used also as a base to check if this data
and our server configuration are in sync.

.. py:data:: link_config

   Contains the configuration for external links. Each item is supposed to be
   a `dict` like this example::

      {"name": "url_name",
       "target": "https://rhodecode.com/r1/enterprise/keyword/",
       "external_target": "https://example.com/some-page.html",
      }

then you can retrieve the url by simply calling the URL function:

`h.url('url_name')`

The redirection must be first implemented in our servers before
you can see it working.
"""
# flake8: noqa
from __future__ import unicode_literals


link_config = [
    {"name": "enterprise_docs",
     "target": "https://rhodecode.com/r1/enterprise/docs/",
     "external_target": "https://docs.rhodecode.com/RhodeCode-Enterprise/",
     },
    {"name": "enterprise_log_file_locations",
     "target": "https://rhodecode.com/r1/enterprise/docs/admin-system-overview/",
     "external_target": "https://docs.rhodecode.com/RhodeCode-Enterprise/admin/system-overview.html#log-files",
     },
    {"name": "enterprise_issue_tracker_settings",
     "target": "https://rhodecode.com/r1/enterprise/docs/issue-trackers-overview/",
     "external_target": "https://docs.rhodecode.com/RhodeCode-Enterprise/issue-trackers/issue-trackers.html",
     },
    {"name": "enterprise_svn_setup",
     "target": "https://rhodecode.com/r1/enterprise/docs/svn-setup/",
     "external_target": "https://docs.rhodecode.com/RhodeCode-Enterprise/admin/svn-http.html",
     },
]


def connect_redirection_links(rmap):
    for link in link_config:
        rmap.connect(link['name'], link['target'], _static=True)
