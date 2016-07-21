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

import urllib

import mock
import pytest

from rhodecode.lib import auth
from rhodecode.lib.utils2 import safe_str, str2bool
from rhodecode.lib.vcs.exceptions import RepositoryRequirementError
from rhodecode.model.db import Repository, RepoGroup, UserRepoToPerm, User,\
    Permission
from rhodecode.model.meta import Session
from rhodecode.model.repo import RepoModel
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.settings import SettingsModel, VcsSettingsModel
from rhodecode.model.user import UserModel
from rhodecode.tests import (
    login_user_session, url, assert_session_flash, TEST_USER_ADMIN_LOGIN,
    TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS, HG_REPO, GIT_REPO,
    logout_user_session)
from rhodecode.tests.fixture import Fixture, error_function
from rhodecode.tests.utils import AssertResponse, repo_on_filesystem

fixture = Fixture()


@pytest.mark.usefixtures("app")
class TestAdminRepos:

    def test_index(self):
        self.app.get(url('repos'))

    def test_create_page_restricted(self, autologin_user, backend):
        with mock.patch('rhodecode.BACKENDS', {'git': 'git'}):
            response = self.app.get(url('new_repo'), status=200)
        assert_response = AssertResponse(response)
        element = assert_response.get_element('#repo_type')
        assert element.text_content() == '\ngit\n'

    def test_create_page_non_restricted(self, autologin_user, backend):
        response = self.app.get(url('new_repo'), status=200)
        assert_response = AssertResponse(response)
        assert_response.element_contains('#repo_type', 'git')
        assert_response.element_contains('#repo_type', 'svn')
        assert_response.element_contains('#repo_type', 'hg')

    @pytest.mark.parametrize("suffix", [u'', u''], ids=['', 'non-ascii'])
    def test_create(self, autologin_user, backend, suffix, csrf_token):
        repo_name_unicode = backend.new_repo_name(suffix=suffix)
        repo_name = repo_name_unicode.encode('utf8')
        description_unicode = u'description for newly created repo' + suffix
        description = description_unicode.encode('utf8')
        self.app.post(
            url('repos'),
            fixture._get_repo_create_params(
                repo_private=False,
                repo_name=repo_name,
                repo_type=backend.alias,
                repo_description=description,
                csrf_token=csrf_token),
            status=302
            )

        self.assert_repository_is_created_correctly(
            repo_name, description, backend)

    def test_create_numeric(self, autologin_user, backend, csrf_token):
        numeric_repo = '1234'
        repo_name = numeric_repo
        description = 'description for newly created repo' + numeric_repo
        self.app.post(
            url('repos'),
            fixture._get_repo_create_params(
                repo_private=False,
                repo_name=repo_name,
                repo_type=backend.alias,
                repo_description=description,
                csrf_token=csrf_token))

        self.assert_repository_is_created_correctly(
            repo_name, description, backend)

    @pytest.mark.parametrize("suffix", [u'', u'ąćę'], ids=['', 'non-ascii'])
    def test_create_in_group(
            self, autologin_user, backend, suffix, csrf_token):
        # create GROUP
        group_name = 'sometest_%s' % backend.alias
        gr = RepoGroupModel().create(group_name=group_name,
                                     group_description='test',
                                     owner=TEST_USER_ADMIN_LOGIN)
        Session().commit()

        repo_name = u'ingroup' + suffix
        repo_name_full = RepoGroup.url_sep().join(
            [group_name, repo_name])
        description = u'description for newly created repo'
        self.app.post(
            url('repos'),
            fixture._get_repo_create_params(
                repo_private=False,
                repo_name=safe_str(repo_name),
                repo_type=backend.alias,
                repo_description=description,
                repo_group=gr.group_id,
                csrf_token=csrf_token))

        # TODO: johbo: Cleanup work to fixture
        try:
            self.assert_repository_is_created_correctly(
                repo_name_full, description, backend)

            new_repo = RepoModel().get_by_repo_name(repo_name_full)
            inherited_perms = UserRepoToPerm.query().filter(
                UserRepoToPerm.repository_id == new_repo.repo_id).all()
            assert len(inherited_perms) == 1
        finally:
            RepoModel().delete(repo_name_full)
            RepoGroupModel().delete(group_name)
            Session().commit()

    def test_create_in_group_numeric(
            self, autologin_user, backend, csrf_token):
        # create GROUP
        group_name = 'sometest_%s' % backend.alias
        gr = RepoGroupModel().create(group_name=group_name,
                                     group_description='test',
                                     owner=TEST_USER_ADMIN_LOGIN)
        Session().commit()

        repo_name = '12345'
        repo_name_full = RepoGroup.url_sep().join([group_name, repo_name])
        description = 'description for newly created repo'
        self.app.post(
            url('repos'),
            fixture._get_repo_create_params(
                repo_private=False,
                repo_name=repo_name,
                repo_type=backend.alias,
                repo_description=description,
                repo_group=gr.group_id,
                csrf_token=csrf_token))

        # TODO: johbo: Cleanup work to fixture
        try:
            self.assert_repository_is_created_correctly(
                repo_name_full, description, backend)

            new_repo = RepoModel().get_by_repo_name(repo_name_full)
            inherited_perms = UserRepoToPerm.query()\
                .filter(UserRepoToPerm.repository_id == new_repo.repo_id).all()
            assert len(inherited_perms) == 1
        finally:
            RepoModel().delete(repo_name_full)
            RepoGroupModel().delete(group_name)
            Session().commit()

    def test_create_in_group_without_needed_permissions(self, backend):
        session = login_user_session(
            self.app, TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        csrf_token = auth.get_csrf_token(session)
        # revoke
        user_model = UserModel()
        # disable fork and create on default user
        user_model.revoke_perm(User.DEFAULT_USER, 'hg.create.repository')
        user_model.grant_perm(User.DEFAULT_USER, 'hg.create.none')
        user_model.revoke_perm(User.DEFAULT_USER, 'hg.fork.repository')
        user_model.grant_perm(User.DEFAULT_USER, 'hg.fork.none')

        # disable on regular user
        user_model.revoke_perm(TEST_USER_REGULAR_LOGIN, 'hg.create.repository')
        user_model.grant_perm(TEST_USER_REGULAR_LOGIN, 'hg.create.none')
        user_model.revoke_perm(TEST_USER_REGULAR_LOGIN, 'hg.fork.repository')
        user_model.grant_perm(TEST_USER_REGULAR_LOGIN, 'hg.fork.none')
        Session().commit()

        # create GROUP
        group_name = 'reg_sometest_%s' % backend.alias
        gr = RepoGroupModel().create(group_name=group_name,
                                     group_description='test',
                                     owner=TEST_USER_ADMIN_LOGIN)
        Session().commit()

        group_name_allowed = 'reg_sometest_allowed_%s' % backend.alias
        gr_allowed = RepoGroupModel().create(
            group_name=group_name_allowed,
            group_description='test',
            owner=TEST_USER_REGULAR_LOGIN)
        Session().commit()

        repo_name = 'ingroup'
        description = 'description for newly created repo'
        response = self.app.post(
            url('repos'),
            fixture._get_repo_create_params(
                repo_private=False,
                repo_name=repo_name,
                repo_type=backend.alias,
                repo_description=description,
                repo_group=gr.group_id,
                csrf_token=csrf_token))

        response.mustcontain('Invalid value')

        # user is allowed to create in this group
        repo_name = 'ingroup'
        repo_name_full = RepoGroup.url_sep().join(
            [group_name_allowed, repo_name])
        description = 'description for newly created repo'
        response = self.app.post(
            url('repos'),
            fixture._get_repo_create_params(
                repo_private=False,
                repo_name=repo_name,
                repo_type=backend.alias,
                repo_description=description,
                repo_group=gr_allowed.group_id,
                csrf_token=csrf_token))

        # TODO: johbo: Cleanup in pytest fixture
        try:
            self.assert_repository_is_created_correctly(
                repo_name_full, description, backend)

            new_repo = RepoModel().get_by_repo_name(repo_name_full)
            inherited_perms = UserRepoToPerm.query().filter(
                UserRepoToPerm.repository_id == new_repo.repo_id).all()
            assert len(inherited_perms) == 1

            assert repo_on_filesystem(repo_name_full)
        finally:
            RepoModel().delete(repo_name_full)
            RepoGroupModel().delete(group_name)
            RepoGroupModel().delete(group_name_allowed)
            Session().commit()

    def test_create_in_group_inherit_permissions(self, autologin_user, backend,
                                                 csrf_token):
        # create GROUP
        group_name = 'sometest_%s' % backend.alias
        gr = RepoGroupModel().create(group_name=group_name,
                                     group_description='test',
                                     owner=TEST_USER_ADMIN_LOGIN)
        perm = Permission.get_by_key('repository.write')
        RepoGroupModel().grant_user_permission(
            gr, TEST_USER_REGULAR_LOGIN, perm)

        # add repo permissions
        Session().commit()

        repo_name = 'ingroup_inherited_%s' % backend.alias
        repo_name_full = RepoGroup.url_sep().join([group_name, repo_name])
        description = 'description for newly created repo'
        self.app.post(
            url('repos'),
            fixture._get_repo_create_params(
                repo_private=False,
                repo_name=repo_name,
                repo_type=backend.alias,
                repo_description=description,
                repo_group=gr.group_id,
                repo_copy_permissions=True,
                csrf_token=csrf_token))

        # TODO: johbo: Cleanup to pytest fixture
        try:
            self.assert_repository_is_created_correctly(
                repo_name_full, description, backend)
        except Exception:
            RepoGroupModel().delete(group_name)
            Session().commit()
            raise

        # check if inherited permissions are applied
        new_repo = RepoModel().get_by_repo_name(repo_name_full)
        inherited_perms = UserRepoToPerm.query().filter(
            UserRepoToPerm.repository_id == new_repo.repo_id).all()
        assert len(inherited_perms) == 2

        assert TEST_USER_REGULAR_LOGIN in [
            x.user.username for x in inherited_perms]
        assert 'repository.write' in [
            x.permission.permission_name for x in inherited_perms]

        RepoModel().delete(repo_name_full)
        RepoGroupModel().delete(group_name)
        Session().commit()

    @pytest.mark.xfail_backends(
        "git", "hg", reason="Missing reposerver support")
    def test_create_with_clone_uri(self, autologin_user, backend, reposerver,
                                   csrf_token):
        source_repo = backend.create_repo(number_of_commits=2)
        source_repo_name = source_repo.repo_name
        reposerver.serve(source_repo.scm_instance())

        repo_name = backend.new_repo_name()
        response = self.app.post(
            url('repos'),
            fixture._get_repo_create_params(
                repo_private=False,
                repo_name=repo_name,
                repo_type=backend.alias,
                repo_description='',
                clone_uri=reposerver.url,
                csrf_token=csrf_token),
            status=302)

        # Should be redirected to the creating page
        response.mustcontain('repo_creating')

        # Expecting that both repositories have same history
        source_repo = RepoModel().get_by_repo_name(source_repo_name)
        source_vcs = source_repo.scm_instance()
        repo = RepoModel().get_by_repo_name(repo_name)
        repo_vcs = repo.scm_instance()
        assert source_vcs[0].message == repo_vcs[0].message
        assert source_vcs.count() == repo_vcs.count()
        assert source_vcs.commit_ids == repo_vcs.commit_ids

    @pytest.mark.xfail_backends("svn", reason="Depends on import support")
    def test_create_remote_repo_wrong_clone_uri(self, autologin_user, backend,
                                                csrf_token):
        repo_name = backend.new_repo_name()
        description = 'description for newly created repo'
        response = self.app.post(
            url('repos'),
            fixture._get_repo_create_params(
                repo_private=False,
                repo_name=repo_name,
                repo_type=backend.alias,
                repo_description=description,
                clone_uri='http://repo.invalid/repo',
                csrf_token=csrf_token))
        response.mustcontain('invalid clone url')

    @pytest.mark.xfail_backends("svn", reason="Depends on import support")
    def test_create_remote_repo_wrong_clone_uri_hg_svn(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.new_repo_name()
        description = 'description for newly created repo'
        response = self.app.post(
            url('repos'),
            fixture._get_repo_create_params(
                repo_private=False,
                repo_name=repo_name,
                repo_type=backend.alias,
                repo_description=description,
                clone_uri='svn+http://svn.invalid/repo',
                csrf_token=csrf_token))
        response.mustcontain('invalid clone url')

    @pytest.mark.parametrize("suffix", [u'', u'ąęł'], ids=['', 'non-ascii'])
    def test_delete(self, autologin_user, backend, suffix, csrf_token):
        repo = backend.create_repo(name_suffix=suffix)
        repo_name = repo.repo_name

        response = self.app.post(url('repo', repo_name=repo_name),
                                 params={'_method': 'delete',
                                         'csrf_token': csrf_token})
        assert_session_flash(response, 'Deleted repository %s' % (repo_name))
        response.follow()

        # check if repo was deleted from db
        assert RepoModel().get_by_repo_name(repo_name) is None
        assert not repo_on_filesystem(repo_name)

    def test_show(self, autologin_user, backend):
        self.app.get(url('repo', repo_name=backend.repo_name))

    def test_edit(self, backend, autologin_user):
        self.app.get(url('edit_repo', repo_name=backend.repo_name))

    def test_edit_accessible_when_missing_requirements(
            self, backend_hg, autologin_user):
        scm_patcher = mock.patch.object(
            Repository, 'scm_instance', side_effect=RepositoryRequirementError)
        with scm_patcher:
            self.app.get(url('edit_repo', repo_name=backend_hg.repo_name))

    def test_set_private_flag_sets_default_to_none(
            self, autologin_user, backend, csrf_token):
        # initially repository perm should be read
        perm = _get_permission_for_user(user='default', repo=backend.repo_name)
        assert len(perm) == 1
        assert perm[0].permission.permission_name == 'repository.read'
        assert not backend.repo.private

        response = self.app.post(
            url('repo', repo_name=backend.repo_name),
            fixture._get_repo_create_params(
                repo_private=1,
                repo_name=backend.repo_name,
                repo_type=backend.alias,
                user=TEST_USER_ADMIN_LOGIN,
                _method='put',
                csrf_token=csrf_token))
        assert_session_flash(
            response,
            msg='Repository %s updated successfully' % (backend.repo_name))
        assert backend.repo.private

        # now the repo default permission should be None
        perm = _get_permission_for_user(user='default', repo=backend.repo_name)
        assert len(perm) == 1
        assert perm[0].permission.permission_name == 'repository.none'

        response = self.app.post(
            url('repo', repo_name=backend.repo_name),
            fixture._get_repo_create_params(
                repo_private=False,
                repo_name=backend.repo_name,
                repo_type=backend.alias,
                user=TEST_USER_ADMIN_LOGIN,
                _method='put',
                csrf_token=csrf_token))
        assert_session_flash(
            response,
            msg='Repository %s updated successfully' % (backend.repo_name))
        assert not backend.repo.private

        # we turn off private now the repo default permission should stay None
        perm = _get_permission_for_user(user='default', repo=backend.repo_name)
        assert len(perm) == 1
        assert perm[0].permission.permission_name == 'repository.none'

        # update this permission back
        perm[0].permission = Permission.get_by_key('repository.read')
        Session().add(perm[0])
        Session().commit()

    def test_default_user_cannot_access_private_repo_in_a_group(
            self, autologin_user, user_util, backend, csrf_token):

        group = user_util.create_repo_group()

        repo = backend.create_repo(
            repo_private=True, repo_group=group, repo_copy_permissions=True)

        permissions = _get_permission_for_user(
            user='default', repo=repo.repo_name)
        assert len(permissions) == 1
        assert permissions[0].permission.permission_name == 'repository.none'
        assert permissions[0].repository.private is True

    def test_set_repo_fork_has_no_self_id(self, autologin_user, backend):
        repo = backend.repo
        response = self.app.get(
            url('edit_repo_advanced', repo_name=backend.repo_name))
        opt = """<option value="%s">vcs_test_git</option>""" % repo.repo_id
        response.mustcontain(no=[opt])

    def test_set_fork_of_target_repo(
            self, autologin_user, backend, csrf_token):
        target_repo = 'target_%s' % backend.alias
        fixture.create_repo(target_repo, repo_type=backend.alias)
        repo2 = Repository.get_by_repo_name(target_repo)
        response = self.app.post(
            url('edit_repo_advanced_fork', repo_name=backend.repo_name),
            params={'id_fork_of': repo2.repo_id, '_method': 'put',
                    'csrf_token': csrf_token})
        repo = Repository.get_by_repo_name(backend.repo_name)
        repo2 = Repository.get_by_repo_name(target_repo)
        assert_session_flash(
            response,
            'Marked repo %s as fork of %s' % (repo.repo_name, repo2.repo_name))

        assert repo.fork == repo2
        response = response.follow()
        # check if given repo is selected

        opt = 'This repository is a fork of <a href="%s">%s</a>' % (
            url('summary_home', repo_name=repo2.repo_name), repo2.repo_name)

        response.mustcontain(opt)

        fixture.destroy_repo(target_repo, forks='detach')

    @pytest.mark.backends("hg", "git")
    def test_set_fork_of_other_type_repo(self, autologin_user, backend,
                                         csrf_token):
        TARGET_REPO_MAP = {
            'git': {
                'type': 'hg',
                'repo_name': HG_REPO},
            'hg': {
                'type': 'git',
                'repo_name': GIT_REPO},
        }
        target_repo = TARGET_REPO_MAP[backend.alias]

        repo2 = Repository.get_by_repo_name(target_repo['repo_name'])
        response = self.app.post(
            url('edit_repo_advanced_fork', repo_name=backend.repo_name),
            params={'id_fork_of': repo2.repo_id, '_method': 'put',
                    'csrf_token': csrf_token})
        assert_session_flash(
            response,
            'Cannot set repository as fork of repository with other type')

    def test_set_fork_of_none(self, autologin_user, backend, csrf_token):
        # mark it as None
        response = self.app.post(
            url('edit_repo_advanced_fork', repo_name=backend.repo_name),
            params={'id_fork_of': None, '_method': 'put',
                    'csrf_token': csrf_token})
        assert_session_flash(
            response,
            'Marked repo %s as fork of %s'
            % (backend.repo_name, "Nothing"))
        assert backend.repo.fork is None

    def test_set_fork_of_same_repo(self, autologin_user, backend, csrf_token):
        repo = Repository.get_by_repo_name(backend.repo_name)
        response = self.app.post(
            url('edit_repo_advanced_fork', repo_name=backend.repo_name),
            params={'id_fork_of': repo.repo_id, '_method': 'put',
                    'csrf_token': csrf_token})
        assert_session_flash(
            response, 'An error occurred during this operation')

    def test_create_on_top_level_without_permissions(self, backend):
        session = login_user_session(
            self.app, TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        csrf_token = auth.get_csrf_token(session)

        # revoke
        user_model = UserModel()
        # disable fork and create on default user
        user_model.revoke_perm(User.DEFAULT_USER, 'hg.create.repository')
        user_model.grant_perm(User.DEFAULT_USER, 'hg.create.none')
        user_model.revoke_perm(User.DEFAULT_USER, 'hg.fork.repository')
        user_model.grant_perm(User.DEFAULT_USER, 'hg.fork.none')

        # disable on regular user
        user_model.revoke_perm(TEST_USER_REGULAR_LOGIN, 'hg.create.repository')
        user_model.grant_perm(TEST_USER_REGULAR_LOGIN, 'hg.create.none')
        user_model.revoke_perm(TEST_USER_REGULAR_LOGIN, 'hg.fork.repository')
        user_model.grant_perm(TEST_USER_REGULAR_LOGIN, 'hg.fork.none')
        Session().commit()

        repo_name = backend.new_repo_name()
        description = 'description for newly created repo'
        response = self.app.post(
            url('repos'),
            fixture._get_repo_create_params(
                repo_private=False,
                repo_name=repo_name,
                repo_type=backend.alias,
                repo_description=description,
                csrf_token=csrf_token))

        response.mustcontain(
            u"You do not have the permission to store repositories in "
            u"the root location.")

    @mock.patch.object(RepoModel, '_create_filesystem_repo', error_function)
    def test_create_repo_when_filesystem_op_fails(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.new_repo_name()
        description = 'description for newly created repo'

        response = self.app.post(
            url('repos'),
            fixture._get_repo_create_params(
                repo_private=False,
                repo_name=repo_name,
                repo_type=backend.alias,
                repo_description=description,
                csrf_token=csrf_token))

        assert_session_flash(
            response, 'Error creating repository %s' % repo_name)
        # repo must not be in db
        assert backend.repo is None
        # repo must not be in filesystem !
        assert not repo_on_filesystem(repo_name)

    def assert_repository_is_created_correctly(
            self, repo_name, description, backend):
        repo_name_utf8 = repo_name.encode('utf-8')

        # run the check page that triggers the flash message
        response = self.app.get(url('repo_check_home', repo_name=repo_name))
        assert response.json == {u'result': True}
        assert_session_flash(
            response,
            u'Created repository <a href="/%s">%s</a>'
            % (urllib.quote(repo_name_utf8), repo_name))

        # test if the repo was created in the database
        new_repo = RepoModel().get_by_repo_name(repo_name)

        assert new_repo.repo_name == repo_name
        assert new_repo.description == description

        # test if the repository is visible in the list ?
        response = self.app.get(url('summary_home', repo_name=repo_name))
        response.mustcontain(repo_name)
        response.mustcontain(backend.alias)

        assert repo_on_filesystem(repo_name)


@pytest.mark.usefixtures("app")
class TestVcsSettings(object):
    FORM_DATA = {
        'inherit_global_settings': False,
        'hooks_changegroup_repo_size': False,
        'hooks_changegroup_push_logger': False,
        'hooks_outgoing_pull_logger': False,
        'extensions_largefiles': False,
        'phases_publish': 'false',
        'rhodecode_pr_merge_enabled': False,
        'rhodecode_use_outdated_comments': False,
        'new_svn_branch': '',
        'new_svn_tag': ''
    }

    @pytest.mark.skip_backends('svn')
    def test_global_settings_initial_values(self, autologin_user, backend):
        repo_name = backend.repo_name
        response = self.app.get(url('repo_vcs_settings', repo_name=repo_name))

        expected_settings = (
            'rhodecode_use_outdated_comments', 'rhodecode_pr_merge_enabled',
            'hooks_changegroup_repo_size', 'hooks_changegroup_push_logger',
            'hooks_outgoing_pull_logger'
        )
        for setting in expected_settings:
            self.assert_repo_value_equals_global_value(response, setting)

    def test_show_settings_requires_repo_admin_permission(
            self, backend, user_util, settings_util):
        repo = backend.create_repo()
        repo_name = repo.repo_name
        user = UserModel().get_by_username(TEST_USER_REGULAR_LOGIN)
        user_util.grant_user_permission_to_repo(repo, user, 'repository.admin')
        login_user_session(
            self.app, TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        self.app.get(url('repo_vcs_settings', repo_name=repo_name), status=200)

    def test_inherit_global_settings_flag_is_true_by_default(
            self, autologin_user, backend):
        repo_name = backend.repo_name
        response = self.app.get(url('repo_vcs_settings', repo_name=repo_name))

        assert_response = AssertResponse(response)
        element = assert_response.get_element('#inherit_global_settings')
        assert element.checked

    @pytest.mark.parametrize('checked_value', [True, False])
    def test_inherit_global_settings_value(
            self, autologin_user, backend, checked_value, settings_util):
        repo = backend.create_repo()
        repo_name = repo.repo_name
        settings_util.create_repo_rhodecode_setting(
            repo, 'inherit_vcs_settings', checked_value, 'bool')
        response = self.app.get(url('repo_vcs_settings', repo_name=repo_name))

        assert_response = AssertResponse(response)
        element = assert_response.get_element('#inherit_global_settings')
        assert element.checked == checked_value

    @pytest.mark.skip_backends('svn')
    def test_hooks_settings_are_created(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.repo_name
        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        settings = SettingsModel(repo=repo_name)
        try:
            for section, key in VcsSettingsModel.HOOKS_SETTINGS:
                ui = settings.get_ui_by_section_and_key(section, key)
                assert ui.ui_active is False
        finally:
            self._cleanup_repo_settings(settings)

    def test_hooks_settings_are_not_created_for_svn(
            self, autologin_user, backend_svn, csrf_token):
        repo_name = backend_svn.repo_name
        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        settings = SettingsModel(repo=repo_name)
        try:
            for section, key in VcsSettingsModel.HOOKS_SETTINGS:
                ui = settings.get_ui_by_section_and_key(section, key)
                assert ui is None
        finally:
            self._cleanup_repo_settings(settings)

    @pytest.mark.skip_backends('svn')
    def test_hooks_settings_are_updated(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.repo_name
        settings = SettingsModel(repo=repo_name)
        for section, key in VcsSettingsModel.HOOKS_SETTINGS:
            settings.create_ui_section_value(section, '', key=key, active=True)

        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        try:
            for section, key in VcsSettingsModel.HOOKS_SETTINGS:
                ui = settings.get_ui_by_section_and_key(section, key)
                assert ui.ui_active is False
        finally:
            self._cleanup_repo_settings(settings)

    def test_hooks_settings_are_not_updated_for_svn(
            self, autologin_user, backend_svn, csrf_token):
        repo_name = backend_svn.repo_name
        settings = SettingsModel(repo=repo_name)
        for section, key in VcsSettingsModel.HOOKS_SETTINGS:
            settings.create_ui_section_value(section, '', key=key, active=True)

        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        try:
            for section, key in VcsSettingsModel.HOOKS_SETTINGS:
                ui = settings.get_ui_by_section_and_key(section, key)
                assert ui.ui_active is True
        finally:
            self._cleanup_repo_settings(settings)

    @pytest.mark.skip_backends('svn')
    def test_pr_settings_are_created(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.repo_name
        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        settings = SettingsModel(repo=repo_name)
        try:
            for name in VcsSettingsModel.GENERAL_SETTINGS:
                setting = settings.get_setting_by_name(name)
                assert setting.app_settings_value is False
        finally:
            self._cleanup_repo_settings(settings)

    def test_pr_settings_are_not_created_for_svn(
            self, autologin_user, backend_svn, csrf_token):
        repo_name = backend_svn.repo_name
        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        settings = SettingsModel(repo=repo_name)
        try:
            for name in VcsSettingsModel.GENERAL_SETTINGS:
                setting = settings.get_setting_by_name(name)
                assert setting is None
        finally:
            self._cleanup_repo_settings(settings)

    def test_pr_settings_creation_requires_repo_admin_permission(
            self, backend, user_util, settings_util, csrf_token):
        repo = backend.create_repo()
        repo_name = repo.repo_name
        user = UserModel().get_by_username(TEST_USER_REGULAR_LOGIN)

        logout_user_session(self.app, csrf_token)
        session = login_user_session(
            self.app, TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        new_csrf_token = auth.get_csrf_token(session)

        user_util.grant_user_permission_to_repo(repo, user, 'repository.admin')
        data = self.FORM_DATA.copy()
        data['csrf_token'] = new_csrf_token
        settings = SettingsModel(repo=repo_name)

        try:
            self.app.post(
                url('repo_vcs_settings', repo_name=repo_name), data,
                status=302)
        finally:
            self._cleanup_repo_settings(settings)

    @pytest.mark.skip_backends('svn')
    def test_pr_settings_are_updated(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.repo_name
        settings = SettingsModel(repo=repo_name)
        for name in VcsSettingsModel.GENERAL_SETTINGS:
            settings.create_or_update_setting(name, True, 'bool')

        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        try:
            for name in VcsSettingsModel.GENERAL_SETTINGS:
                setting = settings.get_setting_by_name(name)
                assert setting.app_settings_value is False
        finally:
            self._cleanup_repo_settings(settings)

    def test_pr_settings_are_not_updated_for_svn(
            self, autologin_user, backend_svn, csrf_token):
        repo_name = backend_svn.repo_name
        settings = SettingsModel(repo=repo_name)
        for name in VcsSettingsModel.GENERAL_SETTINGS:
            settings.create_or_update_setting(name, True, 'bool')

        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        try:
            for name in VcsSettingsModel.GENERAL_SETTINGS:
                setting = settings.get_setting_by_name(name)
                assert setting.app_settings_value is True
        finally:
            self._cleanup_repo_settings(settings)

    def test_svn_settings_are_created(
            self, autologin_user, backend_svn, csrf_token, settings_util):
        repo_name = backend_svn.repo_name
        data = self.FORM_DATA.copy()
        data['new_svn_tag'] = 'svn-tag'
        data['new_svn_branch'] = 'svn-branch'
        data['csrf_token'] = csrf_token

        # Create few global settings to make sure that uniqueness validators
        # are not triggered
        settings_util.create_rhodecode_ui(
            VcsSettingsModel.SVN_BRANCH_SECTION, 'svn-branch')
        settings_util.create_rhodecode_ui(
            VcsSettingsModel.SVN_TAG_SECTION, 'svn-tag')

        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        settings = SettingsModel(repo=repo_name)
        try:
            svn_branches = settings.get_ui_by_section(
                VcsSettingsModel.SVN_BRANCH_SECTION)
            svn_branch_names = [b.ui_value for b in svn_branches]
            svn_tags = settings.get_ui_by_section(
                VcsSettingsModel.SVN_TAG_SECTION)
            svn_tag_names = [b.ui_value for b in svn_tags]
            assert 'svn-branch' in svn_branch_names
            assert 'svn-tag' in svn_tag_names
        finally:
            self._cleanup_repo_settings(settings)

    def test_svn_settings_are_unique(
            self, autologin_user, backend_svn, csrf_token, settings_util):
        repo = backend_svn.repo
        repo_name = repo.repo_name
        data = self.FORM_DATA.copy()
        data['new_svn_tag'] = 'test_tag'
        data['new_svn_branch'] = 'test_branch'
        data['csrf_token'] = csrf_token
        settings_util.create_repo_rhodecode_ui(
            repo, VcsSettingsModel.SVN_BRANCH_SECTION, 'test_branch')
        settings_util.create_repo_rhodecode_ui(
            repo, VcsSettingsModel.SVN_TAG_SECTION, 'test_tag')

        response = self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=200)
        response.mustcontain('Pattern already exists')

    def test_svn_settings_with_empty_values_are_not_created(
            self, autologin_user, backend_svn, csrf_token):
        repo_name = backend_svn.repo_name
        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        settings = SettingsModel(repo=repo_name)
        try:
            svn_branches = settings.get_ui_by_section(
                VcsSettingsModel.SVN_BRANCH_SECTION)
            svn_tags = settings.get_ui_by_section(
                VcsSettingsModel.SVN_TAG_SECTION)
            assert len(svn_branches) == 0
            assert len(svn_tags) == 0
        finally:
            self._cleanup_repo_settings(settings)

    def test_svn_settings_are_shown_for_svn_repository(
            self, autologin_user, backend_svn, csrf_token):
        repo_name = backend_svn.repo_name
        response = self.app.get(
            url('repo_vcs_settings', repo_name=repo_name), status=200)
        response.mustcontain('Subversion Settings')

    @pytest.mark.skip_backends('svn')
    def test_svn_settings_are_not_created_for_not_svn_repository(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.repo_name
        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        settings = SettingsModel(repo=repo_name)
        try:
            svn_branches = settings.get_ui_by_section(
                VcsSettingsModel.SVN_BRANCH_SECTION)
            svn_tags = settings.get_ui_by_section(
                VcsSettingsModel.SVN_TAG_SECTION)
            assert len(svn_branches) == 0
            assert len(svn_tags) == 0
        finally:
            self._cleanup_repo_settings(settings)

    @pytest.mark.skip_backends('svn')
    def test_svn_settings_are_shown_only_for_svn_repository(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.repo_name
        response = self.app.get(
            url('repo_vcs_settings', repo_name=repo_name), status=200)
        response.mustcontain(no='Subversion Settings')

    def test_hg_settings_are_created(
            self, autologin_user, backend_hg, csrf_token):
        repo_name = backend_hg.repo_name
        data = self.FORM_DATA.copy()
        data['new_svn_tag'] = 'svn-tag'
        data['new_svn_branch'] = 'svn-branch'
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        settings = SettingsModel(repo=repo_name)
        try:
            largefiles_ui = settings.get_ui_by_section_and_key(
                'extensions', 'largefiles')
            assert largefiles_ui.ui_active is False
            phases_ui = settings.get_ui_by_section_and_key(
                'phases', 'publish')
            assert str2bool(phases_ui.ui_value) is False
        finally:
            self._cleanup_repo_settings(settings)

    def test_hg_settings_are_updated(
            self, autologin_user, backend_hg, csrf_token):
        repo_name = backend_hg.repo_name
        settings = SettingsModel(repo=repo_name)
        settings.create_ui_section_value(
            'extensions', '', key='largefiles', active=True)
        settings.create_ui_section_value(
            'phases', '1', key='publish', active=True)

        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        try:
            largefiles_ui = settings.get_ui_by_section_and_key(
                'extensions', 'largefiles')
            assert largefiles_ui.ui_active is False
            phases_ui = settings.get_ui_by_section_and_key(
                'phases', 'publish')
            assert str2bool(phases_ui.ui_value) is False
        finally:
            self._cleanup_repo_settings(settings)

    def test_hg_settings_are_shown_for_hg_repository(
            self, autologin_user, backend_hg, csrf_token):
        repo_name = backend_hg.repo_name
        response = self.app.get(
            url('repo_vcs_settings', repo_name=repo_name), status=200)
        response.mustcontain('Mercurial Settings')

    @pytest.mark.skip_backends('hg')
    def test_hg_settings_are_created_only_for_hg_repository(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.repo_name
        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        settings = SettingsModel(repo=repo_name)
        try:
            largefiles_ui = settings.get_ui_by_section_and_key(
                'extensions', 'largefiles')
            assert largefiles_ui is None
            phases_ui = settings.get_ui_by_section_and_key(
                'phases', 'publish')
            assert phases_ui is None
        finally:
            self._cleanup_repo_settings(settings)

    @pytest.mark.skip_backends('hg')
    def test_hg_settings_are_shown_only_for_hg_repository(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.repo_name
        response = self.app.get(
            url('repo_vcs_settings', repo_name=repo_name), status=200)
        response.mustcontain(no='Mercurial Settings')

    @pytest.mark.skip_backends('hg')
    def test_hg_settings_are_updated_only_for_hg_repository(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.repo_name
        settings = SettingsModel(repo=repo_name)
        settings.create_ui_section_value(
            'extensions', '', key='largefiles', active=True)
        settings.create_ui_section_value(
            'phases', '1', key='publish', active=True)

        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)
        try:
            largefiles_ui = settings.get_ui_by_section_and_key(
                'extensions', 'largefiles')
            assert largefiles_ui.ui_active is True
            phases_ui = settings.get_ui_by_section_and_key(
                'phases', 'publish')
            assert phases_ui.ui_value == '1'
        finally:
            self._cleanup_repo_settings(settings)

    def test_per_repo_svn_settings_are_displayed(
            self, autologin_user, backend_svn, settings_util):
        repo = backend_svn.create_repo()
        repo_name = repo.repo_name
        branches = [
            settings_util.create_repo_rhodecode_ui(
                repo, VcsSettingsModel.SVN_BRANCH_SECTION,
                'branch_{}'.format(i))
            for i in range(10)]
        tags = [
            settings_util.create_repo_rhodecode_ui(
                repo, VcsSettingsModel.SVN_TAG_SECTION, 'tag_{}'.format(i))
            for i in range(10)]

        response = self.app.get(
            url('repo_vcs_settings', repo_name=repo_name), status=200)
        assert_response = AssertResponse(response)
        for branch in branches:
            css_selector = '[name=branch_value_{}]'.format(branch.ui_id)
            element = assert_response.get_element(css_selector)
            assert element.value == branch.ui_value
        for tag in tags:
            css_selector = '[name=tag_ui_value_new_{}]'.format(tag.ui_id)
            element = assert_response.get_element(css_selector)
            assert element.value == tag.ui_value

    def test_per_repo_hg_and_pr_settings_are_not_displayed_for_svn(
            self, autologin_user, backend_svn, settings_util):
        repo = backend_svn.create_repo()
        repo_name = repo.repo_name
        response = self.app.get(
            url('repo_vcs_settings', repo_name=repo_name), status=200)
        response.mustcontain(no='<label>Hooks:</label>')
        response.mustcontain(no='<label>Pull Request Settings:</label>')

    def test_inherit_global_settings_value_is_saved(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.repo_name
        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        data['inherit_global_settings'] = True
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)

        settings = SettingsModel(repo=repo_name)
        vcs_settings = VcsSettingsModel(repo=repo_name)
        try:
            assert vcs_settings.inherit_global_settings is True
        finally:
            self._cleanup_repo_settings(settings)

    def test_repo_cache_is_invalidated_when_settings_are_updated(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.repo_name
        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        data['inherit_global_settings'] = True
        settings = SettingsModel(repo=repo_name)

        invalidation_patcher = mock.patch(
            'rhodecode.controllers.admin.repos.ScmModel.mark_for_invalidation')
        with invalidation_patcher as invalidation_mock:
            self.app.post(
                url('repo_vcs_settings', repo_name=repo_name), data,
                status=302)
        try:
            invalidation_mock.assert_called_once_with(repo_name, delete=True)
        finally:
            self._cleanup_repo_settings(settings)

    def test_other_settings_not_saved_inherit_global_settings_is_true(
            self, autologin_user, backend, csrf_token):
        repo_name = backend.repo_name
        data = self.FORM_DATA.copy()
        data['csrf_token'] = csrf_token
        data['inherit_global_settings'] = True
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data, status=302)

        settings = SettingsModel(repo=repo_name)
        ui_settings = (
            VcsSettingsModel.HOOKS_SETTINGS + VcsSettingsModel.HG_SETTINGS)

        vcs_settings = []
        try:
            for section, key in ui_settings:
                ui = settings.get_ui_by_section_and_key(section, key)
                if ui:
                    vcs_settings.append(ui)
            vcs_settings.extend(settings.get_ui_by_section(
                VcsSettingsModel.SVN_BRANCH_SECTION))
            vcs_settings.extend(settings.get_ui_by_section(
                VcsSettingsModel.SVN_TAG_SECTION))
            for name in VcsSettingsModel.GENERAL_SETTINGS:
                setting = settings.get_setting_by_name(name)
                if setting:
                    vcs_settings.append(setting)
            assert vcs_settings == []
        finally:
            self._cleanup_repo_settings(settings)

    def test_delete_svn_branch_and_tag_patterns(
            self, autologin_user, backend_svn, settings_util, csrf_token):
        repo = backend_svn.create_repo()
        repo_name = repo.repo_name
        branch = settings_util.create_repo_rhodecode_ui(
            repo, VcsSettingsModel.SVN_BRANCH_SECTION, 'test_branch',
            cleanup=False)
        tag = settings_util.create_repo_rhodecode_ui(
            repo, VcsSettingsModel.SVN_TAG_SECTION, 'test_tag', cleanup=False)
        data = {
            '_method': 'delete',
            'csrf_token': csrf_token
        }
        for id_ in (branch.ui_id, tag.ui_id):
            data['delete_svn_pattern'] = id_,
            self.app.post(
                url('repo_vcs_settings', repo_name=repo_name), data,
                headers={'X-REQUESTED-WITH': 'XMLHttpRequest', }, status=200)
        settings = VcsSettingsModel(repo=repo_name)
        assert settings.get_repo_svn_branch_patterns() == []

    def test_delete_svn_branch_requires_repo_admin_permission(
            self, backend_svn, user_util, settings_util, csrf_token):
        repo = backend_svn.create_repo()
        repo_name = repo.repo_name
        user = UserModel().get_by_username(TEST_USER_REGULAR_LOGIN)
        logout_user_session(self.app, csrf_token)
        session = login_user_session(
            self.app, TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        csrf_token = auth.get_csrf_token(session)
        user_util.grant_user_permission_to_repo(repo, user, 'repository.admin')
        branch = settings_util.create_repo_rhodecode_ui(
            repo, VcsSettingsModel.SVN_BRANCH_SECTION, 'test_branch',
            cleanup=False)
        data = {
            '_method': 'delete',
            'csrf_token': csrf_token,
            'delete_svn_pattern': branch.ui_id
        }
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data,
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest', }, status=200)

    def test_delete_svn_branch_raises_400_when_not_found(
            self, autologin_user, backend_svn, settings_util, csrf_token):
        repo_name = backend_svn.repo_name
        data = {
            '_method': 'delete',
            'delete_svn_pattern': 123,
            'csrf_token': csrf_token
        }
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data,
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest', }, status=400)

    def test_delete_svn_branch_raises_400_when_no_id_specified(
            self, autologin_user, backend_svn, settings_util, csrf_token):
        repo_name = backend_svn.repo_name
        data = {
            '_method': 'delete',
            'csrf_token': csrf_token
        }
        self.app.post(
            url('repo_vcs_settings', repo_name=repo_name), data,
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest', }, status=400)

    def _cleanup_repo_settings(self, settings_model):
        cleanup = []
        ui_settings = (
            VcsSettingsModel.HOOKS_SETTINGS + VcsSettingsModel.HG_SETTINGS)

        for section, key in ui_settings:
            ui = settings_model.get_ui_by_section_and_key(section, key)
            if ui:
                cleanup.append(ui)

        cleanup.extend(settings_model.get_ui_by_section(
            VcsSettingsModel.INHERIT_SETTINGS))
        cleanup.extend(settings_model.get_ui_by_section(
            VcsSettingsModel.SVN_BRANCH_SECTION))
        cleanup.extend(settings_model.get_ui_by_section(
            VcsSettingsModel.SVN_TAG_SECTION))

        for name in VcsSettingsModel.GENERAL_SETTINGS:
            setting = settings_model.get_setting_by_name(name)
            if setting:
                cleanup.append(setting)

        for object_ in cleanup:
            Session().delete(object_)
        Session().commit()

    def assert_repo_value_equals_global_value(self, response, setting):
        assert_response = AssertResponse(response)
        global_css_selector = '[name={}_inherited]'.format(setting)
        repo_css_selector = '[name={}]'.format(setting)
        repo_element = assert_response.get_element(repo_css_selector)
        global_element = assert_response.get_element(global_css_selector)
        assert repo_element.value == global_element.value


def _get_permission_for_user(user, repo):
    perm = UserRepoToPerm.query()\
        .filter(UserRepoToPerm.repository ==
                Repository.get_by_repo_name(repo))\
        .filter(UserRepoToPerm.user == User.get_by_username(user))\
        .all()
    return perm
