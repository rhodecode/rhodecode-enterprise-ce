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
HG commit module
"""

import os

from zope.cachedescriptors.property import Lazy as LazyProperty

from rhodecode.lib.datelib import utcdate_fromtimestamp
from rhodecode.lib.utils import safe_str, safe_unicode
from rhodecode.lib.vcs import path as vcspath
from rhodecode.lib.vcs.backends import base
from rhodecode.lib.vcs.backends.hg.diff import MercurialDiff
from rhodecode.lib.vcs.exceptions import CommitError
from rhodecode.lib.vcs.nodes import (
    AddedFileNodesGenerator, ChangedFileNodesGenerator, DirNode, FileNode,
    NodeKind, RemovedFileNodesGenerator, RootNode, SubModuleNode,
    LargeFileNode, LARGEFILE_PREFIX)
from rhodecode.lib.vcs.utils.paths import get_dirs_for_path


class MercurialCommit(base.BaseCommit):
    """
    Represents state of the repository at the single commit.
    """

    _filter_pre_load = [
        # git specific property not supported here
        "_commit",
    ]

    def __init__(self, repository, raw_id, idx, pre_load=None):
        raw_id = safe_str(raw_id)

        self.repository = repository
        self._remote = repository._remote

        self.raw_id = raw_id
        self.idx = repository._sanitize_commit_idx(idx)

        self._set_bulk_properties(pre_load)

        # caches
        self.nodes = {}

    def _set_bulk_properties(self, pre_load):
        if not pre_load:
            return
        pre_load = [entry for entry in pre_load
                    if entry not in self._filter_pre_load]
        if not pre_load:
            return

        result = self._remote.bulk_request(self.idx, pre_load)
        for attr, value in result.items():
            if attr in ["author", "branch", "message"]:
                value = safe_unicode(value)
            elif attr == "affected_files":
                value = map(safe_unicode, value)
            elif attr == "date":
                value = utcdate_fromtimestamp(*value)
            elif attr in ["children", "parents"]:
                value = self._make_commits(value)
            self.__dict__[attr] = value

    @LazyProperty
    def tags(self):
        tags = [name for name, commit_id in self.repository.tags.iteritems()
                if commit_id == self.raw_id]
        return tags

    @LazyProperty
    def branch(self):
        return safe_unicode(self._remote.ctx_branch(self.idx))

    @LazyProperty
    def bookmarks(self):
        bookmarks = [
            name for name, commit_id in self.repository.bookmarks.iteritems()
            if commit_id == self.raw_id]
        return bookmarks

    @LazyProperty
    def message(self):
        return safe_unicode(self._remote.ctx_description(self.idx))

    @LazyProperty
    def committer(self):
        return safe_unicode(self.author)

    @LazyProperty
    def author(self):
        return safe_unicode(self._remote.ctx_user(self.idx))

    @LazyProperty
    def date(self):
        return utcdate_fromtimestamp(*self._remote.ctx_date(self.idx))

    @LazyProperty
    def status(self):
        """
        Returns modified, added, removed, deleted files for current commit
        """
        return self._remote.ctx_status(self.idx)

    @LazyProperty
    def _file_paths(self):
        return self._remote.ctx_list(self.idx)

    @LazyProperty
    def _dir_paths(self):
        p = list(set(get_dirs_for_path(*self._file_paths)))
        p.insert(0, '')
        return p

    @LazyProperty
    def _paths(self):
        return self._dir_paths + self._file_paths

    @LazyProperty
    def id(self):
        if self.last:
            return u'tip'
        return self.short_id

    @LazyProperty
    def short_id(self):
        return self.raw_id[:12]

    def _make_commits(self, indexes):
        return [self.repository.get_commit(commit_idx=idx)
                for idx in indexes if idx >= 0]

    @LazyProperty
    def parents(self):
        """
        Returns list of parent commits.
        """
        parents = self._remote.ctx_parents(self.idx)
        return self._make_commits(parents)

    @LazyProperty
    def children(self):
        """
        Returns list of child commits.
        """
        children = self._remote.ctx_children(self.idx)
        return self._make_commits(children)

    def diff(self, ignore_whitespace=True, context=3):
        result = self._remote.ctx_diff(
            self.idx,
            git=True, ignore_whitespace=ignore_whitespace, context=context)
        diff = ''.join(result)
        return MercurialDiff(diff)

    def _fix_path(self, path):
        """
        Mercurial keeps filenodes as str so we need to encode from unicode
        to str.
        """
        return safe_str(super(MercurialCommit, self)._fix_path(path))

    def _get_kind(self, path):
        path = self._fix_path(path)
        if path in self._file_paths:
            return NodeKind.FILE
        elif path in self._dir_paths:
            return NodeKind.DIR
        else:
            raise CommitError(
                "Node does not exist at the given path '%s'" % (path, ))

    def _get_filectx(self, path):
        path = self._fix_path(path)
        if self._get_kind(path) != NodeKind.FILE:
            raise CommitError(
                "File does not exist for idx %s at '%s'" % (self.raw_id, path))
        return path

    def get_file_mode(self, path):
        """
        Returns stat mode of the file at the given ``path``.
        """
        path = self._get_filectx(path)
        if 'x' in self._remote.fctx_flags(self.idx, path):
            return base.FILEMODE_EXECUTABLE
        else:
            return base.FILEMODE_DEFAULT

    def is_link(self, path):
        path = self._get_filectx(path)
        return 'l' in self._remote.fctx_flags(self.idx, path)

    def get_file_content(self, path):
        """
        Returns content of the file at given ``path``.
        """
        path = self._get_filectx(path)
        return self._remote.fctx_data(self.idx, path)

    def get_file_size(self, path):
        """
        Returns size of the file at given ``path``.
        """
        path = self._get_filectx(path)
        return self._remote.fctx_size(self.idx, path)

    def get_file_history(self, path, limit=None, pre_load=None):
        """
        Returns history of file as reversed list of `MercurialCommit` objects
        for which file at given ``path`` has been modified.
        """
        path = self._get_filectx(path)
        hist = self._remote.file_history(self.idx, path, limit)
        return [
            self.repository.get_commit(commit_id=commit_id, pre_load=pre_load)
            for commit_id in hist]

    def get_file_annotate(self, path, pre_load=None):
        """
        Returns a generator of four element tuples with
            lineno, commit_id, commit lazy loader and line
        """
        result = self._remote.fctx_annotate(self.idx, path)

        for ln_no, commit_id, content in result:
            yield (
                ln_no, commit_id,
                lambda: self.repository.get_commit(commit_id=commit_id,
                                                   pre_load=pre_load),
                content)

    def get_nodes(self, path):
        """
        Returns combined ``DirNode`` and ``FileNode`` objects list representing
        state of commit at the given ``path``. If node at the given ``path``
        is not instance of ``DirNode``, CommitError would be raised.
        """

        if self._get_kind(path) != NodeKind.DIR:
            raise CommitError(
                "Directory does not exist for idx %s at '%s'" %
                (self.idx, path))
        path = self._fix_path(path)

        filenodes = [
            FileNode(f, commit=self) for f in self._file_paths
            if os.path.dirname(f) == path]
        # TODO: johbo: Check if this can be done in a more obvious way
        dirs = path == '' and '' or [
            d for d in self._dir_paths
            if d and vcspath.dirname(d) == path]
        dirnodes = [
            DirNode(d, commit=self) for d in dirs
            if os.path.dirname(d) == path]

        alias = self.repository.alias
        for k, vals in self._submodules.iteritems():
            loc = vals[0]
            commit = vals[1]
            dirnodes.append(
                SubModuleNode(k, url=loc, commit=commit, alias=alias))
        nodes = dirnodes + filenodes
        # cache nodes
        for node in nodes:
            self.nodes[node.path] = node
        nodes.sort()

        return nodes

    def get_node(self, path):
        """
        Returns `Node` object from the given `path`. If there is no node at
        the given `path`, `NodeDoesNotExistError` would be raised.
        """
        path = self._fix_path(path)

        if path not in self.nodes:
            if path in self._file_paths:
                node = FileNode(path, commit=self)
            elif path in self._dir_paths:
                if path == '':
                    node = RootNode(commit=self)
                else:
                    node = DirNode(path, commit=self)
            else:
                raise self.no_node_at_path(path)

            # cache node
            self.nodes[path] = node
        return self.nodes[path]

    def get_largefile_node(self, path):
        path = os.path.join(LARGEFILE_PREFIX, path)

        if self._remote.is_large_file(path):
            # content of that file regular FileNode is the hash of largefile
            file_id = self.get_file_content(path).strip()
            if self._remote.in_store(file_id):
                path = self._remote.store_path(file_id)
                return LargeFileNode(path, commit=self)
            elif self._remote.in_user_cache(file_id):
                path = self._remote.store_path(file_id)
                self._remote.link(file_id, path)
                return LargeFileNode(path, commit=self)

    @LazyProperty
    def _submodules(self):
        """
        Returns a dictionary with submodule information from substate file
        of hg repository.
        """
        return self._remote.ctx_substate(self.idx)

    @LazyProperty
    def affected_files(self):
        """
        Gets a fast accessible file changes for given commit
        """
        return self._remote.ctx_files(self.idx)

    @property
    def added(self):
        """
        Returns list of added ``FileNode`` objects.
        """
        return AddedFileNodesGenerator([n for n in self.status[1]], self)

    @property
    def changed(self):
        """
        Returns list of modified ``FileNode`` objects.
        """
        return ChangedFileNodesGenerator([n for n in self.status[0]], self)

    @property
    def removed(self):
        """
        Returns list of removed ``FileNode`` objects.
        """
        return RemovedFileNodesGenerator([n for n in self.status[2]], self)
