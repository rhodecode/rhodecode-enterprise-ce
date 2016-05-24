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
Tests of :mod:`rhodecode.lib.diffs` around the context of a specific line.
"""

import textwrap

import pytest

from rhodecode.lib import diffs
from rhodecode.lib.vcs.backends.git.diff import GitDiff


def test_context_of_new_and_old_line_number_raises(diff_processor):
    with pytest.raises(ValueError):
        diff_processor.get_context_of_line(
            path='file.txt', diff_line=diffs.DiffLineNumber(old=7, new=7))


def test_context_of_an_old_line_number(diff_processor):
    context = diff_processor.get_context_of_line(
        path='file.txt', diff_line=diffs.DiffLineNumber(old=7, new=None))
    expected_context = [
        ('unmod', 'line04\n'),
        ('unmod', 'line05\n'),
        ('unmod', 'line06\n'),
        ('unmod', 'line07\n'),
        ('add', 'line07a Add after line07\n'),
        ('unmod', 'line08\n'),
        ('unmod', 'line09\n'),
    ]
    assert context == expected_context


def test_context_of_a_new_line_number(diff_processor):
    context = diff_processor.get_context_of_line(
        path='file.txt', diff_line=diffs.DiffLineNumber(old=None, new=8))
    expected_context = [
        ('unmod', 'line05\n'),
        ('unmod', 'line06\n'),
        ('unmod', 'line07\n'),
        ('add', 'line07a Add after line07\n'),
        ('unmod', 'line08\n'),
        ('unmod', 'line09\n'),
        ('unmod', 'line10\n'),
    ]
    assert context == expected_context


def test_context_of_an_invisible_line_beginning_of_hunk(diff_processor):
    # Note: The caller has to pass in a diff which is suitable to satisfy
    # its requirements. This test just ensures that we see a sane behavior.
    context = diff_processor.get_context_of_line(
        path='file.txt', diff_line=diffs.DiffLineNumber(old=None, new=3))
    expected_context = [
        ('unmod', 'line02\n'),
        ('unmod', 'line03\n'),
        ('unmod', 'line04\n'),
        ('unmod', 'line05\n'),
        ('unmod', 'line06\n'),
    ]
    assert context == expected_context


def test_context_of_an_invisible_line_end_of_hunk(diff_processor):
    # Note: The caller has to pass in a diff which is suitable to satisfy
    # its requirements. This test just ensures that we see a sane behavior.
    context = diff_processor.get_context_of_line(
        path='file.txt', diff_line=diffs.DiffLineNumber(old=12, new=None))
    expected_context = [
        ('unmod', 'line09\n'),
        ('unmod', 'line10\n'),
        ('unmod', 'line11\n'),
        ('unmod', 'line12\n'),
        ('unmod', 'line13\n'),
    ]
    assert context == expected_context


@pytest.mark.parametrize('diff_fixture', ['change-in-beginning.diff'])
def test_context_of_an_incomplete_hunk_in_the_beginning(diff_processor):
    context = diff_processor.get_context_of_line(
        path='file.txt', diff_line=diffs.DiffLineNumber(old=None, new=2))
    expected_context = [
        ('unmod', 'line01\n'),
        ('add', 'line01a Add line after line01\n'),
        ('unmod', 'line02\n'),
        ('unmod', 'line03\n'),
        ('unmod', 'line04\n'),
    ]
    assert context == expected_context


@pytest.mark.parametrize('diff_fixture', ['change-in-end.diff'])
def test_context_of_an_incomplete_hunk_in_the_end(diff_processor):
    context = diff_processor.get_context_of_line(
        path='file.txt', diff_line=diffs.DiffLineNumber(old=None, new=80))
    expected_context = [
        ('unmod', 'line36\n'),
        ('unmod', 'line37\n'),
        ('unmod', 'line38\n'),
        ('add', 'line38a Add line after line38\n'),
        ('unmod', 'line39\n'),
    ]
    assert context == expected_context


@pytest.mark.parametrize('diff_fixture', [
    'single-line.diff',
    'single-line-two-files.diff',
])
def test_appends_newline_for_each_context_line(diff_processor):
    context = diff_processor.get_context_of_line(
        path='file_b', diff_line=diffs.DiffLineNumber(old=None, new=1))
    assert context == [('add', 'test_content\n')]


def test_context_of_a_missing_line_raises(diff_processor):
    missing_line = 20
    with pytest.raises(diffs.LineNotInDiffException):
        diff_processor.get_context_of_line(
            path='file.txt',
            diff_line=diffs.DiffLineNumber(old=None, new=missing_line))


def test_context_of_a_missing_file_raises(diff_processor):
    with pytest.raises(diffs.FileNotInDiffException):
        diff_processor.get_context_of_line(
            path='not_existing_file.txt',
            diff_line=diffs.DiffLineNumber(old=None, new=8))


def test_find_context_with_full_context(diff_processor):
    context_of_line_7 = [
        ('unmod', 'line05\n'),
        ('unmod', 'line06\n'),
        ('unmod', 'line07\n'),
        ('add', 'line07a Add after line07\n'),
        ('unmod', 'line08\n'),
        ('unmod', 'line09\n'),
        ('unmod', 'line10\n'),
    ]
    found_line = diff_processor.find_context(
        'file.txt', context_of_line_7, offset=3)
    assert found_line == [diffs.DiffLineNumber(old=None, new=8)]


@pytest.mark.parametrize('diff_fixture', ['change-duplicated.diff'])
def test_find_context_multiple_times(diff_processor):
    context = [
        ('unmod', 'line04\n'),
        ('unmod', 'line05\n'),
        ('unmod', 'line06\n'),
        ('add', 'line06a add line\n'),
        ('unmod', 'line07\n'),
        ('unmod', 'line08\n'),
        ('unmod', 'line09\n'),
    ]
    found_line = diff_processor.find_context('file.txt', context, offset=3)
    assert found_line == [
        diffs.DiffLineNumber(old=None, new=7),
        diffs.DiffLineNumber(old=None, new=49),
    ]


@pytest.mark.parametrize('offset', [20, -20, -1, 7])
def test_find_context_offset_param_raises(diff_processor, offset):
    context_of_line_7 = [
        ('unmod', 'line04\n'),
        ('unmod', 'line05\n'),
        ('unmod', 'line06\n'),
        ('unmod', 'line07\n'),
        ('add', 'line07a Add after line07\n'),
        ('unmod', 'line08\n'),
        ('unmod', 'line09\n'),
    ]
    with pytest.raises(ValueError):
        diff_processor.find_context(
            'file.txt', context_of_line_7, offset=offset)


def test_find_context_beginning_of_chunk(diff_processor):
    context_of_first_line = [
        ('unmod', 'line02\n'),
        ('unmod', 'line03\n'),
        ('unmod', 'line04\n'),
        ('unmod', 'line05\n'),
    ]
    found_line = diff_processor.find_context(
        'file.txt', context_of_first_line, offset=0)
    assert found_line == [diffs.DiffLineNumber(old=2, new=2)]


@pytest.mark.parametrize('diff_fixture', ['change-in-beginning.diff'])
def test_find_context_beginning_of_file(diff_processor):
    context_of_first_line = [
        ('add', 'line01a Add line after line01\n'),
        ('unmod', 'line02\n'),
        ('unmod', 'line03\n'),
        ('unmod', 'line04\n'),
        ('unmod', 'line05\n'),
        ('unmod', 'line06\n'),
        ('unmod', 'line07\n'),
    ]
    found_line = diff_processor.find_context(
        'file.txt', context_of_first_line, offset=3)
    assert found_line == [diffs.DiffLineNumber(old=4, new=5)]


def test_find_context_end_of_chunk(diff_processor):
    context_of_last_line = [
        ('unmod', 'line10\n'),
        ('unmod', 'line11\n'),
        ('unmod', 'line12\n'),
        ('unmod', 'line13\n'),
    ]
    found_line = diff_processor.find_context(
        'file.txt', context_of_last_line, offset=3)
    assert found_line == [diffs.DiffLineNumber(old=13, new=14)]


@pytest.fixture
def diff_processor(request, diff_fixture):
    raw_diff = diffs_store[diff_fixture]
    diff = GitDiff(raw_diff)
    processor = diffs.DiffProcessor(diff)
    processor.prepare()
    return processor


@pytest.fixture
def diff_fixture():
    return 'default.diff'


diff_default = textwrap.dedent("""
    diff --git a/file.txt b/file.txt
    index 76e4f2e..6f8738f 100644
    --- a/file.txt
    +++ b/file.txt
    @@ -2,12 +2,13 @@ line01
     line02
     line03
     line04
     line05
     line06
     line07
    +line07a Add after line07
     line08
     line09
     line10
     line11
     line12
     line13
