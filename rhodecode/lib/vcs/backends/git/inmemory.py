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
GIT inmemory module
"""

from rhodecode.lib.datelib import date_to_timestamp_plus_offset
from rhodecode.lib.utils import safe_str
from rhodecode.lib.vcs.backends import base


class GitInMemoryCommit(base.BaseInMemoryCommit):

    def commit(self, message, author, parents=None, branch=None, date=None,
               **kwargs):
        """
        Performs in-memory commit (doesn't check workdir in any way) and
        returns newly created `GitCommit`. Updates repository's
        `commit_ids`.

        :param message: message of the commit
        :param author: full username, i.e. "Joe Doe <joe.doe@example.com>"
        :param parents: single parent or sequence of parents from which commit
          would be derived
        :param date: `datetime.datetime` instance. Defaults to
          ``datetime.datetime.now()``.
        :param branch: branch name, as string. If none given, default backend's
          branch would be used.

        :raises `CommitError`: if any error occurs while committing
        """
        self.check_integrity(parents)
        if branch is None:
            branch = self.repository.DEFAULT_BRANCH_NAME

        ENCODING = "UTF-8"

        commit_tree = None
        if self.parents[0]:
            commit_tree = self.parents[0]._commit['tree']

        updated = []
        for node in self.added + self.changed:
            if not node.is_binary:
                content = node.content.encode(ENCODING)
            else:
                content = node.content
            updated.append({
                'path': node.path,
                'node_path': node.name.encode(ENCODING),
                'content': content,
                'mode': node.mode,
            })

        removed = [node.path for node in self.removed]

        date, tz = date_to_timestamp_plus_offset(date)

        # TODO: johbo: Make kwargs explicit and check if this is needed.
        author_time = kwargs.pop('author_time', date)
        author_tz = kwargs.pop('author_timezone', tz)

        commit_data = {
            'parents': [p._commit['id'] for p in self.parents if p],
            'author': safe_str(author),
            'committer': safe_str(author),
            'encoding': ENCODING,
            'message': safe_str(message),
            'commit_time': int(date),
            'author_time': int(author_time),
            'commit_timezone': tz,
            'author_timezone': author_tz,
        }

        commit_id = self.repository._remote.commit(
            commit_data, branch, commit_tree, updated, removed)

        # Update vcs repository object
        self.repository.commit_ids.append(commit_id)
        self.repository._rebuild_cache(self.repository.commit_ids)

        # invalidate parsed refs after commit
        self.repository._parsed_refs = self.repository._get_parsed_refs()
        self.repository.branches = self.repository._get_branches()
        tip = self.repository.get_commit()
        self.reset()
        return tip
