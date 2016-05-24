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

import pytest

from rhodecode.lib.helpers import _shorten_commit_id
from rhodecode.tests import url


@pytest.mark.usefixtures("app")
class TestChangesetController(object):

    def test_index(self, backend):
        commit_id = self.commit_id[backend.alias]
        response = self.app.get(url(
            controller='changeset', action='index',
            repo_name=backend.repo_name, revision=commit_id))
        response.mustcontain('Added a symlink')
        response.mustcontain(commit_id)
        response.mustcontain('No newline at end of file')

    def test_index_raw(self, backend):
        commit_id = self.commit_id[backend.alias]
        response = self.app.get(url(
            controller='changeset', action='changeset_raw',
            repo_name=backend.repo_name, revision=commit_id))
        assert response.body == self.diffs[backend.alias]

    def test_index_raw_patch(self, backend):
        response = self.app.get(url(
            controller='changeset', action='changeset_patch',
            repo_name=backend.repo_name,
            revision=self.commit_id[backend.alias]))
        assert response.body == self.patches[backend.alias]

    def test_index_changeset_download(self, backend):
        response = self.app.get(url(
            controller='changeset', action='changeset_download',
            repo_name=backend.repo_name,
            revision=self.commit_id[backend.alias]))
        assert response.body == self.diffs[backend.alias]

    @pytest.mark.xfail_backends("svn", reason="Depends on consistent diffs")
    def test_single_commit_page_different_ops(self, backend):
        commit_id = {
            'hg': '603d6c72c46d953420c89d36372f08d9f305f5dd',
            'git': '03fa803d7e9fb14daa9a3089e0d1494eda75d986',
            'svn': '337',
        }
        commit_id = commit_id[backend.alias]
        response = self.app.get(url(
            controller='changeset', action='index',
            repo_name=backend.repo_name, revision=commit_id))

        response.mustcontain(_shorten_commit_id(commit_id))
        response.mustcontain('21 files changed: 943 inserted, 288 deleted')

        # files op files
        response.mustcontain('File no longer present at commit: %s' %
                             _shorten_commit_id(commit_id))
        response.mustcontain('new file 100644')
        response.mustcontain('Changed theme to ADC theme')  # commit msg

        self._check_diff_menus(response, right_menu=True)

    @pytest.mark.xfail_backends("svn", reason="Depends on consistent diffs")
    def test_commit_range_page_different_ops(self, backend):
        commit_id_range = {
            'hg': (
                '25d7e49c18b159446cadfa506a5cf8ad1cb04067',
                '603d6c72c46d953420c89d36372f08d9f305f5dd'),
            'git': (
                '6fc9270775aaf5544c1deb014f4ddd60c952fcbb',
                '03fa803d7e9fb14daa9a3089e0d1494eda75d986'),
            'svn': (
                '335',
                '337'),
        }
        commit_ids = commit_id_range[backend.alias]
        commit_id = '%s...%s' % (commit_ids[0], commit_ids[1])
        response = self.app.get(url(
            controller='changeset', action='index',
            repo_name=backend.repo_name, revision=commit_id))

        response.mustcontain(_shorten_commit_id(commit_ids[0]))
        response.mustcontain(_shorten_commit_id(commit_ids[1]))
        response.mustcontain('33 files changed: 1165 inserted, 308 deleted')

        # files op files
        response.mustcontain('File no longer present at commit: %s' %
                             _shorten_commit_id(commit_ids[1]))
        response.mustcontain('new file 100644')
        response.mustcontain('Added docstrings to vcs.cli')  # commit msg
        response.mustcontain('Changed theme to ADC theme')  # commit msg

        self._check_diff_menus(response)

    @pytest.mark.xfail_backends("svn", reason="Depends on consistent diffs")
    def test_combined_compare_commit_page_different_ops(self, backend):
        commit_id_range = {
            'hg': (
                '4fdd71e9427417b2e904e0464c634fdee85ec5a7',
                '603d6c72c46d953420c89d36372f08d9f305f5dd'),
            'git': (
                'f5fbf9cfd5f1f1be146f6d3b38bcd791a7480c13',
                '03fa803d7e9fb14daa9a3089e0d1494eda75d986'),
            'svn': (
                '335',
                '337'),
        }
        commit_ids = commit_id_range[backend.alias]
        response = self.app.get(url(
            controller='compare', action='compare',
            repo_name=backend.repo_name,
            source_ref_type='rev', source_ref=commit_ids[0],
            target_ref_type='rev', target_ref=commit_ids[1], ))

        response.mustcontain(_shorten_commit_id(commit_ids[0]))
        response.mustcontain(_shorten_commit_id(commit_ids[1]))
        response.mustcontain('32 files changed: 1165 inserted, 308 deleted')

        # files op files
        response.mustcontain('File no longer present at commit: %s' %
                             _shorten_commit_id(commit_ids[1]))
        response.mustcontain('new file 100644')
        response.mustcontain('Added docstrings to vcs.cli')  # commit msg
        response.mustcontain('Changed theme to ADC theme')  # commit msg

        self._check_diff_menus(response)

    def test_changeset_range(self, backend):
        self._check_changeset_range(
            backend, self.commit_id_range, self.commit_id_range_result)

    def test_changeset_range_with_initial_commit(self, backend):
        commit_id_range = {
            'hg': (
                'b986218ba1c9b0d6a259fac9b050b1724ed8e545'
                '...6cba7170863a2411822803fa77a0a264f1310b35'),
            'git': (
                'c1214f7e79e02fc37156ff215cd71275450cffc3'
                '...fa6600f6848800641328adbf7811fd2372c02ab2'),
            'svn': '1...3',
        }
        commit_id_range_result = {
            'hg': ['b986218ba1c9', '3d8f361e72ab', '6cba7170863a'],
            'git': ['c1214f7e79e0', '38b5fe81f109', 'fa6600f68488'],
            'svn': ['1', '2', '3'],
        }
        self._check_changeset_range(
            backend, commit_id_range, commit_id_range_result)

    def _check_changeset_range(
            self, backend, commit_id_ranges, commit_id_range_result):
        response = self.app.get(
            url(controller='changeset', action='index',
                repo_name=backend.repo_name,
                revision=commit_id_ranges[backend.alias]))
        expected_result = commit_id_range_result[backend.alias]
        response.mustcontain('{} commits'.format(len(expected_result)))
        for commit_id in expected_result:
            response.mustcontain(commit_id)

    commit_id = {
        'hg': '2062ec7beeeaf9f44a1c25c41479565040b930b2',
        'svn': '393',
        'git': 'fd627b9e0dd80b47be81af07c4a98518244ed2f7',
    }

    commit_id_range = {
        'hg': (
            'a53d9201d4bc278910d416d94941b7ea007ecd52'
            '...2062ec7beeeaf9f44a1c25c41479565040b930b2'),
        'git': (
            '7ab37bc680b4aa72c34d07b230c866c28e9fc204'
            '...fd627b9e0dd80b47be81af07c4a98518244ed2f7'),
        'svn': '391...393',
    }

    commit_id_range_result = {
        'hg': ['a53d9201d4bc', '96507bd11ecc', '2062ec7beeea'],
        'git': ['7ab37bc680b4', '5f2c6ee19592', 'fd627b9e0dd8'],
        'svn': ['391', '392', '393'],
    }

    diffs = {
        'hg': r"""diff --git a/README b/README
new file mode 120000
--- /dev/null
+++ b/README
@@ -0,0 +1,1 @@
+README.rst
\ No newline at end of file
""",
        'git': r"""diff --git a/README b/README
new file mode 120000
index 0000000000000000000000000000000000000000..92cacd285355271487b7e379dba6ca60f9a554a4
--- /dev/null
+++ b/README
@@ -0,0 +1 @@
+README.rst
\ No newline at end of file
""",
        'svn': """Index: README
===================================================================
diff --git a/README b/README
new file mode 10644
--- /dev/null\t(revision 0)
+++ b/README\t(revision 393)
@@ -0,0 +1 @@
+link README.rst
\\ No newline at end of file
""",
    }

    patches = {
        'hg': r"""# HG changeset patch
# User Marcin Kuzminski <marcin@python-works.com>
# Date 2014-01-07 12:21:40
# Node ID 2062ec7beeeaf9f44a1c25c41479565040b930b2
# Parent  96507bd11ecc815ebc6270fdf6db110928c09c1e

Added a symlink

""" + diffs['hg'],
        'git': r"""From fd627b9e0dd80b47be81af07c4a98518244ed2f7 2014-01-07 12:22:20
From: Marcin Kuzminski <marcin@python-works.com>
Date: 2014-01-07 12:22:20
Subject: [PATCH] Added a symlink

---

""" + diffs['git'],
        'svn': r"""# SVN changeset patch
# User marcin
# Date 2014-09-02 12:25:22.071142
# Revision 393

Added a symlink

""" + diffs['svn'],
    }

    def _check_diff_menus(self, response, right_menu=False):
        # diff menus
        for elem in ['Show File', 'Unified Diff', 'Side-by-side Diff',
                     'Raw Diff', 'Download Diff']:
            response.mustcontain(elem)

        # right pane diff menus
        if right_menu:
            for elem in ['Ignore whitespace', 'Increase context',
                         'Hide comments']:
                response.mustcontain(elem)
