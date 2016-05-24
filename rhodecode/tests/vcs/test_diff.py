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
import pytest

from rhodecode.lib.vcs.nodes import FileNode
from rhodecode.tests.vcs.base import BackendTestMixin


class TestGetDiffValidation:

    def test_raises_on_string_input(self, vcsbackend):
        repo = vcsbackend.repo
        with pytest.raises(TypeError):
            repo.get_diff("1", "2")

    def test_raises_if_commits_not_of_this_repository(self, vcsbackend):
        repo = vcsbackend.repo
        target_repo = vcsbackend.create_repo(number_of_commits=1)
        repo_commit = repo[0]
        wrong_commit = target_repo[0]
        with pytest.raises(ValueError):
            repo.get_diff(repo_commit, wrong_commit)

    def test_allows_empty_commit(self, vcsbackend):
        repo = vcsbackend.repo
        commit = repo[0]
        repo.get_diff(repo.EMPTY_COMMIT, commit)

    def test_raise_if_both_commits_are_empty(self, vcsbackend):
        repo = vcsbackend.repo
        empty_commit = repo.EMPTY_COMMIT
        with pytest.raises(ValueError):
            repo.get_diff(empty_commit, empty_commit)

    def test_supports_path1_parameter(self, vcsbackend):
        repo = vcsbackend.repo
        commit = repo[1]
        repo.get_diff(
            repo.EMPTY_COMMIT, commit,
            path='vcs/__init__.py', path1='vcs/__init__.py')

    @pytest.mark.backends("git", "hg")
    def test_raises_value_error_if_paths_not_supported(self, vcsbackend):
        repo = vcsbackend.repo
        commit = repo[1]
        with pytest.raises(ValueError):
            repo.get_diff(
                repo.EMPTY_COMMIT, commit,
                path='trunk/example.py', path1='branches/argparse/example.py')


