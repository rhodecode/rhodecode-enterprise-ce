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
Controller for Admin panel of RhodeCode Enterprise
"""


import logging

from pylons import request, tmpl_context as c, url
from pylons.controllers.util import redirect
from sqlalchemy.orm import joinedload
from whoosh.qparser.default import QueryParser, query
from whoosh.qparser.dateparse import DateParserPlugin
from whoosh.fields import (TEXT, Schema, DATETIME)
from sqlalchemy.sql.expression import or_, and_, func

from rhodecode.model.db import UserLog, PullRequest
from rhodecode.lib.auth import LoginRequired, HasPermissionAllDecorator
from rhodecode.lib.base import BaseController, render
from rhodecode.lib.utils2 import safe_int, remove_prefix, remove_suffix
from rhodecode.lib.helpers import Page


log = logging.getLogger(__name__)

# JOURNAL SCHEMA used only to generate queries in journal. We use whoosh
# querylang to build sql queries and filter journals
JOURNAL_SCHEMA = Schema(
    username=TEXT(),
    date=DATETIME(),
    action=TEXT(),
    repository=TEXT(),
    ip=TEXT(),
)


def _journal_filter(user_log, search_term):
    """
    Filters sqlalchemy user_log based on search_term with whoosh Query language
    http://packages.python.org/Whoosh/querylang.html

    :param user_log:
    :param search_term:
    """
    log.debug('Initial search term: %r' % search_term)
    qry = None
    if search_term:
        qp = QueryParser('repository', schema=JOURNAL_SCHEMA)
        qp.add_plugin(DateParserPlugin())
        qry = qp.parse(unicode(search_term))
        log.debug('Filtering using parsed query %r' % qry)

    def wildcard_handler(col, wc_term):
        if wc_term.startswith('*') and not wc_term.endswith('*'):
            # postfix == endswith
            wc_term = remove_prefix(wc_term, prefix='*')
            return func.lower(col).endswith(wc_term)
        elif wc_term.startswith('*') and wc_term.endswith('*'):
            # wildcard == ilike
            wc_term = remove_prefix(wc_term, prefix='*')
            wc_term = remove_suffix(wc_term, suffix='*')
            return func.lower(col).contains(wc_term)

    def get_filterion(field, val, term):

        if field == 'repository':
            field = getattr(UserLog, 'repository_name')
        elif field == 'ip':
            field = getattr(UserLog, 'user_ip')
        elif field == 'date':
            field = getattr(UserLog, 'action_date')
        elif field == 'username':
            field = getattr(UserLog, 'username')
        else:
            field = getattr(UserLog, field)
        log.debug('filter field: %s val=>%s' % (field, val))

        # sql filtering
        if isinstance(term, query.Wildcard):
            return wildcard_handler(field, val)
        elif isinstance(term, query.Prefix):
            return func.lower(field).startswith(func.lower(val))
        elif isinstance(term, query.DateRange):
            return and_(field >= val[0], field <= val[1])
        return func.lower(field) == func.lower(val)

    if isinstance(qry, (query.And, query.Term, query.Prefix, query.Wildcard,
                        query.DateRange)):
        if not isinstance(qry, query.And):
            qry = [qry]
        for term in qry:
            field = term.fieldname
            val = (term.text if not isinstance(term, query.DateRange)
                   else [term.startdate, term.enddate])
            user_log = user_log.filter(get_filterion(field, val, term))
    elif isinstance(qry, query.Or):
        filters = []
        for term in qry:
            field = term.fieldname
            val = (term.text if not isinstance(term, query.DateRange)
                   else [term.startdate, term.enddate])
            filters.append(get_filterion(field, val, term))
        user_log = user_log.filter(or_(*filters))

    return user_log


class AdminController(BaseController):

    @LoginRequired()
    def __before__(self):
        super(AdminController, self).__before__()

    @HasPermissionAllDecorator('hg.admin')
    def index(self):
        users_log = UserLog.query()\
            .options(joinedload(UserLog.user))\
            .options(joinedload(UserLog.repository))

        # FILTERING
        c.search_term = request.GET.get('filter')
        try:
            users_log = _journal_filter(users_log, c.search_term)
        except Exception:
            # we want this to crash for now
            raise

        users_log = users_log.order_by(UserLog.action_date.desc())

        p = safe_int(request.GET.get('page', 1), 1)

        def url_generator(**kw):
            return url.current(filter=c.search_term, **kw)

        c.users_log = Page(users_log, page=p, items_per_page=10,
                           url=url_generator)
        c.log_data = render('admin/admin_log.html')

        if request.is_xhr:
            return c.log_data
        return render('admin/admin.html')

    # global redirect doesn't need permissions
    def pull_requests(self, pull_request_id):
        """
        Global redirect for Pull Requests

        :param pull_request_id: id of pull requests in the system
        """
        pull_request = PullRequest.get_or_404(pull_request_id)
        repo_name = pull_request.target_repo.repo_name
        return redirect(url(
            'pullrequest_show', repo_name=repo_name,
            pull_request_id=pull_request_id))
