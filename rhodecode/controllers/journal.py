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
Journal / user event log controller for rhodecode
"""

import logging
from itertools import groupby

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from webhelpers.feedgenerator import Atom1Feed, Rss201rev2Feed

from webob.exc import HTTPBadRequest
from pylons import request, tmpl_context as c, response, url
from pylons.i18n.translation import _

from rhodecode.controllers.admin.admin import _journal_filter
from rhodecode.model.db import UserLog, UserFollowing, User
from rhodecode.model.meta import Session
import rhodecode.lib.helpers as h
from rhodecode.lib.helpers import Page
from rhodecode.lib.auth import LoginRequired, NotAnonymous, CSRFRequired
from rhodecode.lib.base import BaseController, render
from rhodecode.lib.utils2 import safe_int, AttributeDict

log = logging.getLogger(__name__)


class JournalController(BaseController):

    def __before__(self):
        super(JournalController, self).__before__()
        self.language = 'en-us'
        self.ttl = "5"
        self.feed_nr = 20
        c.search_term = request.GET.get('filter')

    def _get_daily_aggregate(self, journal):
        groups = []
        for k, g in groupby(journal, lambda x: x.action_as_day):
            user_group = []
            #groupby username if it's a present value, else fallback to journal username
            for _, g2 in groupby(list(g), lambda x: x.user.username if x.user else x.username):
                l = list(g2)
                user_group.append((l[0].user, l))

            groups.append((k, user_group,))

        return groups

    def _get_journal_data(self, following_repos):
        repo_ids = [x.follows_repository.repo_id for x in following_repos
                    if x.follows_repository is not None]
        user_ids = [x.follows_user.user_id for x in following_repos
                    if x.follows_user is not None]

        filtering_criterion = None

        if repo_ids and user_ids:
            filtering_criterion = or_(UserLog.repository_id.in_(repo_ids),
                        UserLog.user_id.in_(user_ids))
        if repo_ids and not user_ids:
            filtering_criterion = UserLog.repository_id.in_(repo_ids)
        if not repo_ids and user_ids:
            filtering_criterion = UserLog.user_id.in_(user_ids)
        if filtering_criterion is not None:
            journal = self.sa.query(UserLog)\
                .options(joinedload(UserLog.user))\
                .options(joinedload(UserLog.repository))
            #filter
            try:
                journal = _journal_filter(journal, c.search_term)
            except Exception:
                # we want this to crash for now
                raise
            journal = journal.filter(filtering_criterion)\
                        .order_by(UserLog.action_date.desc())
        else:
            journal = []

        return journal

    def _atom_feed(self, repos, public=True):
        journal = self._get_journal_data(repos)
        if public:
            _link = url('public_journal_atom', qualified=True)
            _desc = '%s %s %s' % (c.rhodecode_name, _('public journal'),
                                  'atom feed')
        else:
            _link = url('journal_atom', qualified=True)
            _desc = '%s %s %s' % (c.rhodecode_name, _('journal'), 'atom feed')

        feed = Atom1Feed(title=_desc,
                         link=_link,
                         description=_desc,
                         language=self.language,
                         ttl=self.ttl)

        for entry in journal[:self.feed_nr]:
            user = entry.user
            if user is None:
                #fix deleted users
                user = AttributeDict({'short_contact': entry.username,
                                      'email': '',
                                      'full_contact': ''})
            action, action_extra, ico = h.action_parser(entry, feed=True)
            title = "%s - %s %s" % (user.short_contact, action(),
                                    entry.repository.repo_name)
            desc = action_extra()
            _url = None
            if entry.repository is not None:
                _url = url('changelog_home',
                           repo_name=entry.repository.repo_name,
                           qualified=True)

            feed.add_item(title=title,
                          pubdate=entry.action_date,
                          link=_url or url('', qualified=True),
                          author_email=user.email,
                          author_name=user.full_contact,
                          description=desc)

        response.content_type = feed.mime_type
        return feed.writeString('utf-8')

    def _rss_feed(self, repos, public=True):
        journal = self._get_journal_data(repos)
        if public:
            _link = url('public_journal_atom', qualified=True)
            _desc = '%s %s %s' % (c.rhodecode_name, _('public journal'),
                                  'rss feed')
        else:
            _link = url('journal_atom', qualified=True)
            _desc = '%s %s %s' % (c.rhodecode_name, _('journal'), 'rss feed')

        feed = Rss201rev2Feed(title=_desc,
                         link=_link,
                         description=_desc,
                         language=self.language,
                         ttl=self.ttl)

        for entry in journal[:self.feed_nr]:
            user = entry.user
            if user is None:
                #fix deleted users
                user = AttributeDict({'short_contact': entry.username,
                                      'email': '',
                                      'full_contact': ''})
            action, action_extra, ico = h.action_parser(entry, feed=True)
            title = "%s - %s %s" % (user.short_contact, action(),
                                    entry.repository.repo_name)
            desc = action_extra()
            _url = None
            if entry.repository is not None:
                _url = url('changelog_home',
                           repo_name=entry.repository.repo_name,
                           qualified=True)

            feed.add_item(title=title,
                          pubdate=entry.action_date,
                          link=_url or url('', qualified=True),
                          author_email=user.email,
                          author_name=user.full_contact,
                          description=desc)

        response.content_type = feed.mime_type
        return feed.writeString('utf-8')

    @LoginRequired()
    @NotAnonymous()
    def index(self):
        # Return a rendered template
        p = safe_int(request.GET.get('page', 1), 1)
        c.user = User.get(c.rhodecode_user.user_id)
        following = self.sa.query(UserFollowing)\
            .filter(UserFollowing.user_id == c.rhodecode_user.user_id)\
            .options(joinedload(UserFollowing.follows_repository))\
            .all()

        journal = self._get_journal_data(following)

        def url_generator(**kw):
            return url.current(filter=c.search_term, **kw)

        c.journal_pager = Page(journal, page=p, items_per_page=20, url=url_generator)
        c.journal_day_aggreagate = self._get_daily_aggregate(c.journal_pager)

        c.journal_data = render('journal/journal_data.html')
        if request.is_xhr:
            return c.journal_data

        return render('journal/journal.html')

    @LoginRequired(auth_token_access=True)
    @NotAnonymous()
    def journal_atom(self):
        """
        Produce an atom-1.0 feed via feedgenerator module
        """
        following = self.sa.query(UserFollowing)\
            .filter(UserFollowing.user_id == c.rhodecode_user.user_id)\
            .options(joinedload(UserFollowing.follows_repository))\
            .all()
        return self._atom_feed(following, public=False)

    @LoginRequired(auth_token_access=True)
    @NotAnonymous()
    def journal_rss(self):
        """
        Produce an rss feed via feedgenerator module
        """
        following = self.sa.query(UserFollowing)\
            .filter(UserFollowing.user_id == c.rhodecode_user.user_id)\
            .options(joinedload(UserFollowing.follows_repository))\
            .all()
        return self._rss_feed(following, public=False)

    @CSRFRequired()
    @LoginRequired()
    @NotAnonymous()
    def toggle_following(self):
        user_id = request.POST.get('follows_user_id')
        if user_id:
            try:
                self.scm_model.toggle_following_user(
                    user_id, c.rhodecode_user.user_id)
                Session().commit()
                return 'ok'
            except Exception:
                raise HTTPBadRequest()

        repo_id = request.POST.get('follows_repo_id')
        if repo_id:
            try:
                self.scm_model.toggle_following_repo(
                    repo_id, c.rhodecode_user.user_id)
                Session().commit()
                return 'ok'
            except Exception:
                raise HTTPBadRequest()


    @LoginRequired()
    def public_journal(self):
        # Return a rendered template
        p = safe_int(request.GET.get('page', 1), 1)

        c.following = self.sa.query(UserFollowing)\
            .filter(UserFollowing.user_id == c.rhodecode_user.user_id)\
            .options(joinedload(UserFollowing.follows_repository))\
            .all()

        journal = self._get_journal_data(c.following)

        c.journal_pager = Page(journal, page=p, items_per_page=20)

        c.journal_day_aggreagate = self._get_daily_aggregate(c.journal_pager)

        c.journal_data = render('journal/journal_data.html')
        if request.is_xhr:
            return c.journal_data
        return render('journal/public_journal.html')

    @LoginRequired(auth_token_access=True)
    def public_journal_atom(self):
        """
        Produce an atom-1.0 feed via feedgenerator module
        """
        c.following = self.sa.query(UserFollowing)\
            .filter(UserFollowing.user_id == c.rhodecode_user.user_id)\
            .options(joinedload(UserFollowing.follows_repository))\
            .all()

        return self._atom_feed(c.following)

    @LoginRequired(auth_token_access=True)
    def public_journal_rss(self):
        """
        Produce an rss2 feed via feedgenerator module
        """
        c.following = self.sa.query(UserFollowing)\
            .filter(UserFollowing.user_id == c.rhodecode_user.user_id)\
            .options(joinedload(UserFollowing.follows_repository))\
            .all()

        return self._rss_feed(c.following)
