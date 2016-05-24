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

import mock
import pytest

from rhodecode.lib.vcs.backends.base import EmptyCommit
from rhodecode.lib.vcs.exceptions import RepositoryRequirementError
from rhodecode.model.db import Repository
from rhodecode.model.scm import ScmModel
from rhodecode.tests import url, TEST_USER_ADMIN_LOGIN, assert_session_flash
from rhodecode.tests.utils import AssertResponse


@pytest.mark.usefixtures("autologin_user", "app")
class TestCompareController:

    @pytest.mark.xfail_backends("svn", "git")
    def test_compare_remote_with_different_commit_indexes(self, backend):
        # Preparing the following repository structure:
        #
        # Origin repository has two commits:
        #
        #    0    1
        #    A -- D
        #
        # The fork of it has a few more commits and "D" has a commit index
        # which does not exist in origin.
        #
        #    0    1    2    3    4
        #    A --   --   -- D -- E
        #      \- B -- C
        #

        fork = backend.create_repo()

        # prepare fork
        commit0 = _commit_change(
            fork.repo_name, filename='file1', content='A',
            message='A', vcs_type=backend.alias, parent=None, newfile=True)

        commit1 = _commit_change(
            fork.repo_name, filename='file1', content='B',
            message='B, child of A', vcs_type=backend.alias, parent=commit0)

        _commit_change(  # commit 2
            fork.repo_name, filename='file1', content='C',
            message='C, child of B', vcs_type=backend.alias, parent=commit1)

        commit3 = _commit_change(
            fork.repo_name, filename='file1', content='D',
            message='D, child of A', vcs_type=backend.alias, parent=commit0)

        commit4 = _commit_change(
            fork.repo_name, filename='file1', content='E',
            message='E, child of D', vcs_type=backend.alias, parent=commit3)

        # prepare origin repository, taking just the history up to D
        origin = backend.create_repo()

        origin_repo = origin.scm_instance(cache=False)
        origin_repo.config.clear_section('hooks')
        origin_repo.pull(fork.repo_full_path, commit_ids=[commit3.raw_id])

        # Verify test fixture setup
        assert 5 == len(fork.scm_instance().commit_ids)
        assert 2 == len(origin_repo.commit_ids)

        # Comparing the revisions
        response = self.app.get(
            url('compare_url',
                repo_name=origin.repo_name,
                source_ref_type="rev",
                source_ref=commit3.raw_id,
                target_repo=fork.repo_name,
                target_ref_type="rev",
                target_ref=commit4.raw_id,
                merge='1',))

        compare_page = ComparePage(response)
        compare_page.contains_commits([commit4])

    @pytest.mark.xfail_backends("svn", reason="Depends on branch support")
    def test_compare_forks_on_branch_extra_commits(self, backend):
        repo1 = backend.create_repo()

        # commit something !
        commit0 = _commit_change(
            repo1.repo_name, filename='file1', content='line1\n',
            message='commit1', vcs_type=backend.alias, parent=None,
            newfile=True)

        # fork this repo
        repo2 = backend.create_fork()

        # add two extra commit into fork
        commit1 = _commit_change(
            repo2.repo_name, filename='file1', content='line1\nline2\n',
            message='commit2', vcs_type=backend.alias, parent=commit0)

        commit2 = _commit_change(
            repo2.repo_name, filename='file1', content='line1\nline2\nline3\n',
            message='commit3', vcs_type=backend.alias, parent=commit1)

        commit_id1 = repo1.scm_instance().DEFAULT_BRANCH_NAME
        commit_id2 = repo2.scm_instance().DEFAULT_BRANCH_NAME

        response = self.app.get(
            url('compare_url',
                repo_name=repo1.repo_name,
                source_ref_type="branch",
                source_ref=commit_id2,
                target_repo=repo2.repo_name,
                target_ref_type="branch",
                target_ref=commit_id1,
                merge='1',))

        response.mustcontain('%s@%s' % (repo1.repo_name, commit_id2))
        response.mustcontain('%s@%s' % (repo2.repo_name, commit_id1))

        compare_page = ComparePage(response)
        compare_page.contains_change_summary(1, 2, 0)
        compare_page.contains_commits([commit1, commit2])
        compare_page.contains_file_links_and_anchors([
            ('file1', 'a_c--826e8142e6ba'),
        ])

        # Swap is removed when comparing branches since it's a PR feature and
        # it is then a preview mode
        compare_page.swap_is_hidden()
        compare_page.target_source_are_disabled()

    @pytest.mark.xfail_backends("svn", reason="Depends on branch support")
    def test_compare_forks_on_branch_extra_commits_origin_has_incomming(
            self, backend):
        repo1 = backend.create_repo()

        # commit something !
        commit0 = _commit_change(
            repo1.repo_name, filename='file1', content='line1\n',
            message='commit1', vcs_type=backend.alias, parent=None,
            newfile=True)

        # fork this repo
        repo2 = backend.create_fork()

        # now commit something to origin repo
        _commit_change(
            repo1.repo_name, filename='file2', content='line1file2\n',
            message='commit2', vcs_type=backend.alias, parent=commit0,
            newfile=True)

        # add two extra commit into fork
        commit1 = _commit_change(
            repo2.repo_name, filename='file1', content='line1\nline2\n',
            message='commit2', vcs_type=backend.alias, parent=commit0)

        commit2 = _commit_change(
            repo2.repo_name, filename='file1', content='line1\nline2\nline3\n',
            message='commit3', vcs_type=backend.alias, parent=commit1)

        commit_id1 = repo1.scm_instance().DEFAULT_BRANCH_NAME
        commit_id2 = repo2.scm_instance().DEFAULT_BRANCH_NAME

        response = self.app.get(
            url('compare_url',
                repo_name=repo1.repo_name,
                source_ref_type="branch",
                source_ref=commit_id2,
                target_repo=repo2.repo_name,
                target_ref_type="branch",
                target_ref=commit_id1,
                merge='1'))

        response.mustcontain('%s@%s' % (repo1.repo_name, commit_id2))
        response.mustcontain('%s@%s' % (repo2.repo_name, commit_id1))

        compare_page = ComparePage(response)
        compare_page.contains_change_summary(1, 2, 0)
        compare_page.contains_commits([commit1, commit2])
        compare_page.contains_file_links_and_anchors([
            ('file1', 'a_c--826e8142e6ba'),
        ])

        # Swap is removed when comparing branches since it's a PR feature and
        # it is then a preview mode
        compare_page.swap_is_hidden()
        compare_page.target_source_are_disabled()

    @pytest.mark.xfail_backends("svn", "git")
    def test_compare_of_unrelated_forks(self, backend):
        # TODO: johbo: Fails for git due to some other issue it seems
        orig = backend.create_repo(number_of_commits=1)
        fork = backend.create_repo(number_of_commits=1)

        response = self.app.get(
            url('compare_url',
                repo_name=orig.repo_name,
                action="compare",
                source_ref_type="rev",
                source_ref="tip",
                target_ref_type="rev",
                target_ref="tip",
                merge='1',
                target_repo=fork.repo_name),
            status=400)

        response.mustcontain("Repositories unrelated.")

    @pytest.mark.xfail_backends("svn", "git")
    def test_compare_cherry_pick_commits_from_bottom(self, backend):

        # repo1:
        #     commit0:
        #     commit1:
        # repo1-fork- in which we will cherry pick bottom commits
        #     commit0:
        #     commit1:
        #     commit2: x
        #     commit3: x
        #     commit4: x
        #     commit5:
        # make repo1, and commit1+commit2

        repo1 = backend.create_repo()

        # commit something !
        commit0 = _commit_change(
            repo1.repo_name, filename='file1', content='line1\n',
            message='commit1', vcs_type=backend.alias, parent=None,
            newfile=True)
        commit1 = _commit_change(
            repo1.repo_name, filename='file1', content='line1\nline2\n',
            message='commit2', vcs_type=backend.alias, parent=commit0)

        # fork this repo
        repo2 = backend.create_fork()

        # now make commit3-6
        commit2 = _commit_change(
            repo1.repo_name, filename='file1', content='line1\nline2\nline3\n',
            message='commit3', vcs_type=backend.alias, parent=commit1)
        commit3 = _commit_change(
            repo1.repo_name, filename='file1',
            content='line1\nline2\nline3\nline4\n', message='commit4',
            vcs_type=backend.alias, parent=commit2)
        commit4 = _commit_change(
            repo1.repo_name, filename='file1',
            content='line1\nline2\nline3\nline4\nline5\n', message='commit5',
            vcs_type=backend.alias, parent=commit3)
        _commit_change(  # commit 5
            repo1.repo_name, filename='file1',
            content='line1\nline2\nline3\nline4\nline5\nline6\n',
            message='commit6', vcs_type=backend.alias, parent=commit4)

        response = self.app.get(
            url('compare_url',
                repo_name=repo2.repo_name,
                source_ref_type="rev",
                # parent of commit2, in target repo2
                source_ref=commit1.short_id,
                target_repo=repo1.repo_name,
                target_ref_type="rev",
                target_ref=commit4.short_id,
                merge='1',))
        response.mustcontain('%s@%s' % (repo2.repo_name, commit1.short_id))
        response.mustcontain('%s@%s' % (repo1.repo_name, commit4.short_id))

        # files
        compare_page = ComparePage(response)
        compare_page.contains_change_summary(1, 3, 0)
        compare_page.contains_commits([commit2, commit3, commit4])
        compare_page.contains_file_links_and_anchors([
            ('file1', 'a_c--826e8142e6ba'),
        ])

    @pytest.mark.xfail_backends("svn", "git")
    def test_compare_cherry_pick_commits_from_top(self, backend):
        # repo1:
        #     commit0:
        #     commit1:
        # repo1-fork- in which we will cherry pick bottom commits
        #     commit0:
        #     commit1:
        #     commit2:
        #     commit3: x
        #     commit4: x
        #     commit5: x

        # make repo1, and commit1+commit2
        repo1 = backend.create_repo()

        # commit something !
        commit0 = _commit_change(
            repo1.repo_name, filename='file1', content='line1\n',
            message='commit1', vcs_type=backend.alias, parent=None,
            newfile=True)
        commit1 = _commit_change(
            repo1.repo_name, filename='file1', content='line1\nline2\n',
            message='commit2', vcs_type=backend.alias, parent=commit0)

        # fork this repo
        backend.create_fork()

        # now make commit3-6
        commit2 = _commit_change(
            repo1.repo_name, filename='file1', content='line1\nline2\nline3\n',
            message='commit3', vcs_type=backend.alias, parent=commit1)
        commit3 = _commit_change(
            repo1.repo_name, filename='file1',
            content='line1\nline2\nline3\nline4\n', message='commit4',
            vcs_type=backend.alias, parent=commit2)
        commit4 = _commit_change(
            repo1.repo_name, filename='file1',
            content='line1\nline2\nline3\nline4\nline5\n', message='commit5',
            vcs_type=backend.alias, parent=commit3)
        commit5 = _commit_change(
            repo1.repo_name, filename='file1',
            content='line1\nline2\nline3\nline4\nline5\nline6\n',
            message='commit6', vcs_type=backend.alias, parent=commit4)

        response = self.app.get(
            url('compare_url',
                repo_name=repo1.repo_name,
                source_ref_type="rev",
                # parent of commit3, not in source repo2
                source_ref=commit2.short_id,
                target_ref_type="rev",
                target_ref=commit5.short_id,
                merge='1',))

        response.mustcontain('%s@%s' % (repo1.repo_name, commit2.short_id))
        response.mustcontain('%s@%s' % (repo1.repo_name, commit5.short_id))

        compare_page = ComparePage(response)
        compare_page.contains_change_summary(1, 3, 0)
        compare_page.contains_commits([commit3, commit4, commit5])

        # files
        compare_page.contains_file_links_and_anchors([
            ('file1', 'a_c--826e8142e6ba'),
        ])

    @pytest.mark.xfail_backends("svn")
    def test_compare_remote_branches(self, backend):
        repo1 = backend.repo
        repo2 = backend.create_fork()

        commit_id1 = repo1.get_commit(commit_idx=3).raw_id
        commit_id2 = repo1.get_commit(commit_idx=6).raw_id

        response = self.app.get(
            url('compare_url',
                repo_name=repo1.repo_name,
                source_ref_type="rev",
                source_ref=commit_id1,
                target_ref_type="rev",
                target_ref=commit_id2,
                target_repo=repo2.repo_name,
                merge='1',))

        response.mustcontain('%s@%s' % (repo1.repo_name, commit_id1))
        response.mustcontain('%s@%s' % (repo2.repo_name, commit_id2))

        compare_page = ComparePage(response)

        # outgoing commits between those commits
        compare_page.contains_commits(
            [repo2.get_commit(commit_idx=x) for x in [4, 5, 6]])

        # files
        compare_page.contains_file_links_and_anchors([
            ('vcs/backends/hg.py', 'a_c--9c390eb52cd6'),
            ('vcs/backends/__init__.py', 'a_c--41b41c1f2796'),
            ('vcs/backends/base.py', 'a_c--2f574d260608'),
        ])

    @pytest.mark.xfail_backends("svn")
    def test_source_repo_new_commits_after_forking_simple_diff(self, backend):
        repo1 = backend.create_repo()
        r1_name = repo1.repo_name

        commit0 = _commit_change(
            repo=r1_name, filename='file1',
            content='line1', message='commit1', vcs_type=backend.alias,
            newfile=True)
        assert repo1.scm_instance().commit_ids == [commit0.raw_id]

        # fork the repo1
        repo2 = backend.create_fork()
        assert repo2.scm_instance().commit_ids == [commit0.raw_id]

        self.r2_id = repo2.repo_id
        r2_name = repo2.repo_name

        commit1 = _commit_change(
            repo=r2_name, filename='file1-fork',
            content='file1-line1-from-fork', message='commit1-fork',
            vcs_type=backend.alias, parent=repo2.scm_instance()[-1],
            newfile=True)

        commit2 = _commit_change(
            repo=r2_name, filename='file2-fork',
            content='file2-line1-from-fork', message='commit2-fork',
            vcs_type=backend.alias, parent=commit1,
            newfile=True)

        _commit_change(  # commit 3
            repo=r2_name, filename='file3-fork',
            content='file3-line1-from-fork', message='commit3-fork',
            vcs_type=backend.alias, parent=commit2, newfile=True)

        # compare !
        commit_id1 = repo1.scm_instance().DEFAULT_BRANCH_NAME
        commit_id2 = repo2.scm_instance().DEFAULT_BRANCH_NAME

        response = self.app.get(
            url('compare_url',
                repo_name=r2_name,
                source_ref_type="branch",
                source_ref=commit_id1,
                target_ref_type="branch",
                target_ref=commit_id2,
                target_repo=r1_name,
                merge='1',))

        response.mustcontain('%s@%s' % (r2_name, commit_id1))
        response.mustcontain('%s@%s' % (r1_name, commit_id2))
        response.mustcontain('No files')
        response.mustcontain('No Commits')

        commit0 = _commit_change(
            repo=r1_name, filename='file2',
            content='line1-added-after-fork', message='commit2-parent',
            vcs_type=backend.alias, parent=None, newfile=True)

        # compare !
        response = self.app.get(
            url('compare_url',
                repo_name=r2_name,
                source_ref_type="branch",
                source_ref=commit_id1,
                target_ref_type="branch",
                target_ref=commit_id2,
                target_repo=r1_name,
                merge='1',))

        response.mustcontain('%s@%s' % (r2_name, commit_id1))
        response.mustcontain('%s@%s' % (r1_name, commit_id2))

        response.mustcontain("""commit2-parent""")
        response.mustcontain("""line1-added-after-fork""")
        compare_page = ComparePage(response)
        compare_page.contains_change_summary(1, 1, 0)

    @pytest.mark.xfail_backends("svn")
    def test_compare_commits(self, backend):
        commit0 = backend.repo.get_commit(commit_idx=0)
        commit1 = backend.repo.get_commit(commit_idx=1)

        response = self.app.get(
            url('compare_url',
                repo_name=backend.repo_name,
                source_ref_type="rev",
                source_ref=commit0.raw_id,
                target_ref_type="rev",
                target_ref=commit1.raw_id,
                merge='1',),
            extra_environ={'HTTP_X_PARTIAL_XHR': '1'},)

        # outgoing commits between those commits
        compare_page = ComparePage(response)
        compare_page.contains_commits(commits=[commit1], ancestors=[commit0])

    def test_errors_when_comparing_unknown_repo(self, backend):
        repo = backend.repo
        badrepo = 'badrepo'

        response = self.app.get(
            url('compare_url',
                repo_name=repo.repo_name,
                source_ref_type="rev",
                source_ref='tip',
                target_ref_type="rev",
                target_ref='tip',
                target_repo=badrepo,
                merge='1',),
            status=302)
        redirected = response.follow()
        redirected.mustcontain('Could not find the other repo: %s' % badrepo)

    def test_compare_not_in_preview_mode(self, backend_stub):
        commit0 = backend_stub.repo.get_commit(commit_idx=0)
        commit1 = backend_stub.repo.get_commit(commit_idx=1)

        response = self.app.get(url('compare_url',
                                    repo_name=backend_stub.repo_name,
                                    source_ref_type="rev",
                                    source_ref=commit0.raw_id,
                                    target_ref_type="rev",
                                    target_ref=commit1.raw_id,
                                    ),)

        # outgoing commits between those commits
        compare_page = ComparePage(response)
        compare_page.swap_is_visible()
        compare_page.target_source_are_enabled()

    def test_compare_of_fork_with_largefiles(self, backend_hg, settings_util):
        orig = backend_hg.create_repo(number_of_commits=1)
        fork = backend_hg.create_fork()

        settings_util.create_repo_rhodecode_ui(
            orig, 'extensions', value='', key='largefiles', active=False)
        settings_util.create_repo_rhodecode_ui(
            fork, 'extensions', value='', key='largefiles', active=True)

        compare_module = ('rhodecode.lib.vcs.backends.hg.repository.'
                          'MercurialRepository.compare')
        with mock.patch(compare_module) as compare_mock:
            compare_mock.side_effect = RepositoryRequirementError()

            response = self.app.get(
                url('compare_url',
                    repo_name=orig.repo_name,
                    action="compare",
                    source_ref_type="rev",
                    source_ref="tip",
                    target_ref_type="rev",
                    target_ref="tip",
                    merge='1',
                    target_repo=fork.repo_name),
                status=302)

            assert_session_flash(
                response,
                'Could not compare repos with different large file settings')


