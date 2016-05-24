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
repository permission model for RhodeCode
"""

import logging
from rhodecode.model import BaseModel
from rhodecode.model.db import UserRepoToPerm, UserGroupRepoToPerm, \
    Permission

log = logging.getLogger(__name__)


class RepositoryPermissionModel(BaseModel):

    cls = UserRepoToPerm

    def get_user_permission(self, repository, user):
        repository = self._get_repo(repository)
        user = self._get_user(user)

        return UserRepoToPerm.query() \
                .filter(UserRepoToPerm.user == user) \
                .filter(UserRepoToPerm.repository == repository) \
                .scalar()

    def update_user_permission(self, repository, user, permission):
        permission = Permission.get_by_key(permission)
        current = self.get_user_permission(repository, user)
        if current:
            if not current.permission is permission:
                current.permission = permission
        else:
            p = UserRepoToPerm()
            p.user = user
            p.repository = repository
            p.permission = permission
            self.sa.add(p)

    def delete_user_permission(self, repository, user):
        current = self.get_user_permission(repository, user)
        if current:
            self.sa.delete(current)

    def get_users_group_permission(self, repository, users_group):
        return UserGroupRepoToPerm.query() \
                .filter(UserGroupRepoToPerm.users_group == users_group) \
                .filter(UserGroupRepoToPerm.repository == repository) \
                .scalar()

    def update_users_group_permission(self, repository, users_group,
                                      permission):
        permission = Permission.get_by_key(permission)
        current = self.get_users_group_permission(repository, users_group)
        if current:
            if not current.permission is permission:
                current.permission = permission
        else:
            p = UserGroupRepoToPerm()
            p.users_group = users_group
            p.repository = repository
            p.permission = permission
            self.sa.add(p)

    def delete_users_group_permission(self, repository, users_group):
        current = self.get_users_group_permission(repository, users_group)
        if current:
            self.sa.delete(current)

    def update_or_delete_user_permission(self, repository, user, permission):
        if permission:
            self.update_user_permission(repository, user, permission)
        else:
            self.delete_user_permission(repository, user)

    def update_or_delete_users_group_permission(self, repository, user_group,
                                              permission):
        if permission:
            self.update_users_group_permission(repository, user_group,
                                               permission)
        else:
            self.delete_users_group_permission(repository, user_group)
