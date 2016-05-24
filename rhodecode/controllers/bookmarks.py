# -*- coding: utf-8 -*-

# Copyright (C) 2011-2016  RhodeCode GmbH
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
Bookmarks controller for rhodecode
"""

import logging

from pylons import tmpl_context as c
from webob.exc import HTTPNotFound

from rhodecode.controllers.base_references import BaseReferencesController
from rhodecode.lib import helpers as h

log = logging.getLogger(__name__)


class BookmarksController(BaseReferencesController):

    partials_template = 'bookmarks/bookmarks_data.html'
    template = 'bookmarks/bookmarks.html'

    def __before__(self):
        super(BookmarksController, self).__before__()
        if not h.is_hg(c.rhodecode_repo):
            raise HTTPNotFound()

    def _get_reference_items(self, repo):
        return repo.bookmarks.items()
