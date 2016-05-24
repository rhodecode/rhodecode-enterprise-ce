# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016  RhodeCode GmbH
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
SVN inmemory module
"""

from rhodecode.lib.datelib import date_astimestamp
from rhodecode.lib.utils import safe_str
from rhodecode.lib.vcs.backends import base


class SubversionInMemoryCommit(base.BaseInMemoryCommit):

    def commit(self, message, author, parents=None, branch=None, date=None,
               **kwargs):
        if branch not in (None, self.repository.DEFAULT_BRANCH_NAME):
            raise NotImplementedError("Branches are not yet supported")

        self.check_integrity(parents)

        message = safe_str(message)
        author = safe_str(author)

        updated = []
        for node in self.added:
            node_data = {
                'path': node.path,
                'content': safe_str(node.content),
                'mode': node.mode,
            }
            if node.is_binary:
                node_data['properties'] = {
                    'svn:mime-type': 'application/octet-stream'
                }
            updated.append(node_data)
        for node in self.changed:
            updated.append({
                'path': node.path,
                'content': safe_str(node.content),
                'mode': node.mode,
            })

        removed = []
        for node in self.removed:
            removed.append({
                'path': node.path,
            })

        timestamp = date_astimestamp(date) if date else None
        svn_rev = self.repository._remote.commit(
            message=message, author=author, timestamp=timestamp,
            updated=updated, removed=removed)

        # TODO: Find a nicer way. If commit_ids is not yet evaluated, then
        # we should not add the commit_id, if it is already evaluated, it
        # will not be evaluated again.
        commit_id = str(svn_rev)
        if commit_id not in self.repository.commit_ids:
            self.repository.commit_ids.append(commit_id)
        tip = self.repository.get_commit()
        self.reset()
        return tip