@pytest.mark.usefixtures("autologin_user")
class TestCompareControllerSvn:

    def test_supports_references_with_path(self, app, backend_svn):
        repo = backend_svn['svn-simple-layout']
        commit_id = repo.get_commit(commit_idx=-1).raw_id
        response = app.get(
            url('compare_url',
                repo_name=repo.repo_name,
                source_ref_type="tag",
                source_ref="%s@%s" % ('tags/v0.1', commit_id),
                target_ref_type="tag",
                target_ref="%s@%s" % ('tags/v0.2', commit_id),
                merge='1',),
            status=200)

        # Expecting no commits, since both paths are at the same revision
        response.mustcontain('No Commits')

        # Should find only one file changed when comparing those two tags
        response.mustcontain('example.py')
        compare_page = ComparePage(response)
        compare_page.contains_change_summary(1, 5, 1)

    def test_shows_commits_if_different_ids(self, app, backend_svn):
        repo = backend_svn['svn-simple-layout']
        source_id = repo.get_commit(commit_idx=-6).raw_id
        target_id = repo.get_commit(commit_idx=-1).raw_id
        response = app.get(
            url('compare_url',
                repo_name=repo.repo_name,
                source_ref_type="tag",
                source_ref="%s@%s" % ('tags/v0.1', source_id),
                target_ref_type="tag",
                target_ref="%s@%s" % ('tags/v0.2', target_id),
                merge='1',),
            status=200)

        # It should show commits
        assert 'No Commits' not in response.body

        # Should find only one file changed when comparing those two tags
        response.mustcontain('example.py')
        compare_page = ComparePage(response)
        compare_page.contains_change_summary(1, 5, 1)


