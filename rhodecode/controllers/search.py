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
Search controller for RhodeCode
"""

import logging
import urllib

from pylons import request, config, tmpl_context as c

from webhelpers.util import update_params

from rhodecode.lib.auth import LoginRequired, AuthUser
from rhodecode.lib.base import BaseRepoController, render
from rhodecode.lib.helpers import Page
from rhodecode.lib.utils2 import safe_str, safe_int
from rhodecode.lib.index import searcher_from_config
from rhodecode.model import validation_schema

log = logging.getLogger(__name__)


class SearchController(BaseRepoController):

    @LoginRequired()
    def index(self, repo_name=None):

        searcher = searcher_from_config(config)
        formatted_results = []
        execution_time = ''

        schema = validation_schema.SearchParamsSchema()

        search_params = {}
        errors = []
        try:
            search_params = schema.deserialize(
                dict(search_query=request.GET.get('q'),
                     search_type=request.GET.get('type'),
                     page_limit=request.GET.get('page_limit'),
                     requested_page=request.GET.get('page'))
            )
        except validation_schema.Invalid as e:
            errors = e.children

        search_query = search_params.get('search_query')
        search_type = search_params.get('search_type')

        if search_params.get('search_query'):
            page_limit = search_params['page_limit']
            requested_page = search_params['requested_page']

            def url_generator(**kw):
                q = urllib.quote(safe_str(search_query))
                return update_params(
                    "?q=%s&type=%s" % (q, safe_str(search_type)), **kw)

            c.perm_user = AuthUser(user_id=c.rhodecode_user.user_id,
                                   ip_addr=self.ip_addr)

            try:
                search_result = searcher.search(
                    search_query, search_type, c.perm_user, repo_name)

                formatted_results = Page(
                    search_result['results'], page=requested_page,
                    item_count=search_result['count'],
                    items_per_page=page_limit, url=url_generator)
            finally:
                searcher.cleanup()

            if not search_result['error']:
                execution_time = '%s results (%.3f seconds)' % (
                    search_result['count'],
                    search_result['runtime'])
            elif not errors:
                node = schema['search_query']
                errors = [
                    validation_schema.Invalid(node, search_result['error'])]

        c.errors = errors
        c.formatted_results = formatted_results
        c.runtime = execution_time
        c.cur_query = search_query
        c.search_type = search_type
        # Return a rendered template
        return render('/search/search.html')
