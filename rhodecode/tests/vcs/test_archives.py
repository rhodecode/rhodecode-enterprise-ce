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

import datetime
import os
import shutil
import tarfile
import tempfile
import zipfile
import StringIO

import mock
import pytest

from rhodecode.lib.vcs.backends import base
from rhodecode.lib.vcs.exceptions import ImproperArchiveTypeError, VCSError
from rhodecode.lib.vcs.nodes import FileNode
from rhodecode.tests.vcs.base import BackendTestMixin


class TestArchives(BackendTestMixin):

    @pytest.fixture(autouse=True)
    def tempfile(self, request):
        self.temp_file = tempfile.mkstemp()[1]

        @request.addfinalizer
        def cleanup():
            os.remove(self.temp_file)

    @classmethod
    def _get_commits(cls):
        start_date = datetime.datetime(2010, 1, 1, 20)
        for x in xrange(5):
            yield {
                'message': 'Commit %d' % x,
                'author': 'Joe Doe <joe.doe@example.com>',
                'date': start_date + datetime.timedelta(hours=12 * x),
                'added': [
                    FileNode(
                        '%d/file_%d.txt' % (x, x), content='Foobar %d' % x),
                ],
            }

    @pytest.mark.parametrize('compressor', ['gz', 'bz2'])
    def test_archive_tar(self, compressor):
        self.tip.archive_repo(
            self.temp_file, kind='t' + compressor, prefix='repo')
        out_dir = tempfile.mkdtemp()
        out_file = tarfile.open(self.temp_file, 'r|' + compressor)
        out_file.extractall(out_dir)
        out_file.close()

        for x in xrange(5):
            node_path = '%d/file_%d.txt' % (x, x)
            with open(os.path.join(out_dir, 'repo/' + node_path)) as f:
                file_content = f.read()
            assert file_content == self.tip.get_node(node_path).content

        shutil.rmtree(out_dir)

    def test_archive_zip(self):
        self.tip.archive_repo(self.temp_file, kind='zip', prefix='repo')
        out = zipfile.ZipFile(self.temp_file)

        for x in xrange(5):
            node_path = '%d/file_%d.txt' % (x, x)
            decompressed = StringIO.StringIO()
            decompressed.write(out.read('repo/' + node_path))
            assert decompressed.getvalue() == \
                self.tip.get_node(node_path).content
            decompressed.close()

    def test_archive_zip_with_metadata(self):
        self.tip.archive_repo(self.temp_file, kind='zip',
                              prefix='repo', write_metadata=True)

        out = zipfile.ZipFile(self.temp_file)
        metafile = out.read('.archival.txt')

        raw_id = self.tip.raw_id
        assert 'rev:%s' % raw_id in metafile

        for x in xrange(5):
            node_path = '%d/file_%d.txt' % (x, x)
            decompressed = StringIO.StringIO()
            decompressed.write(out.read('repo/' + node_path))
            assert decompressed.getvalue() == \
                self.tip.get_node(node_path).content
            decompressed.close()

    def test_archive_wrong_kind(self):
        with pytest.raises(ImproperArchiveTypeError):
            self.tip.archive_repo(self.temp_file, kind='wrong kind')


@pytest.fixture
def base_commit():
    """
    Prepare a `base.BaseCommit` just enough for `_validate_archive_prefix`.
    """
    commit = base.BaseCommit()
    commit.repository = mock.Mock()
    commit.repository.name = u'fake_repo'
    commit.short_id = 'fake_id'
    return commit


@pytest.mark.parametrize("prefix", [u"unicode-prefix", u"Ünïcödë"])
def test_validate_archive_prefix_enforces_bytes_as_prefix(prefix, base_commit):
    with pytest.raises(ValueError):
        base_commit._validate_archive_prefix(prefix)


def test_validate_archive_prefix_empty_prefix(base_commit):
    # TODO: johbo: Should raise a ValueError here.
    with pytest.raises(VCSError):
        base_commit._validate_archive_prefix('')


def test_validate_archive_prefix_with_leading_slash(base_commit):
    # TODO: johbo: Should raise a ValueError here.
    with pytest.raises(VCSError):
        base_commit._validate_archive_prefix('/any')


def test_validate_archive_prefix_falls_back_to_repository_name(base_commit):
    prefix = base_commit._validate_archive_prefix(None)
    expected_prefix = base_commit._ARCHIVE_PREFIX_TEMPLATE.format(
        repo_name='fake_repo',
        short_id='fake_id')
    assert isinstance(prefix, str)
    assert prefix == expected_prefix
