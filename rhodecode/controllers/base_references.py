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

from pylons import tmpl_context as c

from rhodecode.controllers import utils
from rhodecode.lib import helpers as h
from rhodecode.lib.auth import LoginRequired, HasRepoPermissionAnyDecorator
from rhodecode.lib.base import BaseRepoController, render
from rhodecode.lib.ext_json import json
from rhodecode.lib.utils import PartialRenderer
from rhodecode.lib.utils2 import datetime_to_time


class BaseReferencesController(BaseRepoController):
    """
    Base for reference controllers for branches, tags and bookmarks.

    Implement and set the following things:

    - `partials_template` is the source for the partials to use.

    - `template` is the template to render in the end.

    - `_get_reference_items(repo)` should return a sequence of tuples which
      map from `name` to `commit_id`.

    """

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def index(self):
        _render = PartialRenderer(self.partials_template)
        _data = []
        pre_load = ["author", "date", "message"]
        repo = c.rhodecode_repo
        is_svn = h.is_svn(repo)
        format_ref_id = utils.get_format_ref_id(repo)

        for ref_name, commit_id in self._get_reference_items(repo):
            commit = repo.get_commit(
                commit_id=commit_id, pre_load=pre_load)

            # TODO: johbo: Unify generation of reference links
            use_commit_id = '/' in ref_name or is_svn
            files_url = h.url(
                'files_home',
                repo_name=c.repo_name,
                f_path=ref_name if is_svn else '',
                revision=commit_id if use_commit_id else ref_name,
                at=ref_name)

            _data.append({
                "name": _render('name', ref_name, files_url),
                "name_raw": ref_name,
                "date": _render('date', commit.date),
                "date_raw": datetime_to_time(commit.date),
                "author": _render('author', commit.author),
                "commit": _render(
                    'commit', commit.message, commit.raw_id, commit.idx),
                "commit_raw": commit.idx,
                "compare": _render(
                    'compare', format_ref_id(ref_name, commit.raw_id)),
            })
        c.has_references = bool(_data)
        c.data = json.dumps(_data)
        return render(self.template)
