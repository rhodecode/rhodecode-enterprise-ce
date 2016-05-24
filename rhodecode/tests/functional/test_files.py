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

import os

import mock
import pytest

from rhodecode.controllers.files import FilesController
from rhodecode.lib import helpers as h
from rhodecode.lib.compat import OrderedDict
from rhodecode.lib.ext_json import json
from rhodecode.lib.vcs import nodes
from rhodecode.lib.vcs.conf import settings
from rhodecode.tests import (
    url, assert_session_flash, assert_not_in_session_flash)
from rhodecode.tests.fixture import Fixture
from rhodecode.tests.utils import AssertResponse

fixture = Fixture()

NODE_HISTORY = {
    'hg': json.loads(fixture.load_resource('hg_node_history_response.json')),
    'git': json.loads(fixture.load_resource('git_node_history_response.json')),
    'svn': json.loads(fixture.load_resource('svn_node_history_response.json')),
}


@pytest.mark.usefixtures("app")
class TestFilesController:

    def test_index(self, backend):
        response = self.app.get(url(
            controller='files', action='index',
            repo_name=backend.repo_name, revision='tip', f_path='/'))
        commit = backend.repo.get_commit()

        params = {
            'repo_name': backend.repo_name,
            'revision': commit.raw_id,
            'date': commit.date
        }
        assert_dirs_in_response(response, ['docs', 'vcs'], params)
        files = [
            '.gitignore',
            '.hgignore',
            '.hgtags',
            # TODO: missing in Git
            # '.travis.yml',
            'MANIFEST.in',
            'README.rst',
            # TODO: File is missing in svn repository
            # 'run_test_and_report.sh',
            'setup.cfg',
            'setup.py',
            'test_and_report.sh',
            'tox.ini',
        ]
        assert_files_in_response(response, files, params)
        assert_timeago_in_response(response, files, params)

    def test_index_links_submodules_with_absolute_url(self, backend_hg):
        repo = backend_hg['subrepos']
        response = self.app.get(url(
            controller='files', action='index',
            repo_name=repo.repo_name, revision='tip', f_path='/'))
        assert_response = AssertResponse(response)
        assert_response.contains_one_link(
            'absolute-path @ 000000000000', 'http://example.com/absolute-path')

    def test_index_links_submodules_with_absolute_url_subpaths(
            self, backend_hg):
        repo = backend_hg['subrepos']
        response = self.app.get(url(
            controller='files', action='index',
            repo_name=repo.repo_name, revision='tip', f_path='/'))
        assert_response = AssertResponse(response)
        assert_response.contains_one_link(
            'subpaths-path @ 000000000000',
            'http://sub-base.example.com/subpaths-path')

    @pytest.mark.xfail_backends("svn", reason="Depends on branch support")
    def test_files_menu(self, backend):
        new_branch = "temp_branch_name"
        commits = [
            {'message': 'a'},
            {'message': 'b', 'branch': new_branch}
        ]
        backend.create_repo(commits)

        backend.repo.landing_rev = "branch:%s" % new_branch

        # get response based on tip and not new revision
        response = self.app.get(url(
            controller='files', action='index',
            repo_name=backend.repo_name, revision='tip', f_path='/'),
            status=200)

        # make sure Files menu url is not tip but new revision
        landing_rev = backend.repo.landing_rev[1]
        files_url = url('files_home', repo_name=backend.repo_name,
                        revision=landing_rev)

        assert landing_rev != 'tip'
        response.mustcontain('<li class="active"><a class="menulink" href="%s">' % files_url)

    def test_index_commit(self, backend):
        commit = backend.repo.get_commit(commit_idx=32)

        response = self.app.get(url(
            controller='files', action='index',
            repo_name=backend.repo_name,
            revision=commit.raw_id,
            f_path='/')
        )

        dirs = ['docs', 'tests']
        files = ['README.rst']
        params = {
            'repo_name': backend.repo_name,
            'revision': commit.raw_id,
        }
        assert_dirs_in_response(response, dirs, params)
        assert_files_in_response(response, files, params)

    @pytest.mark.xfail_backends("git", reason="Missing branches in git repo")
    @pytest.mark.xfail_backends("svn", reason="Depends on branch support")
    def test_index_different_branch(self, backend):
        # TODO: Git test repository does not contain branches
        # TODO: Branch support in Subversion

        commit = backend.repo.get_commit(commit_idx=150)
        response = self.app.get(url(
            controller='files', action='index',
            repo_name=backend.repo_name,
            revision=commit.raw_id,
            f_path='/'))
        assert_response = AssertResponse(response)
        assert_response.element_contains(
            '.tags .branchtag', 'git')

    def test_index_paging(self, backend):
        repo = backend.repo
        indexes = [73, 92, 109, 1, 0]
        idx_map = [(rev, repo.get_commit(commit_idx=rev).raw_id)
                   for rev in indexes]

        for idx in idx_map:
            response = self.app.get(url(
                controller='files', action='index',
                repo_name=backend.repo_name,
                revision=idx[1],
                f_path='/'))

            response.mustcontain("""r%s:%s""" % (idx[0], idx[1][:8]))

    def test_file_source(self, backend):
        commit = backend.repo.get_commit(commit_idx=167)
        response = self.app.get(url(
            controller='files', action='index',
            repo_name=backend.repo_name,
            revision=commit.raw_id,
            f_path='vcs/nodes.py'))

        msgbox = """<div class="commit right-content">%s</div>"""
        response.mustcontain(msgbox % (commit.message, ))

        assert_response = AssertResponse(response)
        if commit.branch:
            assert_response.element_contains('.tags.tags-main .branchtag', commit.branch)
        if commit.tags:
            for tag in commit.tags:
                assert_response.element_contains('.tags.tags-main .tagtag', tag)

    def test_file_source_history(self, backend):
        response = self.app.get(
            url(
                controller='files', action='history',
                repo_name=backend.repo_name,
                revision='tip',
                f_path='vcs/nodes.py'),
            extra_environ={'HTTP_X_PARTIAL_XHR': '1'})
        assert NODE_HISTORY[backend.alias] == json.loads(response.body)

    def test_file_source_history_svn(self, backend_svn):
        simple_repo = backend_svn['svn-simple-layout']
        response = self.app.get(
            url(
                controller='files', action='history',
                repo_name=simple_repo.repo_name,
                revision='tip',
                f_path='trunk/example.py'),
            extra_environ={'HTTP_X_PARTIAL_XHR': '1'})

        expected_data = json.loads(
            fixture.load_resource('svn_node_history_branches.json'))
        assert expected_data == response.json

    def test_file_annotation_history(self, backend):
        response = self.app.get(
            url(
                controller='files', action='history',
                repo_name=backend.repo_name,
                revision='tip',
                f_path='vcs/nodes.py',
                annotate=True),
            extra_environ={'HTTP_X_PARTIAL_XHR': '1'})
        assert NODE_HISTORY[backend.alias] == json.loads(response.body)

    def test_file_annotation(self, backend):
        response = self.app.get(url(
            controller='files', action='index',
            repo_name=backend.repo_name, revision='tip', f_path='vcs/nodes.py',
            annotate=True))

        expected_revisions = {
            'hg': 'r356:25213a5fbb04',
            'git': 'r345:c994f0de03b2',
            'svn': 'r208:209',
        }
        response.mustcontain(expected_revisions[backend.alias])

    def test_file_authors(self, backend):
        response = self.app.get(url(
            controller='files', action='authors',
            repo_name=backend.repo_name,
            revision='tip',
            f_path='vcs/nodes.py',
            annotate=True))

        expected_authors = {
            'hg': ('Marcin Kuzminski', 'Lukasz Balcerzak'),
            'git': ('Marcin Kuzminski', 'Lukasz Balcerzak'),
            'svn': ('marcin', 'lukasz'),
        }

        for author in expected_authors[backend.alias]:
            response.mustcontain(author)

    def test_tree_search_top_level(self, backend, xhr_header):
        commit = backend.repo.get_commit(commit_idx=173)
        response = self.app.get(
            url('files_nodelist_home', repo_name=backend.repo_name,
                revision=commit.raw_id, f_path='/'),
            extra_environ=xhr_header)
        assert 'nodes' in response.json
        assert {'name': 'docs', 'type': 'dir'} in response.json['nodes']

    def test_tree_search_at_path(self, backend, xhr_header):
        commit = backend.repo.get_commit(commit_idx=173)
        response = self.app.get(
            url('files_nodelist_home', repo_name=backend.repo_name,
                revision=commit.raw_id, f_path='/docs'),
            extra_environ=xhr_header)
        assert 'nodes' in response.json
        nodes = response.json['nodes']
        assert {'name': 'docs/api', 'type': 'dir'} in nodes
        assert {'name': 'docs/index.rst', 'type': 'file'} in nodes

    def test_tree_search_at_path_missing_xhr(self, backend):
        self.app.get(
            url('files_nodelist_home', repo_name=backend.repo_name,
                revision='tip', f_path=''), status=400)

    def test_tree_view_list(self, backend, xhr_header):
        commit = backend.repo.get_commit(commit_idx=173)
        response = self.app.get(
            url('files_nodelist_home', repo_name=backend.repo_name,
                f_path='/', revision=commit.raw_id),
            extra_environ=xhr_header,
        )
        response.mustcontain("vcs/web/simplevcs/views/repository.py")

    def test_tree_view_list_at_path(self, backend, xhr_header):
        commit = backend.repo.get_commit(commit_idx=173)
        response = self.app.get(
            url('files_nodelist_home', repo_name=backend.repo_name,
                f_path='/docs', revision=commit.raw_id),
            extra_environ=xhr_header,
        )
        response.mustcontain("docs/index.rst")

    def test_tree_view_list_missing_xhr(self, backend):
        self.app.get(
            url('files_nodelist_home', repo_name=backend.repo_name,
                f_path='/', revision='tip'), status=400)

    def test_tree_metadata_list_success(self, backend, xhr_header):
        commit = backend.repo.get_commit(commit_idx=173)
        response = self.app.get(
            url('files_metadata_list_home', repo_name=backend.repo_name,
                f_path='/', revision=commit.raw_id),
            extra_environ=xhr_header)

        expected_keys = ['author', 'message', 'modified_at', 'modified_ts',
                         'name', 'revision', 'short_id', 'size']
        for filename in response.json.get('metadata'):
            for key in expected_keys:
                assert key in filename

    def test_tree_metadata_list_if_file(self, backend, xhr_header):
        commit = backend.repo.get_commit(commit_idx=173)
        response = self.app.get(
            url('files_metadata_list_home', repo_name=backend.repo_name,
                f_path='README.rst', revision=commit.raw_id),
            extra_environ=xhr_header)
        assert response.json == {'metadata': []}

    def test_tree_metadata_list_missing_xhr(self, backend):
        self.app.get(
            url('files_metadata_list_home', repo_name=backend.repo_name,
                f_path='/', revision='tip'), status=400)

    def test_access_empty_repo_redirect_to_summary_with_alert_write_perms(
            self, app, backend_stub, autologin_regular_user, user_regular,
            user_util):
        repo = backend_stub.create_repo()
        user_util.grant_user_permission_to_repo(
            repo, user_regular, 'repository.write')
        response = self.app.get(url(
            controller='files', action='index',
            repo_name=repo.repo_name, revision='tip', f_path='/'))
        assert_session_flash(
            response,
            'There are no files yet. <a class="alert-link" '
            'href="/%s/add/0/#edit">Click here to add a new file.</a>'
            % (repo.repo_name))

    def test_access_empty_repo_redirect_to_summary_with_alert_no_write_perms(
            self, backend_stub, user_util):
        repo = backend_stub.create_repo()
        repo_file_url = url(
            'files_add_home',
            repo_name=repo.repo_name,
            revision=0, f_path='', anchor='edit')
        response = self.app.get(url(
            controller='files', action='index',
            repo_name=repo.repo_name, revision='tip', f_path='/'))
        assert_not_in_session_flash(response, repo_file_url)