class ComparePage(AssertResponse):
    """
    Abstracts the page template from the tests
    """

    def contains_file_links_and_anchors(self, files):
        for filename, file_id in files:
            self.contains_one_link(filename, '#' + file_id)
            self.contains_one_anchor(file_id)

    def contains_change_summary(self, files_changed, inserted, deleted):
        template = (
            "{files_changed} file{plural} changed: "
            "{inserted} inserted, {deleted} deleted")
        self.response.mustcontain(template.format(
            files_changed=files_changed,
            plural="s" if files_changed > 1 else "",
            inserted=inserted,
            deleted=deleted))

    def contains_commits(self, commits, ancestors=None):
        response = self.response

        for commit in commits:
            # Expecting to see the commit message in an element which
            # has the ID "c-{commit.raw_id}"
            self.element_contains('#c-' + commit.raw_id, commit.message)
            self.contains_one_link(
                'r%s:%s' % (commit.idx, commit.short_id),
                self._commit_url(commit))
        if ancestors:
            response.mustcontain('Ancestor')
            for ancestor in ancestors:
                self.contains_one_link(
                    ancestor.short_id, self._commit_url(ancestor))

    def _commit_url(self, commit):
        return '/%s/changeset/%s' % (commit.repository.name, commit.raw_id)

    def swap_is_hidden(self):
        assert '<a id="btn-swap"' not in self.response.text

    def swap_is_visible(self):
        assert '<a id="btn-swap"' in self.response.text

    def target_source_are_disabled(self):
        response = self.response
        response.mustcontain("var enable_fields = false;")
        response.mustcontain('.select2("enable", enable_fields)')

    def target_source_are_enabled(self):
        response = self.response
        response.mustcontain("var enable_fields = true;")


def _commit_change(
        repo, filename, content, message, vcs_type, parent=None,
        newfile=False):
    repo = Repository.get_by_repo_name(repo)
    _commit = parent
    if not parent:
        _commit = EmptyCommit(alias=vcs_type)

    if newfile:
        nodes = {
            filename: {
                'content': content
            }
        }
        commit = ScmModel().create_nodes(
            user=TEST_USER_ADMIN_LOGIN, repo=repo,
            message=message,
            nodes=nodes,
            parent_commit=_commit,
            author=TEST_USER_ADMIN_LOGIN,
        )
    else:
        commit = ScmModel().commit_change(
            repo=repo.scm_instance(), repo_name=repo.repo_name,
            commit=parent, user=TEST_USER_ADMIN_LOGIN,
            author=TEST_USER_ADMIN_LOGIN,
            message=message,
            content=content,
            f_path=filename
        )
    return commit
