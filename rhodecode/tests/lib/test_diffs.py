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

import textwrap

import pytest

from rhodecode.lib.diffs import (
    DiffProcessor, wrapped_diff,
    NEW_FILENODE, DEL_FILENODE, MOD_FILENODE, RENAMED_FILENODE,
    CHMOD_FILENODE, BIN_FILENODE, COPIED_FILENODE)
from rhodecode.tests.fixture import Fixture
from rhodecode.lib.vcs.backends.git.repository import GitDiff
from rhodecode.lib.vcs.backends.hg.repository import MercurialDiff
from rhodecode.lib.vcs.backends.svn.repository import SubversionDiff

fixture = Fixture()


def test_wrapped_diff_limited_file_diff(vcsbackend_random):
    vcsbackend = vcsbackend_random
    repo = vcsbackend.create_repo()
    vcsbackend.add_file(repo, 'a_file', content="line 1\nline 2\nline3\n")
    commit = repo.get_commit()
    file_node = commit.get_node('a_file')

    # Only limit the file diff to trigger the code path
    result = wrapped_diff(
        None, file_node, diff_limit=10000, file_limit=1)
    data = result[5]

    # Verify that the limits were applied
    assert data['exceeds_limit'] is True
    assert data['is_limited_diff'] is True


def test_diffprocessor_as_html_with_comments():
    raw_diff = textwrap.dedent('''
        diff --git a/setup.py b/setup.py
        index 5b36422..cfd698e 100755
        --- a/setup.py
        +++ b/setup.py
        @@ -2,7 +2,7 @@
         #!/usr/bin/python
         # Setup file for X
         # Copyright (C) No one
        -
        +x
         try:
             from setuptools import setup, Extension
         except ImportError:
    ''')
    diff = GitDiff(raw_diff)
    processor = DiffProcessor(diff)
    processor.prepare()

    # Note that the cell with the context in line 5 (in the html) has the
    # no-comment class, which will prevent the add comment icon to be displayed.
    expected_html = textwrap.dedent('''
        <table class="code-difftable">
        <tr class="line context">
            <td class="add-comment-line"><span class="add-comment-content"></span></td>
            <td  class="lineno old">...</td>
            <td  class="lineno new">...</td>
            <td class="code no-comment">
                <pre>@@ -2,7 +2,7 @@
        </pre>
            </td>
        </tr>
        <tr class="line unmod">
            <td class="add-comment-line"><span class="add-comment-content"><a href="#"><span class="icon-comment-add"></span></a></span></td>
            <td id="setuppy_o2" class="lineno old"><a href="#setuppy_o2">2</a></td>
            <td id="setuppy_n2" class="lineno new"><a href="#setuppy_n2">2</a></td>
            <td class="code">
                <pre>#!/usr/bin/python
        </pre>
            </td>
        </tr>
        <tr class="line unmod">
            <td class="add-comment-line"><span class="add-comment-content"><a href="#"><span class="icon-comment-add"></span></a></span></td>
            <td id="setuppy_o3" class="lineno old"><a href="#setuppy_o3">3</a></td>
            <td id="setuppy_n3" class="lineno new"><a href="#setuppy_n3">3</a></td>
            <td class="code">
                <pre># Setup file for X
        </pre>
            </td>
        </tr>
        <tr class="line unmod">
            <td class="add-comment-line"><span class="add-comment-content"><a href="#"><span class="icon-comment-add"></span></a></span></td>
            <td id="setuppy_o4" class="lineno old"><a href="#setuppy_o4">4</a></td>
            <td id="setuppy_n4" class="lineno new"><a href="#setuppy_n4">4</a></td>
            <td class="code">
                <pre># Copyright (C) No one
        </pre>
            </td>
        </tr>
        <tr class="line del">
            <td class="add-comment-line"><span class="add-comment-content"><a href="#"><span class="icon-comment-add"></span></a></span></td>
            <td id="setuppy_o5" class="lineno old"><a href="#setuppy_o5">5</a></td>
            <td  class="lineno new"><a href="#setuppy_n"></a></td>
            <td class="code">
                <pre>
        </pre>
            </td>
        </tr>
        <tr class="line add">
            <td class="add-comment-line"><span class="add-comment-content"><a href="#"><span class="icon-comment-add"></span></a></span></td>
            <td  class="lineno old"><a href="#setuppy_o"></a></td>
            <td id="setuppy_n5" class="lineno new"><a href="#setuppy_n5">5</a></td>
            <td class="code">
                <pre><ins>x</ins>
        </pre>
            </td>
        </tr>
        <tr class="line unmod">
            <td class="add-comment-line"><span class="add-comment-content"><a href="#"><span class="icon-comment-add"></span></a></span></td>
            <td id="setuppy_o6" class="lineno old"><a href="#setuppy_o6">6</a></td>
            <td id="setuppy_n6" class="lineno new"><a href="#setuppy_n6">6</a></td>
            <td class="code">
                <pre>try:
        </pre>
            </td>
        </tr>
        <tr class="line unmod">
            <td class="add-comment-line"><span class="add-comment-content"><a href="#"><span class="icon-comment-add"></span></a></span></td>
            <td id="setuppy_o7" class="lineno old"><a href="#setuppy_o7">7</a></td>
            <td id="setuppy_n7" class="lineno new"><a href="#setuppy_n7">7</a></td>
            <td class="code">
                <pre>    from setuptools import setup, Extension
        </pre>
            </td>
        </tr>
        <tr class="line unmod">
            <td class="add-comment-line"><span class="add-comment-content"><a href="#"><span class="icon-comment-add"></span></a></span></td>
            <td id="setuppy_o8" class="lineno old"><a href="#setuppy_o8">8</a></td>
            <td id="setuppy_n8" class="lineno new"><a href="#setuppy_n8">8</a></td>
            <td class="code">
                <pre>except ImportError:
        </pre>
            </td>
        </tr>
        </table>
    ''').strip()
    html = processor.as_html(enable_comments=True).replace('\t', '    ')

    assert html == expected_html