# TODO: johbo: Think about a better place for these tests. Either controller
# specific unit tests or we move down the whole logic further towards the vcs
# layer
class TestAdjustFilePathForSvn:
    """SVN specific adjustments of node history in FileController."""

    def test_returns_path_relative_to_matched_reference(self):
        repo = self._repo(branches=['trunk'])
        self.assert_file_adjustment('trunk/file', 'file', repo)

    def test_does_not_modify_file_if_no_reference_matches(self):
        repo = self._repo(branches=['trunk'])
        self.assert_file_adjustment('notes/file', 'notes/file', repo)

    def test_does_not_adjust_partial_directory_names(self):
        repo = self._repo(branches=['trun'])
        self.assert_file_adjustment('trunk/file', 'trunk/file', repo)

    def test_is_robust_to_patterns_which_prefix_other_patterns(self):
        repo = self._repo(branches=['trunk', 'trunk/new', 'trunk/old'])
        self.assert_file_adjustment('trunk/new/file', 'file', repo)

    def assert_file_adjustment(self, f_path, expected, repo):
        controller = FilesController()
        result = controller._adjust_file_path_for_svn(f_path, repo)
        assert result == expected

    def _repo(self, branches=None):
        repo = mock.Mock()
        repo.branches = OrderedDict((name, '0') for name in branches or [])
        repo.tags = {}
        return repo


