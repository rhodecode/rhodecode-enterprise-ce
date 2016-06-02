# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016  RhodeCode GmbH
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
Index schema for RhodeCode
"""

from __future__ import absolute_import
import logging
import os
import re

from pylons.i18n.translation import _

from whoosh import query as query_lib, sorting
from whoosh.highlight import HtmlFormatter, ContextFragmenter
from whoosh.index import create_in, open_dir, exists_in, EmptyIndexError
from whoosh.qparser import QueryParser, QueryParserError

import rhodecode.lib.helpers as h
from rhodecode.lib.index import BaseSearch

log = logging.getLogger(__name__)


try:
    # we first try to import from rhodecode tools, fallback to copies if
    # we're unable to
    from rhodecode_tools.lib.fts_index.whoosh_schema import (
        ANALYZER, FILE_INDEX_NAME, FILE_SCHEMA, COMMIT_INDEX_NAME,
        COMMIT_SCHEMA)
except ImportError:
    log.warning('rhodecode_tools schema not available, doing a fallback '
                'import from `rhodecode.lib.index.whoosh_fallback_schema`')
    from rhodecode.lib.index.whoosh_fallback_schema import (
        ANALYZER, FILE_INDEX_NAME, FILE_SCHEMA, COMMIT_INDEX_NAME,
        COMMIT_SCHEMA)


FORMATTER = HtmlFormatter('span', between='\n<span class="break">...</span>\n')
FRAGMENTER = ContextFragmenter(200)

log = logging.getLogger(__name__)



class Search(BaseSearch):

    name = 'whoosh'

    def __init__(self, config):
        self.config = config
        if not os.path.isdir(self.config['location']):
            os.makedirs(self.config['location'])

        opener = create_in
        if exists_in(self.config['location'], indexname=FILE_INDEX_NAME):
            opener = open_dir
        file_index = opener(self.config['location'], schema=FILE_SCHEMA,
                            indexname=FILE_INDEX_NAME)

        opener = create_in
        if exists_in(self.config['location'], indexname=COMMIT_INDEX_NAME):
            opener = open_dir
        changeset_index = opener(self.config['location'], schema=COMMIT_SCHEMA,
                                 indexname=COMMIT_INDEX_NAME)

        self.commit_schema = COMMIT_SCHEMA
        self.commit_index = changeset_index
        self.file_schema = FILE_SCHEMA
        self.file_index = file_index
        self.searcher = None

    def cleanup(self):
        if self.searcher:
            self.searcher.close()

    def _extend_query(self, query):
        hashes = re.compile('([0-9a-f]{5,40})').findall(query)
        if hashes:
            hashes_or_query = ' OR '.join('commit_id:%s*' % h for h in hashes)
            query = u'(%s) OR %s' % (query, hashes_or_query)
        return query

    def search(self, query, document_type, search_user, repo_name=None,
        requested_page=1, page_limit=10, sort=None):

        original_query = query
        query = self._extend_query(query)

        log.debug(u'QUERY: %s on %s', query, document_type)
        result = {
            'results': [],
            'count': 0,
            'error': None,
            'runtime': 0
        }
        search_type, index_name, schema_defn = self._prepare_for_search(
            document_type)
        self._init_searcher(index_name)
        try:
            qp = QueryParser(search_type, schema=schema_defn)
            allowed_repos_filter = self._get_repo_filter(
                search_user, repo_name)
            try:
                query = qp.parse(unicode(query))
                log.debug('query: %s (%s)' % (query, repr(query)))

                reverse, sortedby = False, None
                if search_type == 'message':
                    if sort == 'oldfirst':
                        sortedby = 'date'
                        reverse = False
                    elif sort == 'newfirst':
                        sortedby = 'date'
                        reverse = True

                whoosh_results = self.searcher.search(
                    query, filter=allowed_repos_filter, limit=None,
                    sortedby=sortedby, reverse=reverse)

                # fixes for 32k limit that whoosh uses for highlight
                whoosh_results.fragmenter.charlimit = None
                res_ln = whoosh_results.scored_length()
                result['runtime'] = whoosh_results.runtime
                result['count'] = res_ln
                result['results'] = WhooshResultWrapper(
                    search_type, res_ln, whoosh_results)

            except QueryParserError:
                result['error'] = _('Invalid search query. Try quoting it.')
        except (EmptyIndexError, IOError, OSError):
            msg = _('There is no index to search in. '
                    'Please run whoosh indexer')
            log.exception(msg)
            result['error'] = msg
        except Exception:
            msg = _('An error occurred during this search operation')
            log.exception(msg)
            result['error'] = msg

        return result

    def statistics(self):
        stats = [
            {'key': _('Index Type'), 'value': 'Whoosh'},
            {'key': _('File Index'), 'value': str(self.file_index)},
            {'key': _('Indexed documents'),
             'value': self.file_index.doc_count()},
            {'key': _('Last update'),
             'value': h.time_to_datetime(self.file_index.last_modified())},
            {'key': _('Commit index'), 'value': str(self.commit_index)},
            {'key': _('Indexed documents'),
             'value': str(self.commit_index.doc_count())},
            {'key': _('Last update'),
             'value': h.time_to_datetime(self.commit_index.last_modified())}
        ]
        return stats

    def _get_repo_filter(self, auth_user, repo_name):

        allowed_to_search = [
            repo for repo, perm in
            auth_user.permissions['repositories'].items()
            if perm != 'repository.none']

        if repo_name:
            repo_filter = [query_lib.Term('repository', repo_name)]

        elif 'hg.admin' in auth_user.permissions.get('global', []):
            return None

        else:
            repo_filter = [query_lib.Term('repository', _rn)
                           for _rn in allowed_to_search]
            # in case we're not allowed to search anywhere, it's a trick
            # to tell whoosh we're filtering, on ALL results
            repo_filter = repo_filter or [query_lib.Term('repository', '')]

        return query_lib.Or(repo_filter)

    def _prepare_for_search(self, cur_type):
        search_type = {
            'content': 'content',
            'commit': 'message',
            'path': 'path',
            'repository': 'repository'
        }.get(cur_type, 'content')

        index_name = {
            'content': FILE_INDEX_NAME,
            'commit': COMMIT_INDEX_NAME,
            'path': FILE_INDEX_NAME
        }.get(cur_type, FILE_INDEX_NAME)

        schema_defn = {
            'content': self.file_schema,
            'commit': self.commit_schema,
            'path': self.file_schema
        }.get(cur_type, self.file_schema)

        log.debug('IDX: %s' % index_name)
        log.debug('SCHEMA: %s' % schema_defn)
        return search_type, index_name, schema_defn

    def _init_searcher(self, index_name):
        idx = open_dir(self.config['location'], indexname=index_name)
        self.searcher = idx.searcher()
        return self.searcher


class WhooshResultWrapper(object):
    def __init__(self, search_type, total_hits, results):
        self.search_type = search_type
        self.results = results
        self.total_hits = total_hits

    def __str__(self):
        return '<%s at %s>' % (self.__class__.__name__, len(self))

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return self.total_hits

    def __iter__(self):
        """
        Allows Iteration over results,and lazy generate content

        *Requires* implementation of ``__getitem__`` method.
        """
        for hit in self.results:
            yield self.get_full_content(hit)

    def __getitem__(self, key):
        """
        Slicing of resultWrapper
        """
        i, j = key.start, key.stop
        for hit in self.results[i:j]:
            yield self.get_full_content(hit)

    def get_full_content(self, hit):
        # TODO: marcink: this feels like an overkill, there's a lot of data
        # inside hit object, and we don't need all
        res = dict(hit)

        f_path = ''  # noqa
        if self.search_type in ['content', 'path']:
            f_path = res['path'].split(res['repository'])[-1]
            f_path = f_path.lstrip(os.sep)

        if self.search_type == 'content':
            res.update({'content_short_hl': hit.highlights('content'),
                        'f_path': f_path})
        elif self.search_type == 'path':
            res.update({'f_path': f_path})
        elif self.search_type == 'message':
            res.update({'message_hl': hit.highlights('message')})

        return res
