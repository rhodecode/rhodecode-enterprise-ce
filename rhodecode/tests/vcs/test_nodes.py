# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
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

import stat

import pytest

from rhodecode.lib.vcs.nodes import DirNode
from rhodecode.lib.vcs.nodes import FileNode
from rhodecode.lib.vcs.nodes import Node
from rhodecode.lib.vcs.nodes import NodeError
from rhodecode.lib.vcs.nodes import NodeKind
from rhodecode.tests.vcs.base import BackendTestMixin


@pytest.fixture()
def binary_filenode():
    def node_maker(filename):
        data = (
            "\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00"
            "\x10\x08\x06\x00\x00\x00\x1f??a\x00\x00\x00\x04gAMA\x00\x00\xaf?7"
            "\x05\x8a?\x00\x00\x00\x19tEXtSoftware\x00Adobe ImageReadyq?e<\x00"
            "\x00\x025IDAT8?\xa5\x93?K\x94Q\x14\x87\x9f\xf7?Q\x1bs4?\x03\x9a"
            "\xa8?B\x02\x8b$\x10[U;i\x13?6h?&h[?\"\x14j?\xa2M\x7fB\x14F\x9aQ?&"
            "\x842?\x0b\x89\"\x82??!?\x9c!\x9c2l??{N\x8bW\x9dY\xb4\t/\x1c?="
            "\x9b?}????\xa9*;9!?\x83\x91?[?\\v*?D\x04\'`EpNp\xa2X\'U?pVq\"Sw."
            "\x1e?\x08\x01D?jw????\xbc??7{|\x9b?\x89$\x01??W@\x15\x9c\x05q`Lt/"
            "\x97?\x94\xa1d?\x18~?\x18?\x18W[%\xb0?\x83??\x14\x88\x8dB?\xa6H"
            "\tL\tl\x19>/\x01`\xac\xabx?\x9cl\nx\xb0\x98\x07\x95\x88D$\"q["
            "\x19?d\x00(o\n\xa0??\x7f\xb9\xa4?\x1bF\x1f\x8e\xac\xa8?j??eUU}?.?"
            "\x9f\x8cE??x\x94??\r\xbdtoJU5\"0N\x10U?\x00??V\t\x02\x9f\x81?U?"
            "\x00\x9eM\xae2?r\x9b7\x83\x82\x8aP3????.?&\"?\xb7ZP \x0c<?O"
            "\xa5\t}\xb8?\x99\xa6?\x87?\x1di|/\xa0??0\xbe\x1fp?d&\x1a\xad"
            "\x95\x8a\x07?\t*\x10??b:?d?.\x13C\x8a?\x12\xbe\xbf\x8e?{???"
            "\x08?\x80\xa7\x13+d\x13>J?\x80\x15T\x95\x9a\x00??S\x8c\r?\xa1"
            "\x03\x07?\x96\x9b\xa7\xab=E??\xa4\xb3?\x19q??B\x91=\x8d??k?J"
            "\x0bV\"??\xf7x?\xa1\x00?\\.\x87\x87???\x02F@D\x99],??\x10#?X"
            "\xb7=\xb9\x10?Z\x1by???cI??\x1ag?\x92\xbc?T?t[\x92\x81?<_\x17~"
            "\x92\x88?H%?\x10Q\x02\x9f\n\x81qQ\x0bm?\x1bX?\xb1AK\xa6\x9e\xb9?u"
            "\xb2?1\xbe|/\x92M@\xa2!F?\xa9>\"\r<DT?>\x92\x8e?>\x9a9Qv\x127?a"
            "\xac?Y?8?:??]X???9\x80\xb7?u?\x0b#BZ\x8d=\x1d?p\x00\x00\x00\x00"
            "IEND\xaeB`\x82")
        return FileNode(filename, content=data)
    return node_maker