@pytest.mark.usefixtures("app")
class TestRepositoryArchival:

    def test_archival(self, backend):
        backend.enable_downloads()
        commit = backend.repo.get_commit(commit_idx=173)
        for archive, info in settings.ARCHIVE_SPECS.items():
            mime_type, arch_ext = info
            short = commit.short_id + arch_ext
            fname = commit.raw_id + arch_ext
            filename = '%s-%s' % (backend.repo_name, short)
            response = self.app.get(url(controller='files',
                                        action='archivefile',
                                        repo_name=backend.repo_name,
                                        fname=fname))

            assert response.status == '200 OK'
            headers = {
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'Content-Disposition': 'attachment; filename=%s' % filename,
                'Content-Type': '%s; charset=utf-8' % mime_type,
            }
            if 'Set-Cookie' in response.response.headers:
                del response.response.headers['Set-Cookie']
            assert response.response.headers == headers

    def test_archival_wrong_ext(self, backend):
        backend.enable_downloads()
        commit = backend.repo.get_commit(commit_idx=173)
        for arch_ext in ['tar', 'rar', 'x', '..ax', '.zipz']:
            fname = commit.raw_id + arch_ext

            response = self.app.get(url(controller='files',
                                        action='archivefile',
                                        repo_name=backend.repo_name,
                                        fname=fname))
            response.mustcontain('Unknown archive type')

    def test_archival_wrong_commit_id(self, backend):
        backend.enable_downloads()
        for commit_id in ['00x000000', 'tar', 'wrong', '@##$@$42413232',
                          '232dffcd']:
            fname = '%s.zip' % commit_id

            response = self.app.get(url(controller='files',
                                        action='archivefile',
                                        repo_name=backend.repo_name,
                                        fname=fname))
            response.mustcontain('Unknown revision')