class TestRepositoryGetDiff(BackendTestMixin):

    recreate_repo_per_test = False

    @classmethod
    def _get_commits(cls):
        commits = [
            {
                'message': 'Initial commit',
                'author': 'Joe Doe <joe.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 20),
                'added': [
                    FileNode('foobar', content='foobar'),
                    FileNode('foobar2', content='foobar2'),
                ],
            },
            {
                'message': 'Changed foobar, added foobar3',
                'author': 'Jane Doe <jane.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 21),
                'added': [
                    FileNode('foobar3', content='foobar3'),
                ],
                'changed': [
                    FileNode('foobar', 'FOOBAR'),
                ],
            },
            {
                'message': 'Removed foobar, changed foobar3',
                'author': 'Jane Doe <jane.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 22),
                'changed': [
                    FileNode('foobar3', content='FOOBAR\nFOOBAR\nFOOBAR\n'),
                ],
                'removed': [FileNode('foobar')],
            },
            {
                'message': 'Whitespace changes',
                'author': 'Jane Doe <jane.doe@example.com>',
                'date': datetime.datetime(2010, 1, 1, 23),
                'changed': [
                    FileNode('foobar3', content='FOOBAR  \nFOOBAR\nFOOBAR\n'),
                ],
            },
        ]
        return commits

    def test_initial_commit_diff(self):
        initial_commit = self.repo[0]
        diff = self.repo.get_diff(self.repo.EMPTY_COMMIT, initial_commit)
        assert diff.raw == self.first_commit_diffs[self.repo.alias]

    def test_second_commit_diff(self):
        diff = self.repo.get_diff(self.repo[0], self.repo[1])
        assert diff.raw == self.second_commit_diffs[self.repo.alias]

    def test_third_commit_diff(self):
        diff = self.repo.get_diff(self.repo[1], self.repo[2])
        assert diff.raw == self.third_commit_diffs[self.repo.alias]

    def test_ignore_whitespace(self):
        diff = self.repo.get_diff(
            self.repo[2], self.repo[3], ignore_whitespace=True)
        assert '@@' not in diff.raw

    def test_only_one_file(self):
        diff = self.repo.get_diff(
            self.repo.EMPTY_COMMIT, self.repo[0], path='foobar')
        assert 'foobar2' not in diff.raw

    def test_context_parameter(self):
        first_commit = self.repo.get_commit(commit_idx=0)
        diff = self.repo.get_diff(
            self.repo.EMPTY_COMMIT, first_commit, context=2)
        assert diff.raw == self.first_commit_diffs[self.repo.alias]

    def test_context_only_one_file(self):
        diff = self.repo.get_diff(
            self.repo.EMPTY_COMMIT, self.repo[0], path='foobar', context=2)
        assert diff.raw == self.first_commit_one_file[self.repo.alias]

    first_commit_diffs = {
        'git': r"""diff --git a/foobar b/foobar
new file mode 100644
index 0000000000000000000000000000000000000000..f6ea0495187600e7b2288c8ac19c5886383a4632
--- /dev/null
+++ b/foobar
@@ -0,0 +1 @@
+foobar
\ No newline at end of file
diff --git a/foobar2 b/foobar2
new file mode 100644
index 0000000000000000000000000000000000000000..e8c9d6b98e3dce993a464935e1a53f50b56a3783
--- /dev/null
+++ b/foobar2
@@ -0,0 +1 @@
+foobar2
\ No newline at end of file
""",
        'hg': r"""diff --git a/foobar b/foobar
new file mode 100644
--- /dev/null
+++ b/foobar
@@ -0,0 +1,1 @@
+foobar
\ No newline at end of file
diff --git a/foobar2 b/foobar2
new file mode 100644
--- /dev/null
+++ b/foobar2
@@ -0,0 +1,1 @@
+foobar2
\ No newline at end of file
""",
        'svn': """Index: foobar
===================================================================
diff --git a/foobar b/foobar
new file mode 10644
--- /dev/null\t(revision 0)
+++ b/foobar\t(revision 1)
@@ -0,0 +1 @@
+foobar
\\ No newline at end of file
Index: foobar2
===================================================================
diff --git a/foobar2 b/foobar2
new file mode 10644
--- /dev/null\t(revision 0)
+++ b/foobar2\t(revision 1)
@@ -0,0 +1 @@
+foobar2
\\ No newline at end of file
""",
    }

    second_commit_diffs = {
        'git': r"""diff --git a/foobar b/foobar
index f6ea0495187600e7b2288c8ac19c5886383a4632..389865bb681b358c9b102d79abd8d5f941e96551 100644
--- a/foobar
+++ b/foobar
@@ -1 +1 @@
-foobar
\ No newline at end of file
+FOOBAR
\ No newline at end of file
diff --git a/foobar3 b/foobar3
new file mode 100644
index 0000000000000000000000000000000000000000..c11c37d41d33fb47741cff93fa5f9d798c1535b0
--- /dev/null
+++ b/foobar3
@@ -0,0 +1 @@
+foobar3
\ No newline at end of file
""",
        'hg': r"""diff --git a/foobar b/foobar
--- a/foobar
+++ b/foobar
@@ -1,1 +1,1 @@
-foobar
\ No newline at end of file
+FOOBAR
\ No newline at end of file
diff --git a/foobar3 b/foobar3
new file mode 100644
--- /dev/null
+++ b/foobar3
@@ -0,0 +1,1 @@
+foobar3
\ No newline at end of file
""",
        'svn': """Index: foobar
===================================================================
diff --git a/foobar b/foobar
--- a/foobar\t(revision 1)
+++ b/foobar\t(revision 2)
@@ -1 +1 @@
-foobar
\\ No newline at end of file
+FOOBAR
\\ No newline at end of file
Index: foobar3
===================================================================
diff --git a/foobar3 b/foobar3
new file mode 10644
--- /dev/null\t(revision 0)
+++ b/foobar3\t(revision 2)
@@ -0,0 +1 @@
+foobar3
\\ No newline at end of file
""",
    }

    third_commit_diffs = {
        'git': r"""diff --git a/foobar b/foobar
deleted file mode 100644
index 389865bb681b358c9b102d79abd8d5f941e96551..0000000000000000000000000000000000000000
--- a/foobar
+++ /dev/null
@@ -1 +0,0 @@
-FOOBAR
\ No newline at end of file
diff --git a/foobar3 b/foobar3
index c11c37d41d33fb47741cff93fa5f9d798c1535b0..f9324477362684ff692aaf5b9a81e01b9e9a671c 100644
--- a/foobar3
+++ b/foobar3
@@ -1 +1,3 @@
-foobar3
\ No newline at end of file
+FOOBAR
+FOOBAR
+FOOBAR
""",
        'hg': r"""diff --git a/foobar b/foobar
deleted file mode 100644
--- a/foobar
+++ /dev/null
@@ -1,1 +0,0 @@
-FOOBAR
\ No newline at end of file
diff --git a/foobar3 b/foobar3
--- a/foobar3
+++ b/foobar3
@@ -1,1 +1,3 @@
-foobar3
\ No newline at end of file
+FOOBAR
+FOOBAR
+FOOBAR
""",
        'svn': """Index: foobar
===================================================================
diff --git a/foobar b/foobar
deleted file mode 10644
--- a/foobar\t(revision 2)
+++ /dev/null\t(revision 3)
@@ -1 +0,0 @@
-FOOBAR
\\ No newline at end of file
Index: foobar3
===================================================================
diff --git a/foobar3 b/foobar3
--- a/foobar3\t(revision 2)
+++ b/foobar3\t(revision 3)
@@ -1 +1,3 @@
-foobar3
\\ No newline at end of file
+FOOBAR
+FOOBAR
+FOOBAR
""",
    }

    first_commit_one_file = {
        'git': r"""diff --git a/foobar b/foobar
new file mode 100644
index 0000000000000000000000000000000000000000..f6ea0495187600e7b2288c8ac19c5886383a4632
--- /dev/null
+++ b/foobar
@@ -0,0 +1 @@
+foobar
\ No newline at end of file
""",
        'hg': r"""diff --git a/foobar b/foobar
new file mode 100644
--- /dev/null
+++ b/foobar
@@ -0,0 +1,1 @@
+foobar
\ No newline at end of file
""",
        'svn': """Index: foobar
===================================================================
diff --git a/foobar b/foobar
new file mode 10644
--- /dev/null\t(revision 0)
+++ b/foobar\t(revision 1)
@@ -0,0 +1 @@
+foobar
\\ No newline at end of file
""",
    }