class TestMixedFilenameEncodings:

    @pytest.fixture(scope="class")
    def raw_diff(self):
        return fixture.load_resource(
            'hg_diff_mixed_filename_encodings.diff')

    @pytest.fixture
    def processor(self, raw_diff):
        diff = MercurialDiff(raw_diff)
        processor = DiffProcessor(diff)
        return processor

    def test_filenames_are_decoded_to_unicode(self, processor):
        diff_data = processor.prepare()
        filenames = [item['filename'] for item in diff_data]
        assert filenames == [
            u'späcial-utf8.txt', u'sp�cial-cp1252.txt', u'sp�cial-latin1.txt']

    def test_raw_diff_is_decoded_to_unicode(self, processor):
        diff_data = processor.prepare()
        raw_diffs = [item['raw_diff'] for item in diff_data]
        new_file_message = u'\nnew file mode 100644\n'
        expected_raw_diffs = [
            u' a/späcial-utf8.txt b/späcial-utf8.txt' + new_file_message,
            u' a/sp�cial-cp1252.txt b/sp�cial-cp1252.txt' + new_file_message,
            u' a/sp�cial-latin1.txt b/sp�cial-latin1.txt' + new_file_message]
        assert raw_diffs == expected_raw_diffs

    def test_as_raw_preserves_the_encoding(self, processor, raw_diff):
        assert processor.as_raw() == raw_diff