@pytest.mark.usefixtures("app", "autologin_user")
class TestRawFileHandling:

    def test_raw_file_ok(self, backend):
        commit = backend.repo.get_commit(commit_idx=173)
        response = self.app.get(url(controller='files', action='rawfile',
                                    repo_name=backend.repo_name,
                                    revision=commit.raw_id,
                                    f_path='vcs/nodes.py'))

        assert response.content_disposition == "attachment; filename=nodes.py"
        assert response.content_type == "text/x-python"

    def test_raw_file_wrong_cs(self, backend):
        commit_id = u'ERRORce30c96924232dffcd24178a07ffeb5dfc'
        f_path = 'vcs/nodes.py'

        response = self.app.get(url(controller='files', action='rawfile',
                                    repo_name=backend.repo_name,
                                    revision=commit_id,
                                    f_path=f_path), status=404)

        msg = """No such commit exists for this repository"""
        response.mustcontain(msg)

    def test_raw_file_wrong_f_path(self, backend):
        commit = backend.repo.get_commit(commit_idx=173)
        f_path = 'vcs/ERRORnodes.py'
        response = self.app.get(url(controller='files', action='rawfile',
                                    repo_name=backend.repo_name,
                                    revision=commit.raw_id,
                                    f_path=f_path), status=404)

        msg = (
            "There is no file nor directory at the given path: "
            "&#39;%s&#39; at commit %s" % (f_path, commit.short_id))
        response.mustcontain(msg)

    def test_raw_ok(self, backend):
        commit = backend.repo.get_commit(commit_idx=173)
        response = self.app.get(url(controller='files', action='raw',
                                    repo_name=backend.repo_name,
                                    revision=commit.raw_id,
                                    f_path='vcs/nodes.py'))

        assert response.content_type == "text/plain"

    def test_raw_wrong_cs(self, backend):
        commit_id = u'ERRORcce30c96924232dffcd24178a07ffeb5dfc'
        f_path = 'vcs/nodes.py'

        response = self.app.get(url(controller='files', action='raw',
                                    repo_name=backend.repo_name,
                                    revision=commit_id,
                                    f_path=f_path), status=404)

        msg = """No such commit exists for this repository"""
        response.mustcontain(msg)

    def test_raw_wrong_f_path(self, backend):
        commit = backend.repo.get_commit(commit_idx=173)
        f_path = 'vcs/ERRORnodes.py'
        response = self.app.get(url(controller='files', action='raw',
                                    repo_name=backend.repo_name,
                                    revision=commit.raw_id,
                                    f_path=f_path), status=404)
        msg = (
            "There is no file nor directory at the given path: "
            "&#39;%s&#39; at commit %s" % (f_path, commit.short_id))
        response.mustcontain(msg)

    def test_raw_svg_should_not_be_rendered(self, backend):
        backend.create_repo()
        backend.ensure_file("xss.svg")
        response = self.app.get(url(controller='files', action='raw',
                                    repo_name=backend.repo_name,
                                    revision='tip',
                                    f_path='xss.svg'))

        # If the content type is image/svg+xml then it allows to render HTML
        # and malicious SVG.
        assert response.content_type == "text/plain"