class TestSvnGetDiff:

    @pytest.mark.parametrize('path, path1', [
        ('trunk/example.py', 'tags/v0.2/example.py'),
        ('trunk', 'tags/v0.2')
    ], ids=['file', 'dir'])
    def test_diff_to_tagged_version(self, vcsbackend_svn, path, path1):
        repo = vcsbackend_svn['svn-simple-layout']
        commit = repo[-1]
        diff = repo.get_diff(commit, commit, path=path, path1=path1)
        assert diff.raw == self.expected_diff_v_0_2

    expected_diff_v_0_2 = '''Index: example.py
===================================================================
diff --git a/example.py b/example.py
--- a/example.py\t(revision 26)
+++ b/example.py\t(revision 26)
@@ -7,8 +7,12 @@
 
 @click.command()
 def main():
+    """
+    Will print out a useful message on invocation.
+    """
     click.echo("Hello world!")
 
 
+# Main entry point
 if __name__ == '__main__':
     main()
'''

    def test_diff_of_moved_directory(self, vcsbackend_svn):
        repo = vcsbackend_svn['svn-move-directory']
        diff = repo.get_diff(repo[0], repo[1])
        # TODO: johbo: Think about supporting svn directory nodes
        # a little bit better, source is here like a file
        expected_diff = """Index: source
===================================================================
diff --git a/source b/source
deleted file mode 10644
--- a/source\t(revision 1)
+++ /dev/null\t(revision 2)
Index: target/file
===================================================================
diff --git a/target/file b/target/file
new file mode 10644
--- /dev/null\t(revision 0)
+++ b/target/file\t(revision 2)
"""
        assert diff.raw == expected_diff


