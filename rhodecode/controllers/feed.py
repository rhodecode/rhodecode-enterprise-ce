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
Feed controller for RhodeCode
"""

import logging

import pytz
from pylons import url, response, tmpl_context as c
from pylons.i18n.translation import _

from beaker.cache import cache_region, region_invalidate
from webhelpers.feedgenerator import Atom1Feed, Rss201rev2Feed

from rhodecode.model.db import CacheKey
from rhodecode.lib import helpers as h
from rhodecode.lib import caches
from rhodecode.lib.auth import LoginRequired, HasRepoPermissionAnyDecorator
from rhodecode.lib.base import BaseRepoController
from rhodecode.lib.diffs import DiffProcessor, LimitedDiffContainer
from rhodecode.lib.utils2 import safe_int, str2bool
from rhodecode.lib.utils import PartialRenderer

log = logging.getLogger(__name__)


class FeedController(BaseRepoController):

    def _get_config(self):
        import rhodecode
        config = rhodecode.CONFIG

        return {
            'language': 'en-us',
            'feed_ttl': '5',  # TTL of feed,
            'feed_include_diff':
                str2bool(config.get('rss_include_diff', False)),
            'feed_items_per_page':
                safe_int(config.get('rss_items_per_page', 20)),
            'feed_diff_limit':
                # we need to protect from parsing huge diffs here other way
                # we can kill the server
                safe_int(config.get('rss_cut_off_limit', 32 * 1024)),
        }

    @LoginRequired(auth_token_access=True)
    def __before__(self):
        super(FeedController, self).__before__()
        config = self._get_config()
        # common values for feeds
        self.description = _('Changes on %s repository')
        self.title = self.title = _('%s %s feed') % (c.rhodecode_name, '%s')
        self.language = config["language"]
        self.ttl = config["feed_ttl"]
        self.feed_include_diff = config['feed_include_diff']
        self.feed_diff_limit = config['feed_diff_limit']
        self.feed_items_per_page = config['feed_items_per_page']

    def __changes(self, commit):
        diff_processor = DiffProcessor(
            commit.diff(), diff_limit=self.feed_diff_limit)
        _parsed = diff_processor.prepare(inline_diff=False)
        limited_diff = isinstance(_parsed, LimitedDiffContainer)

        return _parsed, limited_diff

    def _get_title(self, commit):
        return h.shorter(commit.message, 160)

    def _get_description(self, commit):
        _renderer = PartialRenderer('feed/atom_feed_entry.mako')
        parsed_diff, limited_diff = self.__changes(commit)
        return _renderer(
            'body',
            commit=commit,
            parsed_diff=parsed_diff,
            limited_diff=limited_diff,
            feed_include_diff=self.feed_include_diff,
        )

    def _set_timezone(self, date, tzinfo=pytz.utc):
        if not getattr(date, "tzinfo", None):
            date.replace(tzinfo=tzinfo)
        return date

    def _get_commits(self):
        return list(c.rhodecode_repo[-self.feed_items_per_page:])

    @HasRepoPermissionAnyDecorator(
        'repository.read', 'repository.write', 'repository.admin')
    def atom(self, repo_name):
        """Produce an atom-1.0 feed via feedgenerator module"""

        @cache_region('long_term')
        def _generate_feed(cache_key):
            feed = Atom1Feed(
                title=self.title % repo_name,
                link=url('summary_home', repo_name=repo_name, qualified=True),
                description=self.description % repo_name,
                language=self.language,
                ttl=self.ttl
            )

            for commit in reversed(self._get_commits()):
                date = self._set_timezone(commit.date)
                feed.add_item(
                    title=self._get_title(commit),
                    author_name=commit.author,
                    description=self._get_description(commit),
                    link=url('changeset_home', repo_name=repo_name,
                             revision=commit.raw_id, qualified=True),
                    pubdate=date,)

            return feed.mime_type, feed.writeString('utf-8')

        invalidator_context = CacheKey.repo_context_cache(
            _generate_feed, repo_name, CacheKey.CACHE_TYPE_ATOM)

        with invalidator_context as context:
            context.invalidate()
            mime_type, feed = context.compute()

        response.content_type = mime_type
        return feed

    @HasRepoPermissionAnyDecorator(
        'repository.read', 'repository.write', 'repository.admin')
    def rss(self, repo_name):
        """Produce an rss2 feed via feedgenerator module"""

        @cache_region('long_term')
        def _generate_feed(cache_key):
            feed = Rss201rev2Feed(
                title=self.title % repo_name,
                link=url('summary_home', repo_name=repo_name,
                         qualified=True),
                description=self.description % repo_name,
                language=self.language,
                ttl=self.ttl
            )

            for commit in reversed(self._get_commits()):
                date = self._set_timezone(commit.date)
                feed.add_item(
                    title=self._get_title(commit),
                    author_name=commit.author,
                    description=self._get_description(commit),
                    link=url('changeset_home', repo_name=repo_name,
                             revision=commit.raw_id, qualified=True),
                    pubdate=date,)

            return feed.mime_type, feed.writeString('utf-8')

        invalidator_context = CacheKey.repo_context_cache(
            _generate_feed, repo_name, CacheKey.CACHE_TYPE_RSS)

        with invalidator_context as context:
            context.invalidate()
            mime_type, feed = context.compute()

        response.content_type = mime_type
        return feed