# TODO: mikhail: format the following data structure properly
DIFF_FIXTURES = [
    ('hg',
     'hg_diff_add_single_binary_file.diff',
     [('US Warszawa.jpg', 'A',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {NEW_FILENODE: 'new file 100755',
                BIN_FILENODE: 'binary diff hidden'}}),
      ]),
    ('hg',
     'hg_diff_mod_single_binary_file.diff',
     [('US Warszawa.jpg', 'M',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {MOD_FILENODE: 'modified file',
                BIN_FILENODE: 'binary diff hidden'}}),
      ]),
    ('hg',
     'hg_diff_mod_single_file_and_rename_and_chmod.diff',
     [('README', 'M',
       {'added': 3,
        'deleted': 0,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file',
                RENAMED_FILENODE: 'file renamed from README.rst to README',
                CHMOD_FILENODE: 'modified file chmod 100755 => 100644'}}),
      ]),
    ('hg',
     'hg_diff_mod_file_and_rename.diff',
     [('README.rst', 'M',
       {'added': 3,
        'deleted': 0,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file',
                RENAMED_FILENODE: 'file renamed from README to README.rst'}}),
      ]),
    ('hg',
     'hg_diff_del_single_binary_file.diff',
     [('US Warszawa.jpg', 'D',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {DEL_FILENODE: 'deleted file',
                BIN_FILENODE: 'binary diff hidden'}}),
      ]),
    ('hg',
     'hg_diff_chmod_and_mod_single_binary_file.diff',
     [('gravatar.png', 'M',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {CHMOD_FILENODE: 'modified file chmod 100644 => 100755',
                BIN_FILENODE: 'binary diff hidden'}}),
      ]),
    ('hg',
     'hg_diff_chmod.diff',
     [('file', 'M',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {CHMOD_FILENODE: 'modified file chmod 100755 => 100644'}}),
      ]),
    ('hg',
     'hg_diff_rename_file.diff',
     [('file_renamed', 'M',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {RENAMED_FILENODE: 'file renamed from file to file_renamed'}}),
      ]),
    ('hg',
     'hg_diff_rename_and_chmod_file.diff',
     [('README', 'M',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {CHMOD_FILENODE: 'modified file chmod 100644 => 100755',
                RENAMED_FILENODE: 'file renamed from README.rst to README'}}),
      ]),
    ('hg',
     'hg_diff_binary_and_normal.diff',
     [('img/baseline-10px.png', 'A',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {NEW_FILENODE: 'new file 100644',
                BIN_FILENODE: 'binary diff hidden'}}),
      ('js/jquery/hashgrid.js', 'A',
       {'added': 340,
        'deleted': 0,
        'binary': False,
        'ops': {NEW_FILENODE: 'new file 100755'}}),
      ('index.html', 'M',
       {'added': 3,
        'deleted': 2,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file'}}),
      ('less/docs.less', 'M',
       {'added': 34,
        'deleted': 0,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file'}}),
      ('less/scaffolding.less', 'M',
       {'added': 1,
        'deleted': 3,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file'}}),
      ('readme.markdown', 'M',
       {'added': 1,
        'deleted': 10,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file'}}),
      ('img/baseline-20px.png', 'D',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {DEL_FILENODE: 'deleted file',
                BIN_FILENODE: 'binary diff hidden'}}),
      ('js/global.js', 'D',
       {'added': 0,
        'deleted': 75,
        'binary': False,
        'ops': {DEL_FILENODE: 'deleted file'}})
      ]),
    ('git',
     'git_diff_chmod.diff',
     [('work-horus.xls', 'M',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {CHMOD_FILENODE: 'modified file chmod 100644 => 100755'}})
      ]),
    ('git',
     'git_diff_rename_file.diff',
     [('file.xls', 'M',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {
            RENAMED_FILENODE: 'file renamed from work-horus.xls to file.xls'}})
      ]),
    ('git',
     'git_diff_mod_single_binary_file.diff',
     [('US Warszawa.jpg', 'M',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {MOD_FILENODE: 'modified file',
                BIN_FILENODE: 'binary diff hidden'}})
      ]),
    ('git',
     'git_diff_binary_and_normal.diff',
     [('img/baseline-10px.png', 'A',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {NEW_FILENODE: 'new file 100644',
                BIN_FILENODE: 'binary diff hidden'}}),
      ('js/jquery/hashgrid.js', 'A',
       {'added': 340,
        'deleted': 0,
        'binary': False,
        'ops': {NEW_FILENODE: 'new file 100755'}}),
      ('index.html', 'M',
       {'added': 3,
        'deleted': 2,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file'}}),
      ('less/docs.less', 'M',
       {'added': 34,
        'deleted': 0,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file'}}),
      ('less/scaffolding.less', 'M',
       {'added': 1,
        'deleted': 3,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file'}}),
      ('readme.markdown', 'M',
       {'added': 1,
        'deleted': 10,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file'}}),
      ('img/baseline-20px.png', 'D',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {DEL_FILENODE: 'deleted file',
                BIN_FILENODE: 'binary diff hidden'}}),
      ('js/global.js', 'D',
       {'added': 0,
        'deleted': 75,
        'binary': False,
        'ops': {DEL_FILENODE: 'deleted file'}}),
      ]),
    ('hg',
     'diff_with_diff_data.diff',
     [('vcs/backends/base.py', 'M',
       {'added': 18,
        'deleted': 2,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file'}}),
      ('vcs/backends/git/repository.py', 'M',
       {'added': 46,
        'deleted': 15,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file'}}),
      ('vcs/backends/hg.py', 'M',
       {'added': 22,
        'deleted': 3,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file'}}),
      ('vcs/tests/test_git.py', 'M',
       {'added': 5,
        'deleted': 5,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file'}}),
      ('vcs/tests/test_repository.py', 'M',
       {'added': 174,
        'deleted': 2,
        'binary': False,
        'ops': {MOD_FILENODE: 'modified file'}}),
      ]),
    ('hg',
     'hg_diff_copy_file.diff',
     [('file2', 'M',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {COPIED_FILENODE: 'file copied from file1 to file2'}}),
      ]),
    ('hg',
     'hg_diff_copy_and_modify_file.diff',
     [('file3', 'M',
       {'added': 1,
        'deleted': 0,
        'binary': False,
        'ops': {COPIED_FILENODE: 'file copied from file2 to file3',
                MOD_FILENODE: 'modified file'}}),
      ]),
    ('hg',
     'hg_diff_copy_and_chmod_file.diff',
     [('file4', 'M',
       {'added': 0,
        'deleted': 0,
        'binary': True,
        'ops': {COPIED_FILENODE: 'file copied from file3 to file4',
                CHMOD_FILENODE: 'modified file chmod 100644 => 100755'}}),
      ]),
    ('hg',
     'hg_diff_copy_chmod_and_edit_file.diff',
     [('file5', 'M',
       {'added': 2,
        'deleted': 1,
        'binary': False,
        'ops': {COPIED_FILENODE: 'file copied from file4 to file5',
                CHMOD_FILENODE: 'modified file chmod 100755 => 100644',
                MOD_FILENODE: 'modified file'}})]),

    # Diffs to validate rename and copy file with space in its name
    ('git',
     'git_diff_rename_file_with_spaces.diff',
     [('file_with_  two spaces.txt', 'M',
         {'added': 0,
          'deleted': 0,
          'binary': True,
          'ops': {
              RENAMED_FILENODE: (
                  'file renamed from file_with_ spaces.txt to file_with_ '
                  ' two spaces.txt')}
          }), ]),
    ('hg',
     'hg_diff_rename_file_with_spaces.diff',
     [('file_changed _.txt', 'M',
         {'added': 0,
          'deleted': 0,
          'binary': True,
          'ops': {
              RENAMED_FILENODE: (
                  'file renamed from file_ with update.txt to file_changed'
                  ' _.txt')}
          }), ]),
    ('hg',
     'hg_diff_copy_file_with_spaces.diff',
     [('file_copied_ with  spaces.txt', 'M',
         {'added': 0,
          'deleted': 0,
          'binary': True,
          'ops': {
              COPIED_FILENODE: (
                  'file copied from file_changed_without_spaces.txt to'
                  ' file_copied_ with  spaces.txt')}
          }),
      ]),

    # special signs from git
    ('git',
     'git_diff_binary_special_files.diff',
     [('css/_Icon\\r', 'A',
         {'added': 0,
          'deleted': 0,
          'binary': True,
          'ops': {NEW_FILENODE: 'new file 100644',
                  BIN_FILENODE: 'binary diff hidden'}
          }),
      ]),
    ('git',
     'git_diff_binary_special_files_2.diff',
     [('css/Icon\\r', 'A',
         {'added': 0,
          'deleted': 0,
          'binary': True,
          'ops': {NEW_FILENODE: 'new file 100644', }
          }),
      ]),

    # TODO: mikhail: do we still need this?
    # (
    #     'hg',
    #     'large_diff.diff',
    #     [
    #         ('.hgignore', 'A', {
    #             'deleted': 0, 'binary': False, 'added': 3, 'ops': {
    #                 1: 'new file 100644'}}),
    #         (
    #             'MANIFEST.in', 'A',
    #             {'deleted': 0, 'binary': False, 'added': 3, 'ops': {
    #                 1: 'new file 100644'}}),
    #         (
    #             'README.txt', 'A',
    #             {'deleted': 0, 'binary': False, 'added': 19, 'ops': {
    #                 1: 'new file 100644'}}),
    #         (
    #             'development.ini', 'A', {
    #                 'deleted': 0, 'binary': False, 'added': 116, 'ops': {
    #                     1: 'new file 100644'}}),
    #         (
    #             'docs/index.txt', 'A', {
    #                 'deleted': 0, 'binary': False, 'added': 19, 'ops': {
    #                     1: 'new file 100644'}}),
    #         (
    #             'ez_setup.py', 'A', {
    #                 'deleted': 0, 'binary': False, 'added': 276, 'ops': {
    #                     1: 'new file 100644'}}),
    #         (
    #             'hgapp.py', 'A', {
    #                 'deleted': 0, 'binary': False, 'added': 26, 'ops': {
    #                     1: 'new file 100644'}}),
    #         (
    #             'hgwebdir.config', 'A', {
    #                 'deleted': 0, 'binary': False, 'added': 21, 'ops': {
    #                     1: 'new file 100644'}}),
    #         (
    #             'pylons_app.egg-info/PKG-INFO', 'A', {
    #                 'deleted': 0, 'binary': False, 'added': 10, 'ops': {
    #                     1: 'new file 100644'}}),
    #         (
    #             'pylons_app.egg-info/SOURCES.txt', 'A', {
    #                 'deleted': 0, 'binary': False, 'added': 33, 'ops': {
    #                     1: 'new file 100644'}}),
    #         (
    #             'pylons_app.egg-info/dependency_links.txt', 'A', {
    #                 'deleted': 0, 'binary': False, 'added': 1, 'ops': {
    #                     1: 'new file 100644'}}),
    #         #TODO:
    #     ]
    # ),
]

DIFF_FIXTURES_WITH_CONTENT = [
    (
        'hg', 'hg_diff_single_file_change_newline.diff',
        [
            (
                'file_b',  # filename
                'A',  # change
                {  # stats
                   'added': 1,
                   'deleted': 0,
                   'binary': False,
                   'ops': {NEW_FILENODE: 'new file 100644', }
                },
                '@@ -0,0 +1 @@\n+test_content b\n'  # diff
            ),
        ],
    ),
    (
        'hg', 'hg_diff_double_file_change_newline.diff',
        [
            (
                'file_b',  # filename
                'A',  # change
                {  # stats
                   'added': 1,
                   'deleted': 0,
                   'binary': False,
                   'ops': {NEW_FILENODE: 'new file 100644', }
                },
                '@@ -0,0 +1 @@\n+test_content b\n'  # diff
            ),
            (
                'file_c',  # filename
                'A',  # change
                {  # stats
                   'added': 1,
                   'deleted': 0,
                   'binary': False,
                   'ops': {NEW_FILENODE: 'new file 100644', }
                },
                '@@ -0,0 +1 @@\n+test_content c\n'  # diff
            ),
        ],
    ),
    (
        'hg', 'hg_diff_double_file_change_double_newline.diff',
        [
            (
                'file_b',  # filename
                'A',  # change
                {  # stats
                   'added': 1,
                   'deleted': 0,
                   'binary': False,
                   'ops': {NEW_FILENODE: 'new file 100644', }
                },
                '@@ -0,0 +1 @@\n+test_content b\n\n'  # diff
            ),
            (
                'file_c',  # filename
                'A',  # change
                {  # stats
                   'added': 1,
                   'deleted': 0,
                   'binary': False,
                   'ops': {NEW_FILENODE: 'new file 100644', }
                },
                '@@ -0,0 +1 @@\n+test_content c\n'  # diff
            ),
        ],
    ),
    (
        'hg', 'hg_diff_four_file_change_newline.diff',
        [
            (
                'file',  # filename
                'A',  # change
                {  # stats
                   'added': 1,
                   'deleted': 0,
                   'binary': False,
                   'ops': {NEW_FILENODE: 'new file 100644', }
                },
                '@@ -0,0 +1,1 @@\n+file\n'  # diff
            ),
            (
                'file2',  # filename
                'A',  # change
                {  # stats
                   'added': 1,
                   'deleted': 0,
                   'binary': False,
                   'ops': {NEW_FILENODE: 'new file 100644', }
                },
                '@@ -0,0 +1,1 @@\n+another line\n'  # diff
            ),
            (
                'file3',  # filename
                'A',  # change
                {  # stats
                   'added': 1,
                   'deleted': 0,
                   'binary': False,
                   'ops': {NEW_FILENODE: 'new file 100644', }
                },
                '@@ -0,0 +1,1 @@\n+newline\n'  # diff
            ),
            (
                'file4',  # filename
                'A',  # change
                {  # stats
                   'added': 1,
                   'deleted': 0,
                   'binary': False,
                   'ops': {NEW_FILENODE: 'new file 100644', }
                },
                '@@ -0,0 +1,1 @@\n+fil4\n\\ No newline at end of file'  # diff
            ),
        ],
    ),

]


diff_class = {
    'git': GitDiff,
    'hg': MercurialDiff,
    'svn': SubversionDiff,
}


@pytest.fixture(params=DIFF_FIXTURES)
def diff_fixture(request):
    vcs, diff_fixture, expected = request.param
    diff_txt = fixture.load_resource(diff_fixture)
    diff = diff_class[vcs](diff_txt)
    return diff, expected


def test_diff_lib(diff_fixture):
    diff, expected_data = diff_fixture
    diff_proc = DiffProcessor(diff)
    diff_proc_d = diff_proc.prepare()
    data = [(x['filename'], x['operation'], x['stats']) for x in diff_proc_d]
    assert expected_data == data


@pytest.fixture(params=DIFF_FIXTURES_WITH_CONTENT)
def diff_fixture_w_content(request):
    vcs, diff_fixture, expected = request.param
    diff_txt = fixture.load_resource(diff_fixture)
    diff = diff_class[vcs](diff_txt)
    return diff, expected


def test_diff_lib_newlines(diff_fixture_w_content):
    diff, expected_data = diff_fixture_w_content
    diff_proc = DiffProcessor(diff)
    diff_proc_d = diff_proc.prepare()
    data = [(x['filename'], x['operation'], x['stats'], x['raw_diff'])
            for x in diff_proc_d]
    assert expected_data == data
