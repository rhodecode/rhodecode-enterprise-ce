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
import subprocess

import pytest

from rhodecode.lib.vcs.exceptions import VCSError
from rhodecode.lib.vcs.utils import author_email, author_name
from rhodecode.lib.vcs.utils.helpers import get_scm
from rhodecode.lib.vcs.utils.helpers import get_scms_for_path
from rhodecode.lib.vcs.utils.helpers import parse_datetime
from rhodecode.lib.vcs.utils.paths import get_dirs_for_path


@pytest.mark.usefixtures("pylonsapp")
class TestPaths:

    def _test_get_dirs_for_path(self, path, expected):
        """
        Tests if get_dirs_for_path returns same as expected.
        """
        expected = sorted(expected)
        result = sorted(get_dirs_for_path(path))
        assert result == expected, (
            "%s != %s which was expected result for path %s"
            % (result, expected, path))

    def test_get_dirs_for_path(self):
        path = 'foo/bar/baz/file'
        paths_and_results = (
            ('foo/bar/baz/file', ['foo', 'foo/bar', 'foo/bar/baz']),
            ('foo/bar/', ['foo', 'foo/bar']),
            ('foo/bar', ['foo']),
        )
        for path, expected in paths_and_results:
            self._test_get_dirs_for_path(path, expected)

    def test_get_scms_for_path(self, tmpdir):
        new = tmpdir.strpath
        assert get_scms_for_path(new) == []

        os.mkdir(os.path.join(new, '.tux'))
        assert get_scms_for_path(new) == []

        os.mkdir(os.path.join(new, '.git'))
        assert set(get_scms_for_path(new)) == set(['git'])

        os.mkdir(os.path.join(new, '.hg'))
        assert set(get_scms_for_path(new)) == set(['git', 'hg'])


class TestGetScm:

    def test_existing_repository(self, vcs_repository_support):
        alias, repo = vcs_repository_support
        assert (alias, repo.path) == get_scm(repo.path)

    def test_raises_if_path_is_empty(self, tmpdir):
        with pytest.raises(VCSError):
            get_scm(str(tmpdir))

    def test_get_scm_error_path(self):
        with pytest.raises(VCSError):
            get_scm('err')

    def test_get_two_scms_for_path(self, tmpdir):
        multialias_repo_path = str(tmpdir)

        subprocess.check_call(['hg', 'init', multialias_repo_path])
        subprocess.check_call(['git', 'init', multialias_repo_path])

        with pytest.raises(VCSError):
            get_scm(multialias_repo_path)

    def test_ignores_svn_working_copy(self, tmpdir):
        tmpdir.mkdir('.svn')
        with pytest.raises(VCSError):
            get_scm(tmpdir.strpath)


class TestParseDatetime:

    def test_datetime_text(self):
        assert parse_datetime('2010-04-07 21:29:41') == \
            datetime.datetime(2010, 4, 7, 21, 29, 41)

    def test_no_seconds(self):
        assert parse_datetime('2010-04-07 21:29') == \
            datetime.datetime(2010, 4, 7, 21, 29)

    def test_date_only(self):
        assert parse_datetime('2010-04-07') == \
            datetime.datetime(2010, 4, 7)

    def test_another_format(self):
        assert parse_datetime('04/07/10 21:29:41') == \
            datetime.datetime(2010, 4, 7, 21, 29, 41)

    def test_now(self):
        assert parse_datetime('now') - datetime.datetime.now() < \
            datetime.timedelta(seconds=1)

    def test_today(self):
        today = datetime.date.today()
        assert parse_datetime('today') == \
            datetime.datetime(*today.timetuple()[:3])

    def test_yesterday(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        assert parse_datetime('yesterday') == \
            datetime.datetime(*yesterday.timetuple()[:3])

    def test_tomorrow(self):
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        args = tomorrow.timetuple()[:3] + (23, 59, 59)
        assert parse_datetime('tomorrow') == datetime.datetime(*args)

    def test_days(self):
        timestamp = datetime.datetime.today() - datetime.timedelta(days=3)
        args = timestamp.timetuple()[:3] + (0, 0, 0, 0)
        expected = datetime.datetime(*args)
        assert parse_datetime('3d') == expected
        assert parse_datetime('3 d') == expected
        assert parse_datetime('3 day') == expected
        assert parse_datetime('3 days') == expected

    def test_weeks(self):
        timestamp = datetime.datetime.today() - datetime.timedelta(days=3 * 7)
        args = timestamp.timetuple()[:3] + (0, 0, 0, 0)
        expected = datetime.datetime(*args)
        assert parse_datetime('3w') == expected
        assert parse_datetime('3 w') == expected
        assert parse_datetime('3 week') == expected
        assert parse_datetime('3 weeks') == expected

    def test_mixed(self):
        timestamp = (
            datetime.datetime.today() - datetime.timedelta(days=2 * 7 + 3))
        args = timestamp.timetuple()[:3] + (0, 0, 0, 0)
        expected = datetime.datetime(*args)
        assert parse_datetime('2w3d') == expected
        assert parse_datetime('2w 3d') == expected
        assert parse_datetime('2w 3 days') == expected
        assert parse_datetime('2 weeks 3 days') == expected


@pytest.mark.parametrize("test_str, name, email", [
    ('Marcin Kuzminski <marcin@python-works.com>',
     'Marcin Kuzminski', 'marcin@python-works.com'),
    ('Marcin Kuzminski Spaces < marcin@python-works.com >',
     'Marcin Kuzminski Spaces', 'marcin@python-works.com'),
    ('Marcin Kuzminski <marcin.kuzminski@python-works.com>',
     'Marcin Kuzminski', 'marcin.kuzminski@python-works.com'),
    ('mrf RFC_SPEC <marcin+kuzminski@python-works.com>',
     'mrf RFC_SPEC', 'marcin+kuzminski@python-works.com'),
    ('username <user@email.com>',
     'username', 'user@email.com'),
    ('username <user@email.com',
     'username', 'user@email.com'),
    ('broken missing@email.com',
     'broken', 'missing@email.com'),
    ('<justemail@mail.com>',
     '', 'justemail@mail.com'),
    ('justname',
     'justname', ''),
    ('Mr Double Name withemail@email.com ',
     'Mr Double Name', 'withemail@email.com'),
])
class TestAuthorExtractors:

    def test_author_email(self, test_str, name, email):
        assert email == author_email(test_str)

    def test_author_name(self, test_str, name, email):
        assert name == author_name(test_str)