@pytest.mark.usefixtures("app")
class TestFilesDiff:

    @pytest.mark.parametrize("diff", ['diff', 'download', 'raw'])
    def test_file_full_diff(self, backend, diff):
        commit1 = backend.repo.get_commit(commit_idx=-1)
        commit2 = backend.repo.get_commit(commit_idx=-2)
        response = self.app.get(
            url(
                controller='files',
                action='diff',
                repo_name=backend.repo_name,
                f_path='README'),
            params={
                'diff1': commit1.raw_id,
                'diff2': commit2.raw_id,
                'fulldiff': '1',
                'diff': diff,
            })
        response.mustcontain('README.rst')
        response.mustcontain('No newline at end of file')

    def test_file_binary_diff(self, backend):
        commits = [
            {'message': 'First commit'},
            {'message': 'Commit with binary',
             'added': [nodes.FileNode('file.bin', content='\0BINARY\0')]},
        ]
        repo = backend.create_repo(commits=commits)

        response = self.app.get(
            url(
                controller='files',
                action='diff',
                repo_name=backend.repo_name,
                f_path='file.bin'),
            params={
                'diff1': repo.get_commit(commit_idx=0).raw_id,
                'diff2': repo.get_commit(commit_idx=1).raw_id,
                'fulldiff': '1',
                'diff': 'diff',
            })
        response.mustcontain('Cannot diff binary files')

    def test_diff_2way(self, backend):
        commit1 = backend.repo.get_commit(commit_idx=-1)
        commit2 = backend.repo.get_commit(commit_idx=-2)
        response = self.app.get(
            url(
                controller='files',
                action='diff_2way',
                repo_name=backend.repo_name,
                f_path='README'),
            params={
                'diff1': commit1.raw_id,
                'diff2': commit2.raw_id,
            })

        # Expecting links to both variants of the file. Links are used
        # to load the content dynamically.
        response.mustcontain('/%s/README' % commit1.raw_id)
        response.mustcontain('/%s/README' % commit2.raw_id)

    def test_requires_one_commit_id(self, backend, autologin_user):
        response = self.app.get(
            url(
                controller='files',
                action='diff',
                repo_name=backend.repo_name,
                f_path='README.rst'),
            status=400)
        response.mustcontain(
            'Need query parameter', 'diff1', 'diff2', 'to generate a diff.')

    def test_returns_not_found_if_file_does_not_exist(self, vcsbackend):
        repo = vcsbackend.repo
        self.app.get(
            url(
                controller='files',
                action='diff',
                repo_name=repo.name,
                f_path='does-not-exist-in-any-commit',
                diff1=repo[0].raw_id,
                diff2=repo[1].raw_id),
            status=404)

    def test_returns_redirect_if_file_not_changed(self, backend):
        commit = backend.repo.get_commit(commit_idx=-1)
        f_path= 'README'
        response = self.app.get(
            url(
                controller='files',
                action='diff_2way',
                repo_name=backend.repo_name,
                f_path=f_path,
                diff1=commit.raw_id,
                diff2=commit.raw_id,
            ),
            status=302
        )
        assert response.headers['Location'].endswith(f_path)
        redirected = response.follow()
        redirected.mustcontain('has not changed between')

    def test_supports_diff_to_different_path_svn(self, backend_svn):
        repo = backend_svn['svn-simple-layout'].scm_instance()
        commit_id = repo[-1].raw_id
        response = self.app.get(
            url(
                controller='files',
                action='diff',
                repo_name=repo.name,
                f_path='trunk/example.py',
                diff1='tags/v0.2/example.py@' + commit_id,
                diff2=commit_id),
            status=200)
        response.mustcontain(
            "Will print out a useful message on invocation.")

        # Note: Expecting that we indicate the user what's being compared
        response.mustcontain("trunk/example.py")
        response.mustcontain("tags/v0.2/example.py")

    def test_show_rev_redirects_to_svn_path(self, backend_svn):
        repo = backend_svn['svn-simple-layout'].scm_instance()
        commit_id = repo[-1].raw_id
        response = self.app.get(
            url(
                controller='files',
                action='diff',
                repo_name=repo.name,
                f_path='trunk/example.py',
                diff1='branches/argparse/example.py@' + commit_id,
                diff2=commit_id),
            params={'show_rev': 'Show at Revision'},
            status=302)
        assert response.headers['Location'].endswith(
            'svn-svn-simple-layout/files/26/branches/argparse/example.py')

    def test_show_rev_and_annotate_redirects_to_svn_path(self, backend_svn):
        repo = backend_svn['svn-simple-layout'].scm_instance()
        commit_id = repo[-1].raw_id
        response = self.app.get(
            url(
                controller='files',
                action='diff',
                repo_name=repo.name,
                f_path='trunk/example.py',
                diff1='branches/argparse/example.py@' + commit_id,
                diff2=commit_id),
            params={
                'show_rev': 'Show at Revision',
                'annotate': 'true',
            },
            status=302)
        assert response.headers['Location'].endswith(
            'svn-svn-simple-layout/annotate/26/branches/argparse/example.py')


