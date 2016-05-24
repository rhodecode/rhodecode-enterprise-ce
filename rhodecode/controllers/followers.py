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
Followers controller for rhodecode
"""

import logging

from pylons import tmpl_context as c, request

from rhodecode.lib.helpers import Page
from rhodecode.lib.auth import LoginRequired, HasRepoPermissionAnyDecorator
from rhodecode.lib.base import BaseRepoController, render
from rhodecode.model.db import UserFollowing
from rhodecode.lib.utils2 import safe_int

log = logging.getLogger(__name__)


class FollowersController(BaseRepoController):

    def __before__(self):
        super(FollowersController, self).__before__()

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def followers(self, repo_name):
        p = safe_int(request.GET.get('page', 1), 1)
        repo_id = c.rhodecode_db_repo.repo_id
        d = UserFollowing.get_repo_followers(repo_id)\
            .order_by(UserFollowing.follows_from)
        c.followers_pager = Page(d, page=p, items_per_page=20)

        c.followers_data = render('/followers/followers_data.html')

        if request.environ.get('HTTP_X_PJAX'):
            return c.followers_data

        return render('/followers/followers.html')