class TestNodeBasics:

    @pytest.mark.parametrize("path", ['/foo', '/foo/bar'])
    @pytest.mark.parametrize(
        "kind", [NodeKind.FILE, NodeKind.DIR], ids=["FILE", "DIR"])
    def test_init_wrong_paths(self, path, kind):
        """
        Cannot innitialize Node objects with path with slash at the beginning.
        """
        with pytest.raises(NodeError):
            Node(path, kind)

    @pytest.mark.parametrize("path", ['path', 'some/path'])
    @pytest.mark.parametrize(
        "kind", [NodeKind.FILE, NodeKind.DIR], ids=["FILE", "DIR"])
    def test_name(self, path, kind):
        node = Node(path, kind)
        assert node.name == 'path'

    def test_name_root(self):
        node = Node('', NodeKind.DIR)
        assert node.name == ''

    def test_root_node_cannot_be_file(self):
        with pytest.raises(NodeError):
            Node('', NodeKind.FILE)

    def test_kind_setter(self):
        node = Node('', NodeKind.DIR)
        with pytest.raises(NodeError):
            node.kind = NodeKind.FILE

    def test_compare_equal(self):
        node1 = FileNode('test', content='')
        node2 = FileNode('test', content='')
        assert node1 == node2
        assert not node1 != node2

    def test_compare_unequal(self):
        node1 = FileNode('test', content='a')
        node2 = FileNode('test', content='b')
        assert node1 != node2
        assert not node1 == node2

    @pytest.mark.parametrize("node_path, expected_parent_path", [
        ('', ''),
        ('some/path/', 'some/'),
        ('some/longer/path/', 'some/longer/'),
    ])
    def test_parent_path_new(self, node_path, expected_parent_path):
        """
        Tests if node's parent path are properly computed.
        """
        node = Node(node_path, NodeKind.DIR)
        parent_path = node.get_parent_path()
        assert (parent_path.endswith('/') or
                node.is_root() and parent_path == '')
        assert parent_path == expected_parent_path

    '''
    def _test_trailing_slash(self, path):
        if not path.endswith('/'):
            pytest.fail("Trailing slash tests needs paths to end with slash")
        for kind in NodeKind.FILE, NodeKind.DIR:
            with pytest.raises(NodeError):
                Node(path=path, kind=kind)

    def test_trailing_slash(self):
        for path in ('/', 'foo/', 'foo/bar/', 'foo/bar/biz/'):
            self._test_trailing_slash(path)
    '''

    def test_is_file(self):
        node = Node('any', NodeKind.FILE)
        assert node.is_file()

        node = FileNode('any')
        assert node.is_file()
        with pytest.raises(AttributeError):
            node.nodes

    def test_is_dir(self):
        node = Node('any_dir', NodeKind.DIR)
        assert node.is_dir()

        node = DirNode('any_dir')

        assert node.is_dir()
        with pytest.raises(NodeError):
            node.content

    def test_dir_node_iter(self):
        nodes = [
            DirNode('docs'),
            DirNode('tests'),
            FileNode('bar'),
            FileNode('foo'),
            FileNode('readme.txt'),
            FileNode('setup.py'),
        ]
        dirnode = DirNode('', nodes=nodes)
        for node in dirnode:
            assert node == dirnode.get_node(node.path)

    def test_node_state(self):
        """
        Without link to commit nodes should raise NodeError.
        """
        node = FileNode('anything')
        with pytest.raises(NodeError):
            node.state
        node = DirNode('anything')
        with pytest.raises(NodeError):
            node.state

    def test_file_node_stat(self):
        node = FileNode('foobar', 'empty... almost')
        mode = node.mode  # default should be 0100644
        assert mode & stat.S_IRUSR
        assert mode & stat.S_IWUSR
        assert mode & stat.S_IRGRP
        assert mode & stat.S_IROTH
        assert not mode & stat.S_IWGRP
        assert not mode & stat.S_IWOTH
        assert not mode & stat.S_IXUSR
        assert not mode & stat.S_IXGRP
        assert not mode & stat.S_IXOTH

    def test_file_node_is_executable(self):
        node = FileNode('foobar', 'empty... almost', mode=0100755)
        assert node.is_executable

        node = FileNode('foobar', 'empty... almost', mode=0100500)
        assert node.is_executable

        node = FileNode('foobar', 'empty... almost', mode=0100644)
        assert not node.is_executable

    def test_file_node_is_not_symlink(self):
        node = FileNode('foobar', 'empty...')
        assert not node.is_link()

    def test_mimetype(self):
        py_node = FileNode('test.py')
        tar_node = FileNode('test.tar.gz')

        ext = 'CustomExtension'

        my_node2 = FileNode('myfile2')
        my_node2._mimetype = [ext]

        my_node3 = FileNode('myfile3')
        my_node3._mimetype = [ext, ext]

        assert py_node.mimetype == 'text/x-python'
        assert py_node.get_mimetype() == ('text/x-python', None)

        assert tar_node.mimetype == 'application/x-tar'
        assert tar_node.get_mimetype() == ('application/x-tar', 'gzip')

        with pytest.raises(NodeError):
            my_node2.get_mimetype()

        assert my_node3.mimetype == ext
        assert my_node3.get_mimetype() == [ext, ext]

    def test_lines_counts(self):
        lines = [
            'line1\n',
            'line2\n',
            'line3\n',
            '\n',
            '\n',
            'line4\n',
        ]
        py_node = FileNode('test.py', ''.join(lines))

        assert (len(lines), len(lines)) == py_node.lines()
        assert (len(lines), len(lines) - 2) == py_node.lines(count_empty=True)

    def test_lines_no_newline(self):
        py_node = FileNode('test.py', 'oneline')

        assert (1, 1) == py_node.lines()
        assert (1, 1) == py_node.lines(count_empty=True)


class TestNodeContent:

    def test_if_binary(self, binary_filenode):
        filenode = binary_filenode('calendar.jpg')
        assert filenode.is_binary

    def test_binary_line_counts(self, binary_filenode):
        tar_node = binary_filenode('archive.tar.gz')
        assert (0, 0) == tar_node.lines(count_empty=True)

    def test_binary_mimetype(self, binary_filenode):
        tar_node = binary_filenode('archive.tar.gz')
        assert tar_node.mimetype == 'application/x-tar'


class TestNodesCommits(BackendTestMixin):

    def test_node_last_commit(self, generate_repo_with_commits):
        repo = generate_repo_with_commits(20)
        last_commit = repo.get_commit()

        for x in xrange(3):
            node = last_commit.get_node('file_%s.txt' % x)
            assert node.last_commit == repo[x]