""")


diff_beginning = textwrap.dedent("""
    diff --git a/file.txt b/file.txt
    index 76e4f2e..47d39f4 100644
    --- a/file.txt
    +++ b/file.txt
    @@ -1,7 +1,8 @@
     line01
    +line01a Add line after line01
     line02
     line03
     line04
     line05
     line06
     line07
""")


diff_end = textwrap.dedent("""
    diff --git a/file.txt b/file.txt
    index 76e4f2e..b1304db 100644
    --- a/file.txt
    +++ b/file.txt
    @@ -74,7 +74,8 @@ line32
     line33
     line34
     line35
     line36
     line37
     line38
    +line38a Add line after line38
     line39
""")


diff_duplicated_change = textwrap.dedent("""
    diff --git a/file.txt b/file.txt
    index 76e4f2e..55c2781 100644
    --- a/file.txt
    +++ b/file.txt
    @@ -1,12 +1,13 @@
     line01
     line02
     line03
     line04
     line05
     line06
    +line06a add line
     line07
     line08
     line09
     line10
     line11
     line12
    @@ -42,12 +43,13 @@ line39
     line01
     line02
     line03
     line04
     line05
     line06
    +line06a add line
     line07
     line08
     line09
     line10
     line11
     line12
""")


diff_single_line = textwrap.dedent("""
    diff --git a/file_b b/file_b
    new file mode 100644
    index 00000000..915e94ff
    --- /dev/null
    +++ b/file_b
    @@ -0,0 +1 @@
    +test_content
""")


diff_single_line_two_files = textwrap.dedent("""
    diff --git a/file_b b/file_b
    new file mode 100644
    index 00000000..915e94ff
    --- /dev/null
    +++ b/file_b
    @@ -0,0 +1 @@
    +test_content
    diff --git a/file_c b/file_c
    new file mode 100644
    index 00000000..915e94ff
    --- /dev/null
    +++ b/file_c
    @@ -0,0 +1 @@
    +test_content
""")


diffs_store = {
    'default.diff': diff_default,
    'change-in-beginning.diff': diff_beginning,
    'change-in-end.diff': diff_end,
    'change-duplicated.diff': diff_duplicated_change,
    'single-line.diff': diff_single_line,
    'single-line-two-files.diff': diff_single_line_two_files,
}
