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
Module holding everything related to vcs nodes, with vcs2 architecture.
"""


import stat

from zope.cachedescriptors.property import Lazy as LazyProperty

from rhodecode.lib.utils import safe_unicode, safe_str
from rhodecode.lib.utils2 import md5
from rhodecode.lib.vcs import path as vcspath
from rhodecode.lib.vcs.backends.base import EmptyCommit, FILEMODE_DEFAULT
from rhodecode.lib.vcs.conf.mtypes import get_mimetypes_db
from rhodecode.lib.vcs.exceptions import NodeError, RemovedFileNodeError

LARGEFILE_PREFIX = '.hglf'


class NodeKind:
    SUBMODULE = -1
    DIR = 1
    FILE = 2
    LARGEFILE = 3


class NodeState:
    ADDED = u'added'
    CHANGED = u'changed'
    NOT_CHANGED = u'not changed'
    REMOVED = u'removed'


class NodeGeneratorBase(object):
    """
    Base class for removed added and changed filenodes, it's a lazy generator
    class that will create filenodes only on iteration or call

    The len method doesn't need to create filenodes at all
    """

    def __init__(self, current_paths, cs):
        self.cs = cs
        self.current_paths = current_paths

    def __call__(self):
        return [n for n in self]

    def __getslice__(self, i, j):
        for p in self.current_paths[i:j]:
            yield self.cs.get_node(p)

    def __len__(self):
        return len(self.current_paths)

    def __iter__(self):
        for p in self.current_paths:
            yield self.cs.get_node(p)


class AddedFileNodesGenerator(NodeGeneratorBase):
    """
    Class holding added files for current commit
    """


class ChangedFileNodesGenerator(NodeGeneratorBase):
    """
    Class holding changed files for current commit
    """


class RemovedFileNodesGenerator(NodeGeneratorBase):
    """
    Class holding removed files for current commit
    """
    def __iter__(self):
        for p in self.current_paths:
            yield RemovedFileNode(path=p)

    def __getslice__(self, i, j):
        for p in self.current_paths[i:j]:
            yield RemovedFileNode(path=p)


class Node(object):
    """
    Simplest class representing file or directory on repository.  SCM backends
    should use ``FileNode`` and ``DirNode`` subclasses rather than ``Node``
    directly.

    Node's ``path`` cannot start with slash as we operate on *relative* paths
    only. Moreover, every single node is identified by the ``path`` attribute,
    so it cannot end with slash, too. Otherwise, path could lead to mistakes.
    """

    commit = None

    def __init__(self, path, kind):
        self._validate_path(path)  # can throw exception if path is invalid
        self.path = safe_str(path.rstrip('/'))  # we store paths as str
        if path == '' and kind != NodeKind.DIR:
            raise NodeError("Only DirNode and its subclasses may be "
                            "initialized with empty path")
        self.kind = kind

        if self.is_root() and not self.is_dir():
            raise NodeError("Root node cannot be FILE kind")

    def _validate_path(self, path):
        if path.startswith('/'):
            raise NodeError(
                "Cannot initialize Node objects with slash at "
                "the beginning as only relative paths are supported. "
                "Got %s" % (path,))

    @LazyProperty
    def parent(self):
        parent_path = self.get_parent_path()
        if parent_path:
            if self.commit:
                return self.commit.get_node(parent_path)
            return DirNode(parent_path)
        return None

    @LazyProperty
    def unicode_path(self):
        return safe_unicode(self.path)

    @LazyProperty
    def dir_path(self):
        """
        Returns name of the directory from full path of this vcs node. Empty
        string is returned if there's no directory in the path
        """
        _parts = self.path.rstrip('/').rsplit('/', 1)
        if len(_parts) == 2:
            return safe_unicode(_parts[0])
        return u''

    @LazyProperty
    def name(self):
        """
        Returns name of the node so if its path
        then only last part is returned.
        """
        return safe_unicode(self.path.rstrip('/').split('/')[-1])

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, kind):
        if hasattr(self, '_kind'):
            raise NodeError("Cannot change node's kind")
        else:
            self._kind = kind
            # Post setter check (path's trailing slash)
            if self.path.endswith('/'):
                raise NodeError("Node's path cannot end with slash")

    def __cmp__(self, other):
        """
        Comparator using name of the node, needed for quick list sorting.
        """
        kind_cmp = cmp(self.kind, other.kind)
        if kind_cmp:
            return kind_cmp
        return cmp(self.name, other.name)

    def __eq__(self, other):
        for attr in ['name', 'path', 'kind']:
            if getattr(self, attr) != getattr(other, attr):
                return False
        if self.is_file():
            if self.content != other.content:
                return False
        else:
            # For DirNode's check without entering each dir
            self_nodes_paths = list(sorted(n.path for n in self.nodes))
            other_nodes_paths = list(sorted(n.path for n in self.nodes))
            if self_nodes_paths != other_nodes_paths:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.path)

    def __str__(self):
        return self.__repr__()

    def __unicode__(self):
        return self.name

    def get_parent_path(self):
        """
        Returns node's parent path or empty string if node is root.
        """
        if self.is_root():
            return ''
        return vcspath.dirname(self.path.rstrip('/')) + '/'

    def is_file(self):
        """
        Returns ``True`` if node's kind is ``NodeKind.FILE``, ``False``
        otherwise.
        """
        return self.kind == NodeKind.FILE

    def is_dir(self):
        """
        Returns ``True`` if node's kind is ``NodeKind.DIR``, ``False``
        otherwise.
        """
        return self.kind == NodeKind.DIR

    def is_root(self):
        """
        Returns ``True`` if node is a root node and ``False`` otherwise.
        """
        return self.kind == NodeKind.DIR and self.path == ''

    def is_submodule(self):
        """
        Returns ``True`` if node's kind is ``NodeKind.SUBMODULE``, ``False``
        otherwise.
        """
        return self.kind == NodeKind.SUBMODULE

    def is_largefile(self):
        """
        Returns ``True`` if node's kind is ``NodeKind.LARGEFILE``, ``False``
        otherwise
        """
        return self.kind == NodeKind.LARGEFILE

    def is_link(self):
        if self.commit:
            return self.commit.is_link(self.path)
        return False

    @LazyProperty
    def added(self):
        return self.state is NodeState.ADDED

    @LazyProperty
    def changed(self):
        return self.state is NodeState.CHANGED

    @LazyProperty
    def not_changed(self):
        return self.state is NodeState.NOT_CHANGED

    @LazyProperty
    def removed(self):
        return self.state is NodeState.REMOVED


class FileNode(Node):
    """
    Class representing file nodes.

    :attribute: path: path to the node, relative to repository's root
    :attribute: content: if given arbitrary sets content of the file
    :attribute: commit: if given, first time content is accessed, callback
    :attribute: mode: stat mode for a node. Default is `FILEMODE_DEFAULT`.
    """

    def __init__(self, path, content=None, commit=None, mode=None):
        """
        Only one of ``content`` and ``commit`` may be given. Passing both
        would raise ``NodeError`` exception.

        :param path: relative path to the node
        :param content: content may be passed to constructor
        :param commit: if given, will use it to lazily fetch content
        :param mode: ST_MODE (i.e. 0100644)
        """
        if content and commit:
            raise NodeError("Cannot use both content and commit")
        super(FileNode, self).__init__(path, kind=NodeKind.FILE)
        self.commit = commit
        self._content = content
        self._mode = mode or FILEMODE_DEFAULT

    @LazyProperty
    def mode(self):
        """
        Returns lazily mode of the FileNode. If `commit` is not set, would
        use value given at initialization or `FILEMODE_DEFAULT` (default).
        """
        if self.commit:
            mode = self.commit.get_file_mode(self.path)
        else:
            mode = self._mode
        return mode

    @LazyProperty
    def raw_bytes(self):
        """
        Returns lazily the raw bytes of the FileNode.
        """
        if self.commit:
            if self._content is None:
                self._content = self.commit.get_file_content(self.path)
            content = self._content
        else:
            content = self._content
        return content

    @LazyProperty
    def md5(self):
        """
        Returns md5 of the file node.
        """
        return md5(self.raw_bytes)

    @LazyProperty
    def content(self):
        """
        Returns lazily content of the FileNode. If possible, would try to
        decode content from UTF-8.
        """
        content = self.raw_bytes

        if self.is_binary:
            return content
        return safe_unicode(content)

    @LazyProperty
    def size(self):
        if self.commit:
            return self.commit.get_file_size(self.path)
        raise NodeError(
            "Cannot retrieve size of the file without related "
            "commit attribute")

    @LazyProperty
    def message(self):
        if self.commit:
            return self.last_commit.message
        raise NodeError(
            "Cannot retrieve message of the file without related "
            "commit attribute")

    @LazyProperty
    def last_commit(self):
        if self.commit:
            pre_load = ["author", "date", "message"]
            return self.commit.get_file_commit(self.path, pre_load=pre_load)
        raise NodeError(
            "Cannot retrieve last commit of the file without "
            "related commit attribute")

    def get_mimetype(self):
        """
        Mimetype is calculated based on the file's content. If ``_mimetype``
        attribute is available, it will be returned (backends which store
        mimetypes or can easily recognize them, should set this private
        attribute to indicate that type should *NOT* be calculated).
        """

        if hasattr(self, '_mimetype'):
            if (isinstance(self._mimetype, (tuple, list,)) and
                    len(self._mimetype) == 2):
                return self._mimetype
            else:
                raise NodeError('given _mimetype attribute must be an 2 '
                                'element list or tuple')

        db = get_mimetypes_db()
        mtype, encoding = db.guess_type(self.name)

        if mtype is None:
            if self.is_binary:
                mtype = 'application/octet-stream'
                encoding = None
            else:
                mtype = 'text/plain'
                encoding = None

                # try with pygments
                try:
                    from pygments.lexers import get_lexer_for_filename
                    mt = get_lexer_for_filename(self.name).mimetypes
                except Exception:
                    mt = None

                if mt:
                    mtype = mt[0]

        return mtype, encoding

    @LazyProperty
    def mimetype(self):
        """
        Wrapper around full mimetype info. It returns only type of fetched
        mimetype without the encoding part. use get_mimetype function to fetch
        full set of (type,encoding)
        """
        return self.get_mimetype()[0]

    @LazyProperty
    def mimetype_main(self):
        return self.mimetype.split('/')[0]

    @LazyProperty
    def lexer(self):
        """
        Returns pygment's lexer class. Would try to guess lexer taking file's
        content, name and mimetype.
        """
        from pygments import lexers
        try:
            lexer = lexers.guess_lexer_for_filename(self.name, self.content, stripnl=False)
        except lexers.ClassNotFound:
            lexer = lexers.TextLexer(stripnl=False)
        # returns first alias
        return lexer

    @LazyProperty
    def lexer_alias(self):
        """
        Returns first alias of the lexer guessed for this file.
        """
        return self.lexer.aliases[0]

    @LazyProperty
    def history(self):
        """
        Returns a list of commit for this file in which the file was changed
        """
        if self.commit is None:
            raise NodeError('Unable to get commit for this FileNode')
        return self.commit.get_file_history(self.path)

    @LazyProperty
    def annotate(self):
        """
        Returns a list of three element tuples with lineno, commit and line
        """
        if self.commit is None:
            raise NodeError('Unable to get commit for this FileNode')
        pre_load = ["author", "date", "message"]
        return self.commit.get_file_annotate(self.path, pre_load=pre_load)

    @LazyProperty
    def state(self):
        if not self.commit:
            raise NodeError(
                "Cannot check state of the node if it's not "
                "linked with commit")
        elif self.path in (node.path for node in self.commit.added):
            return NodeState.ADDED
        elif self.path in (node.path for node in self.commit.changed):
            return NodeState.CHANGED
        else:
            return NodeState.NOT_CHANGED

    @LazyProperty
    def is_binary(self):
        """
        Returns True if file has binary content.
        """
        _bin = self.raw_bytes and '\0' in self.raw_bytes
        return _bin

    @LazyProperty
    def extension(self):
        """Returns filenode extension"""
        return self.name.split('.')[-1]

    @property
    def is_executable(self):
        """
        Returns ``True`` if file has executable flag turned on.
        """
        return bool(self.mode & stat.S_IXUSR)

    def get_largefile_node(self):
        """
        Try to return a Mercurial FileNode from this node. It does internal
        checks inside largefile store, if that file exist there it will
        create special instance of LargeFileNode which can get content from
        LF store.
        """
        if self.commit and self.path.startswith(LARGEFILE_PREFIX):
            largefile_path = self.path.split(LARGEFILE_PREFIX)[-1].lstrip('/')
            return self.commit.get_largefile_node(largefile_path)

    def lines(self, count_empty=False):
        all_lines, empty_lines = 0, 0

        if not self.is_binary:
            content = self.content
            if count_empty:
                all_lines = 0
                empty_lines = 0
                for line in content.splitlines(True):
                    if line == '\n':
                        empty_lines += 1
                    all_lines += 1

                return all_lines, all_lines - empty_lines
            else:
                # fast method
                empty_lines = all_lines = content.count('\n')
                if all_lines == 0 and content:
                    # one-line without a newline
                    empty_lines = all_lines = 1

        return all_lines, empty_lines

    def __repr__(self):
        return '<%s %r @ %s>' % (self.__class__.__name__, self.path,
                                 getattr(self.commit, 'short_id', ''))


class RemovedFileNode(FileNode):
    """
    Dummy FileNode class - trying to access any public attribute except path,
    name, kind or state (or methods/attributes checking those two) would raise
    RemovedFileNodeError.
    """
    ALLOWED_ATTRIBUTES = [
        'name', 'path', 'state', 'is_root', 'is_file', 'is_dir', 'kind',
        'added', 'changed', 'not_changed', 'removed'
    ]

    def __init__(self, path):
        """
        :param path: relative path to the node
        """
        super(RemovedFileNode, self).__init__(path=path)

    def __getattribute__(self, attr):
        if attr.startswith('_') or attr in RemovedFileNode.ALLOWED_ATTRIBUTES:
            return super(RemovedFileNode, self).__getattribute__(attr)
        raise RemovedFileNodeError(
            "Cannot access attribute %s on RemovedFileNode" % attr)

    @LazyProperty
    def state(self):
        return NodeState.REMOVED


class DirNode(Node):
    """
    DirNode stores list of files and directories within this node.
    Nodes may be used standalone but within repository context they
    lazily fetch data within same repositorty's commit.
    """

    def __init__(self, path, nodes=(), commit=None):
        """
        Only one of ``nodes`` and ``commit`` may be given. Passing both
        would raise ``NodeError`` exception.

        :param path: relative path to the node
        :param nodes: content may be passed to constructor
        :param commit: if given, will use it to lazily fetch content
        """
        if nodes and commit:
            raise NodeError("Cannot use both nodes and commit")
        super(DirNode, self).__init__(path, NodeKind.DIR)
        self.commit = commit
        self._nodes = nodes

    @LazyProperty
    def content(self):
        raise NodeError(
            "%s represents a dir and has no `content` attribute" % self)

    @LazyProperty
    def nodes(self):
        if self.commit:
            nodes = self.commit.get_nodes(self.path)
        else:
            nodes = self._nodes
        self._nodes_dict = dict((node.path, node) for node in nodes)
        return sorted(nodes)

    @LazyProperty
    def files(self):
        return sorted((node for node in self.nodes if node.is_file()))

    @LazyProperty
    def dirs(self):
        return sorted((node for node in self.nodes if node.is_dir()))

    def __iter__(self):
        for node in self.nodes:
            yield node

    def get_node(self, path):
        """
        Returns node from within this particular ``DirNode``, so it is now
        allowed to fetch, i.e. node located at 'docs/api/index.rst' from node
        'docs'. In order to access deeper nodes one must fetch nodes between
        them first - this would work::

           docs = root.get_node('docs')
           docs.get_node('api').get_node('index.rst')

        :param: path - relative to the current node

        .. note::
           To access lazily (as in example above) node have to be initialized
           with related commit object - without it node is out of
           context and may know nothing about anything else than nearest
           (located at same level) nodes.
        """
        try:
            path = path.rstrip('/')
            if path == '':
                raise NodeError("Cannot retrieve node without path")
            self.nodes  # access nodes first in order to set _nodes_dict
            paths = path.split('/')
            if len(paths) == 1:
                if not self.is_root():
                    path = '/'.join((self.path, paths[0]))
                else:
                    path = paths[0]
                return self._nodes_dict[path]
            elif len(paths) > 1:
                if self.commit is None:
                    raise NodeError(
                        "Cannot access deeper nodes without commit")
                else:
                    path1, path2 = paths[0], '/'.join(paths[1:])
                    return self.get_node(path1).get_node(path2)
            else:
                raise KeyError
        except KeyError:
            raise NodeError("Node does not exist at %s" % path)

    @LazyProperty
    def state(self):
        raise NodeError("Cannot access state of DirNode")

    @LazyProperty
    def size(self):
        size = 0
        for root, dirs, files in self.commit.walk(self.path):
            for f in files:
                size += f.size

        return size

    def __repr__(self):
        return '<%s %r @ %s>' % (self.__class__.__name__, self.path,
                                 getattr(self.commit, 'short_id', ''))


class RootNode(DirNode):
    """
    DirNode being the root node of the repository.
    """

    def __init__(self, nodes=(), commit=None):
        super(RootNode, self).__init__(path='', nodes=nodes, commit=commit)

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


class SubModuleNode(Node):
    """
    represents a SubModule of Git or SubRepo of Mercurial
    """
    is_binary = False
    size = 0

    def __init__(self, name, url=None, commit=None, alias=None):
        self.path = name
        self.kind = NodeKind.SUBMODULE
        self.alias = alias

        # we have to use EmptyCommit here since this can point to svn/git/hg
        # submodules we cannot get from repository
        self.commit = EmptyCommit(str(commit), alias=alias)
        self.url = url or self._extract_submodule_url()

    def __repr__(self):
        return '<%s %r @ %s>' % (self.__class__.__name__, self.path,
                                 getattr(self.commit, 'short_id', ''))

    def _extract_submodule_url(self):
        # TODO: find a way to parse gits submodule file and extract the
        # linking URL
        return self.path

    @LazyProperty
    def name(self):
        """
        Returns name of the node so if its path
        then only last part is returned.
        """
        org = safe_unicode(self.path.rstrip('/').split('/')[-1])
        return u'%s @ %s' % (org, self.commit.short_id)


class LargeFileNode(FileNode):

    def _validate_path(self, path):
        """
        we override check since the LargeFileNode path is system absolute
        """

    def raw_bytes(self):
        if self.commit:
            with open(self.path, 'rb') as f:
                content = f.read()
        else:
            content = self._content
        return content