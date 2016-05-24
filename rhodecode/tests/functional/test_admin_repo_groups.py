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

from rhodecode.lib import helpers as h
from rhodecode.model.meta import Session
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.tests import (
    url, TestController, assert_session_flash, GIT_REPO, HG_REPO,
    TESTS_TMP_PATH, TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
from rhodecode.tests.fixture import Fixture

fixture = Fixture()


def test_update(app, csrf_token, autologin_user, user_util):
    repo_group = user_util.create_repo_group()
    description = 'description for newly created repo group'
    Session().commit()
    response = app.post(
        url('update_repo_group', group_name=repo_group.group_name),
        fixture._get_group_create_params(
            group_name=repo_group.group_name,
            group_description=description,
            csrf_token=csrf_token,
            _method='PUT')
        )
    # TODO: anderson: johbo: we believe that this update should return
    # a redirect instead of rendering the template.
    assert response.status_code == 200


def test_edit(app, user_util, autologin_user):
    repo_group = user_util.create_repo_group()
    Session().commit()
    response = app.get(
        url('edit_repo_group', group_name=repo_group.group_name))
    assert response.status_code == 200


def test_edit_repo_group_perms(app, user_util, autologin_user):
    repo_group = user_util.create_repo_group()
    Session().commit()
    response = app.get(
        url('edit_repo_group_perms', group_name=repo_group.group_name))
    assert response.status_code == 200


def test_update_fails_when_parent_pointing_to_self(
        app, csrf_token, user_util, autologin_user):
    group = user_util.create_repo_group()
    response = app.post(
        url('update_repo_group', group_name=group.group_name),
        fixture._get_group_create_params(
            group_parent_id=group.group_id,
            csrf_token=csrf_token,
            _method='PUT')
        )
    response.mustcontain(
        '<select class="medium error" id="group_parent_id"'
        ' name="group_parent_id">')
    response.mustcontain('<span class="error-message">Value must be one of:')


class _BaseTest(TestController):

    REPO_GROUP = None
    NEW_REPO_GROUP = None
    REPO = None
    REPO_TYPE = None

    def test_index(self):
        self.log_user()
        response = self.app.get(url('repo_groups'))
        response.mustcontain('data: []')

    def test_index_after_creating_group(self):
        self.log_user()
        fixture.create_repo_group('test_repo_group')
        response = self.app.get(url('repo_groups'))
        response.mustcontain('"name_raw": "test_repo_group"')
        fixture.destroy_repo_group('test_repo_group')

    def test_new(self):
        self.log_user()
        self.app.get(url('new_repo_group'))

    def test_new_by_regular_user_no_permission(self):
        self.log_user(TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        self.app.get(url('new_repo_group'), status=403)

    def test_create(self):
        self.log_user()
        repo_group_name = self.NEW_REPO_GROUP
        repo_group_name_unicode = repo_group_name.decode('utf8')
        description = 'description for newly created repo group'

        response = self.app.post(
            url('repo_groups'),
            fixture._get_group_create_params(
                group_name=repo_group_name,
                group_description=description,
                csrf_token=self.csrf_token))

        # run the check page that triggers the flash message
        # response = self.app.get(url('repo_check_home', repo_name=repo_name))
        # assert response.json == {u'result': True}
        assert_session_flash(
            response,
            u'Created repository group <a href="%s">%s</a>' % (
                h.url('repo_group_home', group_name=repo_group_name),
                repo_group_name_unicode))

        # # test if the repo group was created in the database
        new_repo_group = RepoGroupModel()._get_repo_group(
            repo_group_name_unicode)
        assert new_repo_group is not None

        assert new_repo_group.group_name == repo_group_name_unicode
        assert new_repo_group.group_description == description

        #
        # # test if the repository is visible in the list ?
        response = self.app.get(
            url('repo_group_home', group_name=repo_group_name))
        response.mustcontain(repo_group_name)

        # test if the repository group was created on filesystem
        is_on_filesystem = os.path.isdir(
            os.path.join(TESTS_TMP_PATH, repo_group_name))
        if not is_on_filesystem:
            self.fail('no repo group %s in filesystem' % repo_group_name)

        RepoGroupModel().delete(repo_group_name_unicode)
        Session().commit()

    def test_create_subgroup(self, user_util):
        self.log_user()
        repo_group_name = self.NEW_REPO_GROUP
        parent_group = user_util.create_repo_group()
        parent_group_name = parent_group.group_name

        expected_group_name = '{}/{}'.format(
            parent_group_name, repo_group_name)
        expected_group_name_unicode = expected_group_name.decode('utf8')

        try:
            response = self.app.post(
                url('repo_groups'),
                fixture._get_group_create_params(
                    group_name=repo_group_name,
                    group_parent_id=parent_group.group_id,
                    group_description='Test desciption',
                    csrf_token=self.csrf_token))

            assert_session_flash(
                response,
                u'Created repository group <a href="%s">%s</a>' % (
                    h.url('repo_group_home', group_name=expected_group_name),
                    expected_group_name_unicode))
        finally:
            RepoGroupModel().delete(expected_group_name_unicode)
            Session().commit()

    def test_user_with_creation_permissions_cannot_create_subgroups(
            self, user_util):

        user_util.grant_user_permission(
            TEST_USER_REGULAR_LOGIN, 'hg.repogroup.create.true')
        parent_group = user_util.create_repo_group()
        parent_group_id = parent_group.group_id
        self.log_user(TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        self.app.get(
            url('new_repo_group', parent_group=parent_group_id,),
            status=403)


class TestRepoGroupsControllerGIT(_BaseTest):
    REPO_GROUP = None
    NEW_REPO_GROUP = 'git_repo'
    REPO = GIT_REPO
    REPO_TYPE = 'git'


class TestRepoGroupsControllerHG(_BaseTest):
    REPO_GROUP = None
    NEW_REPO_GROUP = 'hg_repo'
    REPO = HG_REPO
    REPO_TYPE = 'hg'


class TestRepoGroupsControllerNumericalHG(_BaseTest):
    REPO_GROUP = None
    NEW_REPO_GROUP = '12345'
    REPO = HG_REPO
    REPO_TYPE = 'hg'


class TestRepoGroupsControllerNonAsciiHG(_BaseTest):
    REPO_GROUP = None
    NEW_REPO_GROUP = 'hg_repo_ąć'
    REPO = HG_REPO
    REPO_TYPE = 'hg'