class TestGetDiffBinary(BackendTestMixin):

    recreate_repo_per_test = False

    # Note: "Fake" PNG files, has the correct magic as prefix
    BINARY = """\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00"""
    BINARY2 = """\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x01\x00\x00"""

    @staticmethod
    def _get_commits():
        commits = [
            {
                'message': 'Add binary file image.png',
                'author': 'Joe Doe <joe.deo@example.com>',
                'date': datetime.datetime(2010, 1, 1, 20),
                'added': [
                    FileNode('image.png', content=TestGetDiffBinary.BINARY),
                ]},
            {
                'message': 'Modify image.png',
                'author': 'Joe Doe <joe.deo@example.com>',
                'date': datetime.datetime(2010, 1, 1, 21),
                'changed': [
                    FileNode('image.png', content=TestGetDiffBinary.BINARY2),
                ]},
            {
                'message': 'Remove image.png',
                'author': 'Joe Doe <joe.deo@example.com>',
                'date': datetime.datetime(2010, 1, 1, 21),
                'removed': [
                    FileNode('image.png'),
                ]},
        ]
        return commits

    def test_add_a_binary_file(self):
        diff = self.repo.get_diff(self.repo.EMPTY_COMMIT, self.repo[0])

        expected = {
            'git': """diff --git a/image.png b/image.png
new file mode 100644
index 0000000000000000000000000000000000000000..28380fd4a25c58be1b68b523ba2a314f4459ee9c
GIT binary patch
literal 19
YcmeAS@N?(olHy`uVBq!ia0vp^03%2O-T(jq

literal 0
HcmV?d00001

""",
            'hg': """diff --git a/image.png b/image.png
new file mode 100644
index e69de29bb2d1d6434b8b29ae775ad8c2e48c5391..28380fd4a25c58be1b68b523ba2a314f4459ee9c
GIT binary patch
literal 19
Yc%17D@N?(olHy`uVBq!ia0vp^03%2O-T(jq

""",
            'svn': """===================================================================
Cannot display: file marked as a binary type.
svn:mime-type = application/octet-stream
Index: image.png
===================================================================
diff --git a/image.png b/image.png
new file mode 10644
--- /dev/null\t(revision 0)
+++ b/image.png\t(revision 1)
""",
        }
        assert diff.raw == expected[self.repo.alias]

    def test_update_a_binary_file(self):
        diff = self.repo.get_diff(self.repo[0], self.repo[1])

        expected = {
            'git': """diff --git a/image.png b/image.png
index 28380fd4a25c58be1b68b523ba2a314f4459ee9c..1008a77cd372386a1c24fbd96019333f67ad0065 100644
GIT binary patch
literal 19
acmeAS@N?(olHy`uVBq!ia0y~$U;qFkO9I~j

literal 19
YcmeAS@N?(olHy`uVBq!ia0vp^03%2O-T(jq

""",
            'hg': """diff --git a/image.png b/image.png
index 28380fd4a25c58be1b68b523ba2a314f4459ee9c..1008a77cd372386a1c24fbd96019333f67ad0065
GIT binary patch
literal 19
ac%17D@N?(olHy`uVBq!ia0y~$U;qFkO9I~j

""",
            'svn': """===================================================================
Cannot display: file marked as a binary type.
svn:mime-type = application/octet-stream
Index: image.png
===================================================================
diff --git a/image.png b/image.png
--- a/image.png\t(revision 1)
+++ b/image.png\t(revision 2)
""",
        }
        assert diff.raw == expected[self.repo.alias]

    def test_remove_a_binary_file(self):
        diff = self.repo.get_diff(self.repo[1], self.repo[2])

        expected = {
            'git': """diff --git a/image.png b/image.png
deleted file mode 100644
index 1008a77cd372386a1c24fbd96019333f67ad0065..0000000000000000000000000000000000000000
GIT binary patch
literal 0
HcmV?d00001

literal 19
acmeAS@N?(olHy`uVBq!ia0y~$U;qFkO9I~j

""",
            'hg': """diff --git a/image.png b/image.png
deleted file mode 100644
index 1008a77cd372386a1c24fbd96019333f67ad0065..e69de29bb2d1d6434b8b29ae775ad8c2e48c5391
GIT binary patch
literal 0
Hc$@<O00001

""",
            'svn': """===================================================================
Cannot display: file marked as a binary type.
svn:mime-type = application/octet-stream
Index: image.png
===================================================================
diff --git a/image.png b/image.png
deleted file mode 10644
--- a/image.png\t(revision 2)
+++ /dev/null\t(revision 3)
""",
        }
        assert diff.raw == expected[self.repo.alias]
