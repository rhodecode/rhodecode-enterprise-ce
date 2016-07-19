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
Summary controller for RhodeCode Enterprise
"""

import logging
from string import lower

from pylons import tmpl_context as c, request
from pylons.i18n.translation import _
from beaker.cache import cache_region, region_invalidate

from rhodecode.config.conf import (LANGUAGES_EXTENSIONS_MAP)
from rhodecode.controllers import utils
from rhodecode.controllers.changelog import _load_changelog_summary
from rhodecode.lib import caches, helpers as h
from rhodecode.lib.utils import jsonify
from rhodecode.lib.utils2 import safe_str
from rhodecode.lib.auth import (
    LoginRequired, HasRepoPermissionAnyDecorator, NotAnonymous, XHRRequired)
from rhodecode.lib.base import BaseRepoController, render
from rhodecode.lib.markup_renderer import MarkupRenderer
from rhodecode.lib.ext_json import json
from rhodecode.lib.vcs.backends.base import EmptyCommit
from rhodecode.lib.vcs.exceptions import (
    CommitError, EmptyRepositoryError, NodeDoesNotExistError)
from rhodecode.model.db import Statistics, CacheKey, User

log = logging.getLogger(__name__)


class SummaryController(BaseRepoController):

    def __before__(self):
        super(SummaryController, self).__before__()

    def __get_readme_data(self, db_repo):
        repo_name = db_repo.repo_name
        log.debug('Looking for README file')
        default_renderer = c.visual.default_renderer

        @cache_region('long_term')
        def _generate_readme(cache_key):
            readme_data = None
            readme_file = None
            try:
                # gets the landing revision or tip if fails
                commit = db_repo.get_landing_commit()
                if isinstance(commit, EmptyCommit):
                    raise EmptyRepositoryError()
                renderer = MarkupRenderer()
                for f in renderer.pick_readme_order(default_renderer):
                    try:
                        node = commit.get_node(f)
                    except NodeDoesNotExistError:
                        continue

                    if not node.is_file():
                        continue

                    readme_file = f
                    log.debug('Found README file `%s` rendering...',
                              readme_file)
                    readme_data = renderer.render(node.content,
                                                  filename=f)
                    break
            except CommitError:
                log.exception("Problem getting commit")
                pass
            except EmptyRepositoryError:
                pass
            except Exception:
                log.exception("General failure")

            return readme_data, readme_file

        invalidator_context = CacheKey.repo_context_cache(
            _generate_readme, repo_name, CacheKey.CACHE_TYPE_README)

        with invalidator_context as context:
            context.invalidate()
            computed = context.compute()

        return computed


    @LoginRequired()
    @HasRepoPermissionAnyDecorator(
        'repository.read', 'repository.write', 'repository.admin')
    def index(self, repo_name):
        username = ''
        if c.rhodecode_user.username != User.DEFAULT_USER:
            username = safe_str(c.rhodecode_user.username)

        _def_clone_uri = _def_clone_uri_by_id = c.clone_uri_tmpl
        if '{repo}' in _def_clone_uri:
            _def_clone_uri_by_id = _def_clone_uri.replace(
                '{repo}', '_{repoid}')
        elif '{repoid}' in _def_clone_uri:
            _def_clone_uri_by_id = _def_clone_uri.replace(
                '_{repoid}', '{repo}')

        c.clone_repo_url = c.rhodecode_db_repo.clone_url(
            user=username, uri_tmpl=_def_clone_uri)
        c.clone_repo_url_id = c.rhodecode_db_repo.clone_url(
            user=username, uri_tmpl=_def_clone_uri_by_id)

        c.show_stats = bool(c.rhodecode_db_repo.enable_statistics)

        stats = self.sa.query(Statistics)\
            .filter(Statistics.repository == c.rhodecode_db_repo)\
            .scalar()

        c.stats_percentage = 0

        if stats and stats.languages:
            c.no_data = False is c.rhodecode_db_repo.enable_statistics
            lang_stats_d = json.loads(stats.languages)

            # Sort first by decreasing count and second by the file extension,
            # so we have a consistent output.
            lang_stats_items = sorted(lang_stats_d.iteritems(),
                                      key=lambda k: (-k[1], k[0]))[:10]
            lang_stats = [(x, {"count": y,
                               "desc": LANGUAGES_EXTENSIONS_MAP.get(x)})
                          for x, y in lang_stats_items]

            c.trending_languages = json.dumps(lang_stats)
        else:
            c.no_data = True
            c.trending_languages = json.dumps({})

        c.enable_downloads = c.rhodecode_db_repo.enable_downloads
        c.repository_followers = self.scm_model.get_followers(
            c.rhodecode_db_repo)
        c.repository_forks = self.scm_model.get_forks(c.rhodecode_db_repo)
        c.repository_is_user_following = self.scm_model.is_following_repo(
            c.repo_name, c.rhodecode_user.user_id)

        if c.repository_requirements_missing:
            return render('summary/missing_requirements.html')

        c.readme_data, c.readme_file = \
            self.__get_readme_data(c.rhodecode_db_repo)

        _load_changelog_summary()

        if request.is_xhr:
            return render('changelog/changelog_summary_data.html')

        return render('summary/summary.html')

    @LoginRequired()
    @XHRRequired()
    @HasRepoPermissionAnyDecorator(
        'repository.read', 'repository.write', 'repository.admin')
    @jsonify
    def repo_stats(self, repo_name, commit_id):
        _namespace = caches.get_repo_namespace_key(
            caches.SUMMARY_STATS, repo_name)
        show_stats = bool(c.rhodecode_db_repo.enable_statistics)
        cache_manager = caches.get_cache_manager('repo_cache_long', _namespace)
        _cache_key = caches.compute_key_from_params(
            repo_name, commit_id, show_stats)

        def compute_stats():
            code_stats = {}
            size = 0
            try:
                scm_instance = c.rhodecode_db_repo.scm_instance()
                commit = scm_instance.get_commit(commit_id)

                for node in commit.get_filenodes_generator():
                    size += node.size
                    if not show_stats:
                        continue
                    ext = lower(node.extension)
                    ext_info = LANGUAGES_EXTENSIONS_MAP.get(ext)
                    if ext_info:
                        if ext in code_stats:
                            code_stats[ext]['count'] += 1
                        else:
                            code_stats[ext] = {"count": 1, "desc": ext_info}
            except EmptyRepositoryError:
                pass
            return {'size': h.format_byte_size_binary(size),
                    'code_stats': code_stats}

        stats = cache_manager.get(_cache_key, createfunc=compute_stats)
        return stats

    def _switcher_reference_data(self, repo_name, references, is_svn):
        """Prepare reference data for given `references`"""
        items = []
        for name, commit_id in references.items():
            use_commit_id = '/' in name or is_svn
            items.append({
                'name': name,
                'commit_id': commit_id,
                'files_url': h.url(
                    'files_home',
                    repo_name=repo_name,
                    f_path=name if is_svn else '',
                    revision=commit_id if use_commit_id else name,
                    at=name)
            })
        return items

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @jsonify
    def repo_refs_data(self, repo_name):
        repo = c.rhodecode_repo
        refs_to_create = [
            (_("Branch"), repo.branches, 'branch'),
            (_("Tag"), repo.tags, 'tag'),
            (_("Bookmark"), repo.bookmarks, 'book'),
        ]
        res = self._create_reference_data(repo, repo_name, refs_to_create)
        data = {
            'more': False,
            'results': res
        }
        return data

    @jsonify
    def repo_refs_changelog_data(self, repo_name):
        repo = c.rhodecode_repo

        refs_to_create = [
            (_("Branches"), repo.branches, 'branch'),
            (_("Closed branches"), repo.branches_closed, 'branch_closed'),
            # TODO: enable when vcs can handle bookmarks filters
            # (_("Bookmarks"), repo.bookmarks, "book"),
        ]
        res = self._create_reference_data(repo, repo_name, refs_to_create)
        data = {
            'more': False,
            'results': res
        }
        return data

    def _create_reference_data(self, repo, full_repo_name, refs_to_create):
        format_ref_id = utils.get_format_ref_id(repo)

        result = []
        for title, refs, ref_type in refs_to_create:
            if refs:
                result.append({
                    'text': title,
                    'children': self._create_reference_items(
                        repo, full_repo_name, refs, ref_type, format_ref_id),
                })
        return result

    def _create_reference_items(self, repo, full_repo_name, refs, ref_type,
                                format_ref_id):
        result = []
        is_svn = h.is_svn(repo)
        for ref_name, raw_id in refs.iteritems():
            files_url = self._create_files_url(
                repo, full_repo_name, ref_name, raw_id, is_svn)
            result.append({
                'text': ref_name,
                'id': format_ref_id(ref_name, raw_id),
                'raw_id': raw_id,
                'type': ref_type,
                'files_url': files_url,
            })
        return result

    def _create_files_url(self, repo, full_repo_name, ref_name, raw_id,
                          is_svn):
        use_commit_id = '/' in ref_name or is_svn
        return h.url(
            'files_home',
            repo_name=full_repo_name,
            f_path=ref_name if is_svn else '',
            revision=raw_id if use_commit_id else ref_name,
            at=ref_name)
