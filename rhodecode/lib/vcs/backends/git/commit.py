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
GIT commit module
"""

import re
import stat
from ConfigParser import ConfigParser
from itertools import chain
from StringIO import StringIO

from zope.cachedescriptors.property import Lazy as LazyProperty

from rhodecode.lib.datelib import date_fromtimestamp
from rhodecode.lib.utils import safe_unicode, safe_str
from rhodecode.lib.utils2 import safe_int
from rhodecode.lib.vcs.conf import settings
from rhodecode.lib.vcs.backends import base
from rhodecode.lib.vcs.exceptions import CommitError, NodeDoesNotExistError
from rhodecode.lib.vcs.nodes import (
    FileNode, DirNode, NodeKind, RootNode, SubModuleNode,
    ChangedFileNodesGenerator, AddedFileNodesGenerator,
    RemovedFileNodesGenerator)


class GitCommit(base.BaseCommit):
    """
    Represents state of the repository at single commit id.
    """
    _author_property = 'author'
    _committer_property = 'committer'
    _date_property = 'commit_time'
    _date_tz_property = 'commit_timezone'
    _message_property = 'message'
    _parents_property = 'parents'

    _filter_pre_load = [
        # done through a more complex tree walk on parents
        "affected_files",
        # based on repository cached property
        "branch",
        # done through subprocess not remote call
        "children",
        # done through a more complex tree walk on parents
        "status",
        # mercurial specific property not supported here
        "_file_paths",
    ]

    def __init__(self, repository, raw_id, idx, pre_load=None):
        self.repository = repository
        self._remote = repository._remote
        # TODO: johbo: Tweak of raw_id should not be necessary
        self.raw_id = safe_str(raw_id)
        self.idx = idx

        self._set_bulk_properties(pre_load)

        # caches
        self._stat_modes = {}  # stat info for paths
        self._paths = {}  # path processed with parse_tree
        self.nodes = {}
        self._submodules = None

    def _set_bulk_properties(self, pre_load):
        if not pre_load:
            return
        pre_load = [entry for entry in pre_load
                    if entry not in self._filter_pre_load]
        if not pre_load:
            return

        result = self._remote.bulk_request(self.raw_id, pre_load)
        for attr, value in result.items():
            if attr in ["author", "message"]:
                if value:
                    value = safe_unicode(value)
            elif attr == "date":
                value = date_fromtimestamp(*value)
            elif attr == "parents":
                value = self._make_commits(value)
            self.__dict__[attr] = value

    @LazyProperty
    def _commit(self):
        return self._remote[self.raw_id]

    @LazyProperty
    def _tree_id(self):
        return self._remote[self._commit['tree']]['id']

    @LazyProperty
    def id(self):
        return self.raw_id

    @LazyProperty
    def short_id(self):
        return self.raw_id[:12]

    @LazyProperty
    def message(self):
        return safe_unicode(
            self._remote.commit_attribute(self.id, self._message_property))

    @LazyProperty
    def committer(self):
        return safe_unicode(
            self._remote.commit_attribute(self.id, self._committer_property))

    @LazyProperty
    def author(self):
        return safe_unicode(
            self._remote.commit_attribute(self.id, self._author_property))

    @LazyProperty
    def date(self):
        unix_ts, tz = self._remote.get_object_attrs(
            self.raw_id, self._date_property, self._date_tz_property)
        return date_fromtimestamp(unix_ts, tz)

    @LazyProperty
    def status(self):
        """
        Returns modified, added, removed, deleted files for current commit
        """
        return self.changed, self.added, self.removed

    @LazyProperty
    def tags(self):
        tags = [safe_unicode(name) for name,
                commit_id in self.repository.tags.iteritems()
                if commit_id == self.raw_id]
        return tags

    @LazyProperty
    def branch(self):
        for name, commit_id in self.repository.branches.iteritems():
            if commit_id == self.raw_id:
                return safe_unicode(name)
        return None

    def _get_id_for_path(self, path):
        path = safe_str(path)
        if path in self._paths:
            return self._paths[path]

        tree_id = self._tree_id

        path = path.strip('/')
        if path == '':
            data = [tree_id, "tree"]
            self._paths[''] = data
            return data

        parts = path.split('/')
        dirs, name = parts[:-1], parts[-1]
        cur_dir = ''

        # initially extract things from root dir
        tree_items = self._remote.tree_items(tree_id)
        self._process_tree_items(tree_items, cur_dir)

        for dir in dirs:
            if cur_dir:
                cur_dir = '/'.join((cur_dir, dir))
            else:
                cur_dir = dir
            dir_id = None
            for item, stat_, id_, type_ in tree_items:
                if item == dir:
                    dir_id = id_
                    break
            if dir_id:
                if type_ != "tree":
                    raise CommitError('%s is not a directory' % cur_dir)
                # update tree
                tree_items = self._remote.tree_items(dir_id)
            else:
                raise CommitError('%s have not been found' % cur_dir)

            # cache all items from the given traversed tree
            self._process_tree_items(tree_items, cur_dir)

        if path not in self._paths:
            raise self.no_node_at_path(path)

        return self._paths[path]

    def _process_tree_items(self, items, cur_dir):
        for item, stat_, id_, type_ in items:
            if cur_dir:
                name = '/'.join((cur_dir, item))
            else:
                name = item
            self._paths[name] = [id_, type_]
            self._stat_modes[name] = stat_

    def _get_kind(self, path):
        path_id, type_ = self._get_id_for_path(path)
        if type_ == 'blob':
            return NodeKind.FILE
        elif type_ == 'tree':
            return NodeKind.DIR
        elif type == 'link':
            return NodeKind.SUBMODULE
        return None

    def _get_filectx(self, path):
        path = self._fix_path(path)
        if self._get_kind(path) != NodeKind.FILE:
            raise CommitError(
                "File does not exist for commit %s at  '%s'" %
                (self.raw_id, path))
        return path

    def _get_file_nodes(self):
        return chain(*(t[2] for t in self.walk()))

    @LazyProperty
    def parents(self):
        """
        Returns list of parent commits.
        """
        parent_ids = self._remote.commit_attribute(
            self.id, self._parents_property)
        return self._make_commits(parent_ids)

    @LazyProperty
    def children(self):
        """
        Returns list of child commits.
        """
        rev_filter = settings.GIT_REV_FILTER
        output, __ = self.repository.run_git_command(
            ['rev-list', '--children'] + rev_filter)

        child_ids = []
        pat = re.compile(r'^%s' % self.raw_id)
        for l in output.splitlines():
            if pat.match(l):
                found_ids = l.split(' ')[1:]
                child_ids.extend(found_ids)
        return self._make_commits(child_ids)

    def _make_commits(self, commit_ids):
        return [self.repository.get_commit(commit_id=commit_id)
                for commit_id in commit_ids]

    def get_file_mode(self, path):
        """
        Returns stat mode of the file at the given `path`.
        """
        path = safe_str(path)
        # ensure path is traversed
        self._get_id_for_path(path)
        return self._stat_modes[path]

    def is_link(self, path):
        return stat.S_ISLNK(self.get_file_mode(path))

    def get_file_content(self, path):
        """
        Returns content of the file at given `path`.
        """
        id_, _ = self._get_id_for_path(path)
        return self._remote.blob_as_pretty_string(id_)

    def get_file_size(self, path):
        """
        Returns size of the file at given `path`.
        """
        id_, _ = self._get_id_for_path(path)
        return self._remote.blob_raw_length(id_)

    def get_file_history(self, path, limit=None, pre_load=None):
        """
        Returns history of file as reversed list of `GitCommit` objects for
        which file at given `path` has been modified.

        TODO: This function now uses an underlying 'git' command which works
        quickly but ideally we should replace with an algorithm.
        """
        self._get_filectx(path)
        f_path = safe_str(path)

        cmd = ['log']
        if limit:
            cmd.extend(['-n', str(safe_int(limit, 0))])
        cmd.extend(['--pretty=format: %H', '-s', self.raw_id, '--', f_path])

        output, __ = self.repository.run_git_command(cmd)
        commit_ids = re.findall(r'[0-9a-fA-F]{40}', output)

        return [
            self.repository.get_commit(commit_id=commit_id, pre_load=pre_load)
            for commit_id in commit_ids]

    # TODO: unused for now potential replacement for subprocess
    def get_file_history_2(self, path, limit=None, pre_load=None):
        """
        Returns history of file as reversed list of `Commit` objects for
        which file at given `path` has been modified.
        """
        self._get_filectx(path)
        f_path = safe_str(path)

        commit_ids = self._remote.get_file_history(f_path, self.id, limit)

        return [
            self.repository.get_commit(commit_id=commit_id, pre_load=pre_load)
            for commit_id in commit_ids]

    def get_file_annotate(self, path, pre_load=None):
        """
        Returns a generator of four element tuples with
            lineno, commit_id, commit lazy loader and line

        TODO: This function now uses os underlying 'git' command which is
        generally not good. Should be replaced with algorithm iterating
        commits.
        """
        cmd = ['blame', '-l', '--root', '-r', self.raw_id, '--', path]
        # -l     ==> outputs long shas (and we need all 40 characters)
        # --root ==> doesn't put '^' character for bounderies
        # -r commit_id ==> blames for the given commit
        output, __ = self.repository.run_git_command(cmd)

        for i, blame_line in enumerate(output.split('\n')[:-1]):
            line_no = i + 1
            commit_id, line = re.split(r' ', blame_line, 1)
            yield (
                line_no, commit_id,
                lambda: self.repository.get_commit(commit_id=commit_id,
                                                   pre_load=pre_load),
                line)

    def get_nodes(self, path):
        if self._get_kind(path) != NodeKind.DIR:
            raise CommitError(
                "Directory does not exist for commit %s at "
                " '%s'" % (self.raw_id, path))
        path = self._fix_path(path)
        id_, _ = self._get_id_for_path(path)
        tree_id = self._remote[id_]['id']
        dirnodes = []
        filenodes = []
        alias = self.repository.alias
        for name, stat_, id_, type_ in self._remote.tree_items(tree_id):
            if type_ == 'link':
                url = self._get_submodule_url('/'.join((path, name)))
                dirnodes.append(SubModuleNode(
                    name, url=url, commit=id_, alias=alias))
                continue

            if path != '':
                obj_path = '/'.join((path, name))
            else:
                obj_path = name
            if obj_path not in self._stat_modes:
                self._stat_modes[obj_path] = stat_

            if type_ == 'tree':
                dirnodes.append(DirNode(obj_path, commit=self))
            elif type_ == 'blob':
                filenodes.append(FileNode(obj_path, commit=self, mode=stat_))
            else:
                raise CommitError(
                    "Requested object should be Tree or Blob, is %s", type_)

        nodes = dirnodes + filenodes
        for node in nodes:
            if node.path not in self.nodes:
                self.nodes[node.path] = node
        nodes.sort()
        return nodes

    def get_node(self, path):
        if isinstance(path, unicode):
            path = path.encode('utf-8')
        path = self._fix_path(path)
        if path not in self.nodes:
            try:
                id_, type_ = self._get_id_for_path(path)
            except CommitError:
                raise NodeDoesNotExistError(
                    "Cannot find one of parents' directories for a given "
                    "path: %s" % path)

            if type_ == 'link':
                url = self._get_submodule_url(path)
                node = SubModuleNode(path, url=url, commit=id_,
                                     alias=self.repository.alias)
            elif type_ == 'tree':
                if path == '':
                    node = RootNode(commit=self)
                else:
                    node = DirNode(path, commit=self)
            elif type_ == 'blob':
                node = FileNode(path, commit=self)
            else:
                raise self.no_node_at_path(path)

            # cache node
            self.nodes[path] = node
        return self.nodes[path]

    @LazyProperty
    def affected_files(self):
        """
        Gets a fast accessible file changes for given commit
        """
        added, modified, deleted = self._changes_cache
        return list(added.union(modified).union(deleted))

    @LazyProperty
    def _changes_cache(self):
        added = set()
        modified = set()
        deleted = set()
        _r = self._remote

        parents = self.parents
        if not self.parents:
            parents = [base.EmptyCommit()]
        for parent in parents:
            if isinstance(parent, base.EmptyCommit):
                oid = None
            else:
                oid = parent.raw_id
            changes = _r.tree_changes(oid, self.raw_id)
            for (oldpath, newpath), (_, _), (_, _) in changes:
                if newpath and oldpath:
                    modified.add(newpath)
                elif newpath and not oldpath:
                    added.add(newpath)
                elif not newpath and oldpath:
                    deleted.add(oldpath)
        return added, modified, deleted

    def _get_paths_for_status(self, status):
        """
        Returns sorted list of paths for given ``status``.

        :param status: one of: *added*, *modified* or *deleted*
        """
        added, modified, deleted = self._changes_cache
        return sorted({
            'added': list(added),
            'modified': list(modified),
            'deleted': list(deleted)}[status]
        )

    @LazyProperty
    def added(self):
        """
        Returns list of added ``FileNode`` objects.
        """
        if not self.parents:
            return list(self._get_file_nodes())
        return AddedFileNodesGenerator(
            [n for n in self._get_paths_for_status('added')], self)

    @LazyProperty
    def changed(self):
        """
        Returns list of modified ``FileNode`` objects.
        """
        if not self.parents:
            return []
        return ChangedFileNodesGenerator(
            [n for n in self._get_paths_for_status('modified')], self)

    @LazyProperty
    def removed(self):
        """
        Returns list of removed ``FileNode`` objects.
        """
        if not self.parents:
            return []
        return RemovedFileNodesGenerator(
            [n for n in self._get_paths_for_status('deleted')], self)

    def _get_submodule_url(self, submodule_path):
        git_modules_path = '.gitmodules'

        if self._submodules is None:
            self._submodules = {}

            try:
                submodules_node = self.get_node(git_modules_path)
            except NodeDoesNotExistError:
                return None

            content = submodules_node.content

            # ConfigParser fails if there are whitespaces
            content = '\n'.join(l.strip() for l in content.split('\n'))

            parser = ConfigParser()
            parser.readfp(StringIO(content))

            for section in parser.sections():
                path = parser.get(section, 'path')
                url = parser.get(section, 'url')
                if path and url:
                    self._submodules[path.strip('/')] = url

        return self._submodules.get(submodule_path.strip('/'))
