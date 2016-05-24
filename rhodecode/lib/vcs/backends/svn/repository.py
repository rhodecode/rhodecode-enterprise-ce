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
SVN repository module
"""

import logging
import os
import urllib

from zope.cachedescriptors.property import Lazy as LazyProperty

from rhodecode.lib.compat import OrderedDict
from rhodecode.lib.datelib import date_astimestamp
from rhodecode.lib.utils import safe_str, safe_unicode
from rhodecode.lib.vcs import connection, path as vcspath
from rhodecode.lib.vcs.backends import base
from rhodecode.lib.vcs.backends.svn.commit import (
    SubversionCommit, _date_from_svn_properties)
from rhodecode.lib.vcs.backends.svn.diff import SubversionDiff
from rhodecode.lib.vcs.backends.svn.inmemory import SubversionInMemoryCommit
from rhodecode.lib.vcs.conf import settings
from rhodecode.lib.vcs.exceptions import (
    CommitDoesNotExistError, EmptyRepositoryError, RepositoryError,
    VCSError, NodeDoesNotExistError)


log = logging.getLogger(__name__)


class SubversionRepository(base.BaseRepository):
    """
    Subversion backend implementation

    .. important::

       It is very important to distinguish the commit index and the commit id
       which is assigned by Subversion. The first one is always handled as an
       `int` by this implementation. The commit id assigned by Subversion on
       the other side will always be a `str`.

       There is a specific trap since the first commit will have the index
       ``0`` but the svn id will be ``"1"``.

    """

    # Note: Subversion does not really have a default branch name.
    DEFAULT_BRANCH_NAME = None

    contact = base.BaseRepository.DEFAULT_CONTACT
    description = base.BaseRepository.DEFAULT_DESCRIPTION

    def __init__(self, repo_path, config=None, create=False, src_url=None,
                 **kwargs):
        self.path = safe_str(os.path.abspath(repo_path))
        self.config = config if config else base.Config()
        self._remote = connection.Svn(
            self.path, self.config)

        self._init_repo(create, src_url)

        self.bookmarks = {}

    def _init_repo(self, create, src_url):
        if create and os.path.exists(self.path):
            raise RepositoryError(
                "Cannot create repository at %s, location already exist"
                % self.path)

        if create:
            self._remote.create_repository(settings.SVN_COMPATIBLE_VERSION)
            if src_url:
                src_url = _sanitize_url(src_url)
                self._remote.import_remote_repository(src_url)
        else:
            self._check_path()

    @LazyProperty
    def commit_ids(self):
        head = self._remote.lookup(None)
        return [str(r) for r in xrange(1, head + 1)]

    @LazyProperty
    def branches(self):
        return self._tags_or_branches('vcs_svn_branch')

    @LazyProperty
    def branches_closed(self):
        return {}

    @LazyProperty
    def branches_all(self):
        # TODO: johbo: Implement proper branch support
        all_branches = {}
        all_branches.update(self.branches)
        all_branches.update(self.branches_closed)
        return all_branches

    @LazyProperty
    def tags(self):
        return self._tags_or_branches('vcs_svn_tag')

    def _tags_or_branches(self, config_section):
        found_items = {}

        if self.is_empty():
            return {}

        for pattern in self._patterns_from_section(config_section):
            pattern = vcspath.sanitize(pattern)
            tip = self.get_commit()
            try:
                if pattern.endswith('*'):
                    basedir = tip.get_node(vcspath.dirname(pattern))
                    directories = basedir.dirs
                else:
                    directories = (tip.get_node(pattern), )
            except NodeDoesNotExistError:
                continue
            found_items.update(
                (safe_unicode(n.path),
                 self.commit_ids[-1])
                for n in directories)

        def get_name(item):
            return item[0]

        return OrderedDict(sorted(found_items.items(), key=get_name))

    def _patterns_from_section(self, section):
        return (pattern for key, pattern in self.config.items(section))

    def get_common_ancestor(self, commit_id1, commit_id2, repo2):
        if self != repo2:
            raise ValueError(
                "Subversion does not support getting common ancestor of"
                " different repositories.")

        if int(commit_id1) < int(commit_id2):
            return commit_id1
        return commit_id2

    def compare(self, commit_id1, commit_id2, repo2, merge, pre_load=None):
        # TODO: johbo: Implement better comparison, this is a very naive
        # version which does not allow to compare branches, tags or folders
        # at all.
        if repo2 != self:
            raise ValueError(
                "Subversion does not support comparison of of different "
                "repositories.")

        if commit_id1 == commit_id2:
            return []

        commit_idx1 = self._get_commit_idx(commit_id1)
        commit_idx2 = self._get_commit_idx(commit_id2)

        commits = [
            self.get_commit(commit_idx=idx)
            for idx in range(commit_idx1 + 1, commit_idx2 + 1)]

        return commits

    def _get_commit_idx(self, commit_id):
        try:
            svn_rev = int(commit_id)
        except:
            # TODO: johbo: this might be only one case, HEAD, check this
            svn_rev = self._remote.lookup(commit_id)
        commit_idx = svn_rev - 1
        if commit_idx >= len(self.commit_ids):
            raise CommitDoesNotExistError(
                "Commit at index %s does not exist." % (commit_idx, ))
        return commit_idx

    @staticmethod
    def check_url(url, config):
        """
        Check if `url` is a valid source to import a Subversion repository.
        """
        # convert to URL if it's a local directory
        if os.path.isdir(url):
            url = 'file://' + urllib.pathname2url(url)
        return connection.Svn.check_url(url, config.serialize())

    @staticmethod
    def is_valid_repository(path):
        try:
            SubversionRepository(path)
            return True
        except VCSError:
            pass
        return False

    def _check_path(self):
        if not os.path.exists(self.path):
            raise VCSError('Path "%s" does not exist!' % (self.path, ))
        if not self._remote.is_path_valid_repository(self.path):
            raise VCSError(
                'Path "%s" does not contain a Subversion repository' %
                (self.path, ))

    @LazyProperty
    def last_change(self):
        """
        Returns last change made on this repository as
        `datetime.datetime` object.
        """
        # Subversion always has a first commit which has id "0" and contains
        # what we are looking for.
        last_id = len(self.commit_ids)
        properties = self._remote.revision_properties(last_id)
        return _date_from_svn_properties(properties)

    @LazyProperty
    def in_memory_commit(self):
        return SubversionInMemoryCommit(self)

    def get_hook_location(self):
        """
        returns absolute path to location where hooks are stored
        """
        return os.path.join(self.path, 'hooks')

    def get_commit(self, commit_id=None, commit_idx=None, pre_load=None):
        if self.is_empty():
            raise EmptyRepositoryError("There are no commits yet")
        if commit_id is not None:
            self._validate_commit_id(commit_id)
        elif commit_idx is not None:
            self._validate_commit_idx(commit_idx)
            try:
                commit_id = self.commit_ids[commit_idx]
            except IndexError:
                raise CommitDoesNotExistError

        commit_id = self._sanitize_commit_id(commit_id)
        commit = SubversionCommit(repository=self, commit_id=commit_id)
        return commit

    def get_commits(
            self, start_id=None, end_id=None, start_date=None, end_date=None,
            branch_name=None, pre_load=None):
        if self.is_empty():
            raise EmptyRepositoryError("There are no commit_ids yet")
        self._validate_branch_name(branch_name)

        if start_id is not None:
            self._validate_commit_id(start_id)
        if end_id is not None:
            self._validate_commit_id(end_id)

        start_raw_id = self._sanitize_commit_id(start_id)
        start_pos = self.commit_ids.index(start_raw_id) if start_id else None
        end_raw_id = self._sanitize_commit_id(end_id)
        end_pos = max(0, self.commit_ids.index(end_raw_id)) if end_id else None

        if None not in [start_id, end_id] and start_pos > end_pos:
            raise RepositoryError(
                "Start commit '%s' cannot be after end commit '%s'" %
                (start_id, end_id))
        if end_pos is not None:
            end_pos += 1

        # Date based filtering
        if start_date or end_date:
            start_raw_id, end_raw_id = self._remote.lookup_interval(
                date_astimestamp(start_date) if start_date else None,
                date_astimestamp(end_date) if end_date else None)
            start_pos = start_raw_id - 1
            end_pos = end_raw_id

        commit_ids = self.commit_ids

        # TODO: johbo: Reconsider impact of DEFAULT_BRANCH_NAME here
        if branch_name not in [None, self.DEFAULT_BRANCH_NAME]:
            svn_rev = long(self.commit_ids[-1])
            commit_ids = self._remote.node_history(
                path=branch_name, revision=svn_rev, limit=None)
            commit_ids = [str(i) for i in reversed(commit_ids)]

        if start_pos or end_pos:
            commit_ids = commit_ids[start_pos:end_pos]
        return base.CollectionGenerator(self, commit_ids, pre_load=pre_load)

    def _sanitize_commit_id(self, commit_id):
        if commit_id and commit_id.isdigit():
            if int(commit_id) <= len(self.commit_ids):
                return commit_id
            else:
                raise CommitDoesNotExistError(
                    "Commit %s does not exist." % (commit_id, ))
        if commit_id not in [
                None, 'HEAD', 'tip', self.DEFAULT_BRANCH_NAME]:
            raise CommitDoesNotExistError(
                "Commit id %s not understood." % (commit_id, ))
        svn_rev = self._remote.lookup('HEAD')
        return str(svn_rev)

    def get_diff(
            self, commit1, commit2, path=None, ignore_whitespace=False,
            context=3, path1=None):
        self._validate_diff_commits(commit1, commit2)
        svn_rev1 = long(commit1.raw_id)
        svn_rev2 = long(commit2.raw_id)
        diff = self._remote.diff(
            svn_rev1, svn_rev2, path1=path1, path2=path,
            ignore_whitespace=ignore_whitespace, context=context)
        return SubversionDiff(diff)


def _sanitize_url(url):
    if '://' not in url:
        url = 'file://' + urllib.pathname2url(url)
    return url
