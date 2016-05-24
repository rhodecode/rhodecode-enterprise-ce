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
HG inmemory module
"""

from rhodecode.lib.datelib import date_to_timestamp_plus_offset
from rhodecode.lib.utils import safe_str
from rhodecode.lib.vcs.backends.base import BaseInMemoryCommit
from rhodecode.lib.vcs.exceptions import RepositoryError


class MercurialInMemoryCommit(BaseInMemoryCommit):

    def commit(self, message, author, parents=None, branch=None, date=None,
               **kwargs):
        """
        Performs in-memory commit (doesn't check workdir in any way) and
        returns newly created `MercurialCommit`. Updates repository's
        `commit_ids`.

        :param message: message of the commit
        :param author: full username, i.e. "Joe Doe <joe.doe@example.com>"
        :param parents: single parent or sequence of parents from which commit
          would be derived
        :param date: `datetime.datetime` instance. Defaults to
          ``datetime.datetime.now()``.
        :param branch: Optional. Branch name as unicode. Will use the backend's
          default if not given.

        :raises `RepositoryError`: if any error occurs while committing
        """
        self.check_integrity(parents)

        if not isinstance(message, unicode) or not isinstance(author, unicode):
            # TODO: johbo: Should be a TypeError
            raise RepositoryError('Given message and author needs to be '
                                  'an <unicode> instance got %r & %r instead'
                                  % (type(message), type(author)))

        if branch is None:
            branch = self.repository.DEFAULT_BRANCH_NAME
        kwargs['branch'] = safe_str(branch)

        message = safe_str(message)
        author = safe_str(author)

        parent_ids = [p.raw_id if p else None for p in self.parents]

        ENCODING = "UTF-8"

        updated = []
        for node in self.added + self.changed:
            if node.is_binary:
                content = node.content
            else:
                content = node.content.encode(ENCODING)
            updated.append({
                'path': node.path,
                'content': content,
                'mode': node.mode,
            })

        removed = [node.path for node in self.removed]

        date, tz = date_to_timestamp_plus_offset(date)

        new_id = self.repository._remote.commitctx(
            message=message, parents=parent_ids,
            commit_time=date, commit_timezone=tz, user=author,
            files=self.get_paths(), extra=kwargs, removed=removed,
            updated=updated)

        self.repository.commit_ids.append(new_id)
        self.repository._rebuild_cache(self.repository.commit_ids)
        self.repository.branches = self.repository._get_branches()
        tip = self.repository.get_commit()
        self.reset()
        return tip
