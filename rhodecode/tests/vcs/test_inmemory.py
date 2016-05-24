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

"""
Tests so called "in memory commits" commit API of vcs.
"""
import datetime

import pytest

from rhodecode.lib.utils2 import safe_unicode
from rhodecode.lib.vcs.exceptions import (
    EmptyRepositoryError, NodeAlreadyAddedError, NodeAlreadyExistsError,
    NodeAlreadyRemovedError, NodeAlreadyChangedError, NodeDoesNotExistError,
    NodeNotChangedError)
from rhodecode.lib.vcs.nodes import DirNode, FileNode
from rhodecode.tests.vcs.base import BackendTestMixin


@pytest.fixture
def nodes():
    nodes = [
        FileNode('foobar', content='Foo & bar'),
        FileNode('foobar2', content='Foo & bar, doubled!'),
        FileNode('foo bar with spaces', content=''),
        FileNode('foo/bar/baz', content='Inside'),
        FileNode(
            'foo/bar/file.bin',
            content=(
                '\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1\x00\x00\x00\x00\x00\x00'
                '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00;\x00\x03\x00\xfe'
                '\xff\t\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                '\x01\x00\x00\x00\x1a\x00\x00\x00\x00\x00\x00\x00\x00\x10\x00'
                '\x00\x18\x00\x00\x00\x01\x00\x00\x00\xfe\xff\xff\xff\x00\x00'
                '\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff'
                '\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
            )
        ),
    ]
    return nodes


