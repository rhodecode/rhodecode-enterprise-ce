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
SVN commit module
"""


import dateutil.parser
from zope.cachedescriptors.property import Lazy as LazyProperty

from rhodecode.lib.utils import safe_str, safe_unicode
from rhodecode.lib.vcs import nodes, path as vcspath
from rhodecode.lib.vcs.backends import base
from rhodecode.lib.vcs.exceptions import CommitError, NodeDoesNotExistError


_SVN_PROP_TRUE = '*'


class SubversionCommit(base.BaseCommit):
    """
    Subversion specific implementation of commits

    .. attribute:: branch

       The Subversion backend does not support to assign branches to
       specific commits. This attribute has always the value `None`.

    """

    def __init__(self, repository, commit_id):
        self.repository = repository
        self.idx = self.repository._get_commit_idx(commit_id)
        self._svn_rev = self.idx + 1
        self._remote = repository._remote
        # TODO: handling of raw_id should be a method on repository itself,
        # which knows how to translate commit index and commit id
        self.raw_id = commit_id
        self.short_id = commit_id
        self.id = 'r%s' % (commit_id, )

        # TODO: Implement the following placeholder attributes
        self.nodes = {}
        self.tags = []

    @property
    def author(self):
        return safe_unicode(self._properties.get('svn:author'))

    @property
    def date(self):
        return _date_from_svn_properties(self._properties)

    @property
    def message(self):
        return safe_unicode(self._properties.get('svn:log'))

    @LazyProperty
    def _properties(self):
        return self._remote.revision_properties(self._svn_rev)

    @LazyProperty
    def parents(self):
        parent_idx = self.idx - 1
        if parent_idx >= 0:
            parent = self.repository.get_commit(commit_idx=parent_idx)
            return [parent]
        return []

    @LazyProperty
    def children(self):
        child_idx = self.idx + 1
        if child_idx < len(self.repository.commit_ids):
            child = self.repository.get_commit(commit_idx=child_idx)
            return [child]
        return []

    def get_file_mode(self, path):
        # Note: Subversion flags files which are executable with a special
        # property `svn:executable` which is set to the value ``"*"``.
        if self._get_file_property(path, 'svn:executable') == _SVN_PROP_TRUE:
            return base.FILEMODE_EXECUTABLE
        else:
            return base.FILEMODE_DEFAULT

    def is_link(self, path):
        # Note: Subversion has a flag for special files, the content of the
        # file contains the type of that file.
        if self._get_file_property(path, 'svn:special') == _SVN_PROP_TRUE:
            return self.get_file_content(path).startswith('link')
        return False

    def _get_file_property(self, path, name):
        file_properties = self._remote.node_properties(
            safe_str(path), self._svn_rev)
        return file_properties.get(name)

    def get_file_content(self, path):
        path = self._fix_path(path)
        return self._remote.get_file_content(safe_str(path), self._svn_rev)

    def get_file_size(self, path):
        path = self._fix_path(path)
        return self._remote.get_file_size(safe_str(path), self._svn_rev)

    def get_file_history(self, path, limit=None, pre_load=None):
        path = safe_str(self._fix_path(path))
        history = self._remote.node_history(path, self._svn_rev, limit)
        return [
            self.repository.get_commit(commit_id=str(svn_rev))
            for svn_rev in history]

    def get_file_annotate(self, path, pre_load=None):
        result = self._remote.file_annotate(safe_str(path), self._svn_rev)

        for zero_based_line_no, svn_rev, content in result:
            commit_id = str(svn_rev)
            line_no = zero_based_line_no + 1
            yield (
                line_no,
                commit_id,
                lambda: self.repository.get_commit(commit_id=commit_id),
                content)

    def get_node(self, path):
        path = self._fix_path(path)
        if path not in self.nodes:

            if path == '':
                node = nodes.RootNode(commit=self)
            else:
                node_type = self._remote.get_node_type(
                    safe_str(path), self._svn_rev)
                if node_type == 'dir':
                    node = nodes.DirNode(path, commit=self)
                elif node_type == 'file':
                    node = nodes.FileNode(path, commit=self)
                else:
                    raise NodeDoesNotExistError(self.no_node_at_path(path))

            self.nodes[path] = node
        return self.nodes[path]

    def get_nodes(self, path):
        if self._get_kind(path) != nodes.NodeKind.DIR:
            raise CommitError(
                "Directory does not exist for commit %s at "
                " '%s'" % (self.raw_id, path))
        path = self._fix_path(path)

        path_nodes = []
        for name, kind in self._remote.get_nodes(
                safe_str(path), revision=self._svn_rev):
            node_path = vcspath.join(path, name)
            if kind == 'dir':
                node = nodes.DirNode(node_path, commit=self)
            elif kind == 'file':
                node = nodes.FileNode(node_path, commit=self)
            else:
                raise ValueError("Node kind %s not supported." % (kind, ))
            self.nodes[node_path] = node
            path_nodes.append(node)

        return path_nodes

    def _get_kind(self, path):
        path = self._fix_path(path)
        kind = self._remote.get_node_type(path, self._svn_rev)
        if kind == 'file':
            return nodes.NodeKind.FILE
        elif kind == 'dir':
            return nodes.NodeKind.DIR
        else:
            raise CommitError(
                "Node does not exist at the given path '%s'" % (path, ))

    @LazyProperty
    def _changes_cache(self):
        return self._remote.revision_changes(self._svn_rev)

    @LazyProperty
    def affected_files(self):
        changed_files = set()
        for files in self._changes_cache.itervalues():
            changed_files.update(files)
        return list(changed_files)

    @property
    def added(self):
        return nodes.AddedFileNodesGenerator(
            self._changes_cache['added'], self)

    @property
    def changed(self):
        return nodes.ChangedFileNodesGenerator(
            self._changes_cache['changed'], self)

    @property
    def removed(self):
        return nodes.RemovedFileNodesGenerator(
            self._changes_cache['removed'], self)


def _date_from_svn_properties(properties):
    """
    Parses the date out of given svn properties.

    :return: :class:`datetime.datetime` instance. The object is naive.
    """
    aware_date = dateutil.parser.parse(properties.get('svn:date'))
    local_date = aware_date.astimezone(dateutil.tz.tzlocal())
    return local_date.replace(tzinfo=None)