@pytest.mark.usefixtures("app", "autologin_user")
class TestChangingFiles:

    def test_add_file_view(self, backend):
        self.app.get(url(
            'files_add_home',
            repo_name=backend.repo_name,
            revision='tip', f_path='/'))

    @pytest.mark.xfail_backends("svn", reason="Depends on online editing")
    def test_add_file_into_repo_missing_content(self, backend, csrf_token):
        repo = backend.create_repo()
        filename = 'init.py'
        response = self.app.post(
            url(
                'files_add',
                repo_name=repo.repo_name,
                revision='tip', f_path='/'),
            params={
                'content': "",
                'filename': filename,
                'location': "",
                'csrf_token': csrf_token,
            },
            status=302)
        assert_session_flash(
            response, 'Successfully committed to %s'
            % os.path.join(filename))

    def test_add_file_into_repo_missing_filename(self, backend, csrf_token):
        response = self.app.post(
            url(
                'files_add',
                repo_name=backend.repo_name,
                revision='tip', f_path='/'),
            params={
                'content': "foo",
                'csrf_token': csrf_token,
            },
            status=302)

        assert_session_flash(response, 'No filename')

    def test_add_file_into_repo_errors_and_no_commits(
            self, backend, csrf_token):
        repo = backend.create_repo()
        # Create a file with no filename, it will display an error but
        # the repo has no commits yet
        response = self.app.post(
            url(
                'files_add',
                repo_name=repo.repo_name,
                revision='tip', f_path='/'),
            params={
                'content': "foo",
                'csrf_token': csrf_token,
            },
            status=302)

        assert_session_flash(response, 'No filename')

        # Not allowed, redirect to the summary
        redirected = response.follow()
        summary_url = url('summary_home', repo_name=repo.repo_name)

        # As there are no commits, displays the summary page with the error of
        # creating a file with no filename
        assert redirected.req.path == summary_url

    @pytest.mark.parametrize("location, filename", [
        ('/abs', 'foo'),
        ('../rel', 'foo'),
        ('file/../foo', 'foo'),
    ])
    def test_add_file_into_repo_bad_filenames(
            self, location, filename, backend, csrf_token):
        response = self.app.post(
            url(
                'files_add',
                repo_name=backend.repo_name,
                revision='tip', f_path='/'),
            params={
                'content': "foo",
                'filename': filename,
                'location': location,
                'csrf_token': csrf_token,
            },
            status=302)

        assert_session_flash(
            response,
            'The location specified must be a relative path and must not '
            'contain .. in the path')

    @pytest.mark.parametrize("cnt, location, filename", [
        (1, '', 'foo.txt'),
        (2, 'dir', 'foo.rst'),
        (3, 'rel/dir', 'foo.bar'),
    ])
    def test_add_file_into_repo(self, cnt, location, filename, backend,
                                csrf_token):
        repo = backend.create_repo()
        response = self.app.post(
            url(
                'files_add',
                repo_name=repo.repo_name,
                revision='tip', f_path='/'),
            params={
                'content': "foo",
                'filename': filename,
                'location': location,
                'csrf_token': csrf_token,
            },
            status=302)
        assert_session_flash(
            response, 'Successfully committed to %s'
            % os.path.join(location, filename))

    def test_edit_file_view(self, backend):
        response = self.app.get(
            url(
                'files_edit_home',
                repo_name=backend.repo_name,
                revision=backend.default_head_id,
                f_path='vcs/nodes.py'),
            status=200)
        response.mustcontain("Module holding everything related to vcs nodes.")

    def test_edit_file_view_not_on_branch(self, backend):
        repo = backend.create_repo()
        backend.ensure_file("vcs/nodes.py")

        response = self.app.get(
            url(
                'files_edit_home',
                repo_name=repo.repo_name,
                revision='tip', f_path='vcs/nodes.py'),
            status=302)
        assert_session_flash(
            response,
            'You can only edit files with revision being a valid branch')

    def test_edit_file_view_commit_changes(self, backend, csrf_token):
        repo = backend.create_repo()
        backend.ensure_file("vcs/nodes.py", content="print 'hello'")

        response = self.app.post(
            url(
                'files_edit',
                repo_name=repo.repo_name,
                revision=backend.default_head_id,
                f_path='vcs/nodes.py'),
            params={
                'content': "print 'hello world'",
                'message': 'I committed',
                'filename': "vcs/nodes.py",
                'csrf_token': csrf_token,
            },
            status=302)
        assert_session_flash(
            response, 'Successfully committed to vcs/nodes.py')
        tip = repo.get_commit(commit_idx=-1)
        assert tip.message == 'I committed'

    def test_edit_file_view_commit_changes_default_message(self, backend,
                                                           csrf_token):
        repo = backend.create_repo()
        backend.ensure_file("vcs/nodes.py", content="print 'hello'")

        commit_id = (
            backend.default_branch_name or
            backend.repo.scm_instance().commit_ids[-1])

        response = self.app.post(
            url(
                'files_edit',
                repo_name=repo.repo_name,
                revision=commit_id,
                f_path='vcs/nodes.py'),
            params={
                'content': "print 'hello world'",
                'message': '',
                'filename': "vcs/nodes.py",
                'csrf_token': csrf_token,
            },
            status=302)
        assert_session_flash(
            response, 'Successfully committed to vcs/nodes.py')
        tip = repo.get_commit(commit_idx=-1)
        assert tip.message == 'Edited file vcs/nodes.py via RhodeCode Enterprise'

    def test_delete_file_view(self, backend):
        self.app.get(url(
            'files_delete_home',
            repo_name=backend.repo_name,
            revision='tip', f_path='vcs/nodes.py'))

    def test_delete_file_view_not_on_branch(self, backend):
        repo = backend.create_repo()
        backend.ensure_file('vcs/nodes.py')

        response = self.app.get(
            url(
                'files_delete_home',
                repo_name=repo.repo_name,
                revision='tip', f_path='vcs/nodes.py'),
            status=302)
        assert_session_flash(
            response,
            'You can only delete files with revision being a valid branch')

    def test_delete_file_view_commit_changes(self, backend, csrf_token):
        repo = backend.create_repo()
        backend.ensure_file("vcs/nodes.py")

        response = self.app.post(
            url(
                'files_delete_home',
                repo_name=repo.repo_name,
                revision=backend.default_head_id,
                f_path='vcs/nodes.py'),
            params={
                'message': 'i commited',
                'csrf_token': csrf_token,
            },
            status=302)
        assert_session_flash(
            response, 'Successfully deleted file vcs/nodes.py')


def assert_files_in_response(response, files, params):
    template = (
        "href='/%(repo_name)s/files/%(revision)s/%(name)s'")
    _assert_items_in_response(response, files, template, params)


def assert_dirs_in_response(response, dirs, params):
    template = (
        "href='/%(repo_name)s/files/%(revision)s/%(name)s'")
    _assert_items_in_response(response, dirs, template, params)


def _assert_items_in_response(response, items, template, params):
    for item in items:
        item_params = {'name': item}
        item_params.update(params)
        response.mustcontain(template % item_params)


def assert_timeago_in_response(response, items, params):
    for item in items:
        response.mustcontain(h.age_component(params['date']))