class TestInMemoryCommit(BackendTestMixin):
    """
    This is a backend independent test case class which should be created
    with ``type`` method.

    It is required to set following attributes at subclass:

    - ``backend_alias``: alias of used backend (see ``vcs.BACKENDS``)
    """

    @classmethod
    def _get_commits(cls):
        return []

    def test_add(self, nodes):
        for node in nodes:
            self.imc.add(node)

        self.commit()
        self.assert_succesful_commit(nodes)

    @pytest.mark.skip_backends(
        'svn', reason="Svn does not support commits on branches.")
    def test_add_on_branch(self, nodes):
        for node in nodes:
            self.imc.add(node)
        self.commit(branch=u'stable')
        self.assert_succesful_commit(nodes)

    def test_add_in_bulk(self, nodes):
        self.imc.add(*nodes)

        self.commit()
        self.assert_succesful_commit(nodes)

    def test_add_non_ascii_files(self):
        nodes = [
            FileNode('żółwik/zwierzątko_utf8_str', content='ćććć'),
            FileNode(u'żółwik/zwierzątko_unicode', content=u'ćććć'),
        ]

        for node in nodes:
            self.imc.add(node)

        self.commit()
        self.assert_succesful_commit(nodes)

    def commit(self, branch=None):
        self.old_commit_count = len(self.repo.commit_ids)
        self.commit_message = u'Test commit with unicode: żółwik'
        self.commit_author = unicode(self.__class__)
        self.commit = self.imc.commit(
            message=self.commit_message, author=self.commit_author,
            branch=branch)

    def test_add_actually_adds_all_nodes_at_second_commit_too(self):
        to_add = [
            FileNode('foo/bar/image.png', content='\0'),
            FileNode('foo/README.txt', content='readme!'),
        ]
        self.imc.add(*to_add)
        commit = self.imc.commit(u'Initial', u'joe.doe@example.com')
        assert isinstance(commit.get_node('foo'), DirNode)
        assert isinstance(commit.get_node('foo/bar'), DirNode)
        self.assert_nodes_in_commit(commit, to_add)

        # commit some more files again
        to_add = [
            FileNode('foo/bar/foobaz/bar', content='foo'),
            FileNode('foo/bar/another/bar', content='foo'),
            FileNode('foo/baz.txt', content='foo'),
            FileNode('foobar/foobaz/file', content='foo'),
            FileNode('foobar/barbaz', content='foo'),
        ]
        self.imc.add(*to_add)
        commit = self.imc.commit(u'Another', u'joe.doe@example.com')
        self.assert_nodes_in_commit(commit, to_add)

    def test_add_raise_already_added(self):
        node = FileNode('foobar', content='baz')
        self.imc.add(node)
        with pytest.raises(NodeAlreadyAddedError):
            self.imc.add(node)

    def test_check_integrity_raise_already_exist(self):
        node = FileNode('foobar', content='baz')
        self.imc.add(node)
        self.imc.commit(message=u'Added foobar', author=unicode(self))
        self.imc.add(node)
        with pytest.raises(NodeAlreadyExistsError):
            self.imc.commit(message='new message', author=str(self))

    def test_change(self):
        self.imc.add(FileNode('foo/bar/baz', content='foo'))
        self.imc.add(FileNode('foo/fbar', content='foobar'))
        tip = self.imc.commit(u'Initial', u'joe.doe@example.com')

        # Change node's content
        node = FileNode('foo/bar/baz', content='My **changed** content')
        self.imc.change(node)
        self.imc.commit(u'Changed %s' % node.path, u'joe.doe@example.com')

        newtip = self.repo.get_commit()
        assert tip != newtip
        assert tip.id != newtip.id
        self.assert_nodes_in_commit(newtip, (node,))

    def test_change_non_ascii(self):
        to_add = [
            FileNode('żółwik/zwierzątko', content='ćććć'),
            FileNode(u'żółwik/zwierzątko_uni', content=u'ćććć'),
        ]
        for node in to_add:
            self.imc.add(node)

        tip = self.imc.commit(u'Initial', u'joe.doe@example.com')

        # Change node's content
        node = FileNode('żółwik/zwierzątko', content='My **changed** content')
        self.imc.change(node)
        self.imc.commit(u'Changed %s' % safe_unicode(node.path),
                        u'joe.doe@example.com')

        node_uni = FileNode(
            u'żółwik/zwierzątko_uni', content=u'My **changed** content')
        self.imc.change(node_uni)
        self.imc.commit(u'Changed %s' % safe_unicode(node_uni.path),
                        u'joe.doe@example.com')

        newtip = self.repo.get_commit()
        assert tip != newtip
        assert tip.id != newtip.id

        self.assert_nodes_in_commit(newtip, (node, node_uni))

    def test_change_raise_empty_repository(self):
        node = FileNode('foobar')
        with pytest.raises(EmptyRepositoryError):
            self.imc.change(node)

    def test_check_integrity_change_raise_node_does_not_exist(self):
        node = FileNode('foobar', content='baz')
        self.imc.add(node)
        self.imc.commit(message=u'Added foobar', author=unicode(self))
        node = FileNode('not-foobar', content='')
        self.imc.change(node)
        with pytest.raises(NodeDoesNotExistError):
            self.imc.commit(
                message='Changed not existing node',
                author=str(self))

    def test_change_raise_node_already_changed(self):
        node = FileNode('foobar', content='baz')
        self.imc.add(node)
        self.imc.commit(message=u'Added foobar', author=unicode(self))
        node = FileNode('foobar', content='more baz')
        self.imc.change(node)
        with pytest.raises(NodeAlreadyChangedError):
            self.imc.change(node)

    def test_check_integrity_change_raise_node_not_changed(self, nodes):
        self.test_add(nodes)  # Performs first commit

        node = FileNode(nodes[0].path, content=nodes[0].content)
        self.imc.change(node)
        with pytest.raises(NodeNotChangedError):
            self.imc.commit(
                message=u'Trying to mark node as changed without touching it',
                author=unicode(self))

    def test_change_raise_node_already_removed(self):
        node = FileNode('foobar', content='baz')
        self.imc.add(node)
        self.imc.commit(message=u'Added foobar', author=unicode(self))
        self.imc.remove(FileNode('foobar'))
        with pytest.raises(NodeAlreadyRemovedError):
            self.imc.change(node)

    def test_remove(self, nodes):
        self.test_add(nodes)  # Performs first commit

        tip = self.repo.get_commit()
        node = nodes[0]
        assert node.content == tip.get_node(node.path).content
        self.imc.remove(node)
        self.imc.commit(
            message=u'Removed %s' % node.path, author=unicode(self))

        newtip = self.repo.get_commit()
        assert tip != newtip
        assert tip.id != newtip.id
        with pytest.raises(NodeDoesNotExistError):
            newtip.get_node(node.path)

    def test_remove_last_file_from_directory(self):
        node = FileNode('omg/qwe/foo/bar', content='foobar')
        self.imc.add(node)
        self.imc.commit(u'added', u'joe doe')

        self.imc.remove(node)
        tip = self.imc.commit(u'removed', u'joe doe')
        with pytest.raises(NodeDoesNotExistError):
            tip.get_node('omg/qwe/foo/bar')

    def test_remove_raise_node_does_not_exist(self, nodes):
        self.imc.remove(nodes[0])
        with pytest.raises(NodeDoesNotExistError):
            self.imc.commit(
                message='Trying to remove node at empty repository',
                author=str(self))

    def test_check_integrity_remove_raise_node_does_not_exist(self, nodes):
        self.test_add(nodes)  # Performs first commit

        node = FileNode('no-such-file')
        self.imc.remove(node)
        with pytest.raises(NodeDoesNotExistError):
            self.imc.commit(
                message=u'Trying to remove not existing node',
                author=unicode(self))

    def test_remove_raise_node_already_removed(self, nodes):
        self.test_add(nodes)  # Performs first commit

        node = FileNode(nodes[0].path)
        self.imc.remove(node)
        with pytest.raises(NodeAlreadyRemovedError):
            self.imc.remove(node)

    def test_remove_raise_node_already_changed(self, nodes):
        self.test_add(nodes)  # Performs first commit

        node = FileNode(nodes[0].path, content='Bending time')
        self.imc.change(node)
        with pytest.raises(NodeAlreadyChangedError):
            self.imc.remove(node)

    def test_reset(self):
        self.imc.add(FileNode('foo', content='bar'))
        # self.imc.change(FileNode('baz', content='new'))
        # self.imc.remove(FileNode('qwe'))
        self.imc.reset()
        assert not any((self.imc.added, self.imc.changed, self.imc.removed))

    def test_multiple_commits(self):
        N = 3  # number of commits to perform
        last = None
        for x in xrange(N):
            fname = 'file%s' % str(x).rjust(5, '0')
            content = 'foobar\n' * x
            node = FileNode(fname, content=content)
            self.imc.add(node)
            commit = self.imc.commit(u"Commit no. %s" % (x + 1), author=u'vcs')
            assert last != commit
            last = commit

        # Check commit number for same repo
        assert len(self.repo.commit_ids) == N

        # Check commit number for recreated repo
        repo = self.Backend(self.repo_path)
        assert len(repo.commit_ids) == N

    def test_date_attr(self):
        node = FileNode('foobar.txt', content='Foobared!')
        self.imc.add(node)
        date = datetime.datetime(1985, 1, 30, 1, 45)
        commit = self.imc.commit(
            u"Committed at time when I was born ;-)",
            author=u'lb', date=date)

        assert commit.date == date

    def assert_succesful_commit(self, added_nodes):
        newtip = self.repo.get_commit()
        assert self.commit == newtip
        assert self.old_commit_count + 1 == len(self.repo.commit_ids)
        assert newtip.message == self.commit_message
        assert newtip.author == self.commit_author
        assert not any((self.imc.added, self.imc.changed, self.imc.removed))
        self.assert_nodes_in_commit(newtip, added_nodes)

    def assert_nodes_in_commit(self, commit, nodes):
        for node in nodes:
            assert commit.get_node(node.path).content == node.content
