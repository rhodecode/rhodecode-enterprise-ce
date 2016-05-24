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

from rhodecode.tests import *
from rhodecode.tests.fixture import Fixture

from rhodecode.model.db import Repository
from rhodecode.model.repo import RepoModel
from rhodecode.model.user import UserModel
from rhodecode.model.meta import Session

fixture = Fixture()


class _BaseTest(TestController):

    REPO = None
    REPO_TYPE = None
    NEW_REPO = None
    REPO_FORK = None

    @pytest.fixture(autouse=True)
    def prepare(self, request, pylonsapp):
        self.username = u'forkuser'
        self.password = u'qweqwe'
        self.u1 = fixture.create_user(self.username, password=self.password,
                                      email=u'fork_king@rhodecode.org')
        Session().commit()
        self.u1id = self.u1.user_id
        request.addfinalizer(self.cleanup)

    def cleanup(self):
        u1 = UserModel().get(self.u1id)
        Session().delete(u1)
        Session().commit()

    def test_index(self):
        self.log_user()
        repo_name = self.REPO
        response = self.app.get(url(controller='forks', action='forks',
                                    repo_name=repo_name))

        response.mustcontain("""There are no forks yet""")

    def test_no_permissions_to_fork(self):
        usr = self.log_user(TEST_USER_REGULAR_LOGIN,
                            TEST_USER_REGULAR_PASS)['user_id']
        user_model = UserModel()
        user_model.revoke_perm(usr, 'hg.fork.repository')
        user_model.grant_perm(usr, 'hg.fork.none')
        u = UserModel().get(usr)
        u.inherit_default_permissions = False
        Session().commit()
        # try create a fork
        repo_name = self.REPO
        self.app.post(
            url(controller='forks', action='fork_create', repo_name=repo_name),
            {'csrf_token': self.csrf_token}, status=403)

    def test_index_with_fork(self):
        self.log_user()

        # create a fork
        fork_name = self.REPO_FORK
        description = 'fork of vcs test'
        repo_name = self.REPO
        source_repo = Repository.get_by_repo_name(repo_name)
        creation_args = {
            'repo_name': fork_name,
            'repo_group': '',
            'fork_parent_id': source_repo.repo_id,
            'repo_type': self.REPO_TYPE,
            'description': description,
            'private': 'False',
            'landing_rev': 'rev:tip',
            'csrf_token': self.csrf_token,
        }

        self.app.post(url(controller='forks', action='fork_create',
                          repo_name=repo_name), creation_args)

        response = self.app.get(url(controller='forks', action='forks',
                                    repo_name=repo_name))

        response.mustcontain(
            """<a href="/%s">%s</a>""" % (fork_name, fork_name)
        )

        # remove this fork
        response = self.app.post(
            url('repo', repo_name=fork_name),
            params={'_method': 'delete', 'csrf_token': self.csrf_token})

    def test_fork_create_into_group(self):
        self.log_user()
        group = fixture.create_repo_group('vc')
        group_id = group.group_id
        fork_name = self.REPO_FORK
        fork_name_full = 'vc/%s' % fork_name
        description = 'fork of vcs test'
        repo_name = self.REPO
        source_repo = Repository.get_by_repo_name(repo_name)
        creation_args = {
            'repo_name': fork_name,
            'repo_group': group_id,
            'fork_parent_id': source_repo.repo_id,
            'repo_type': self.REPO_TYPE,
            'description': description,
            'private': 'False',
            'landing_rev': 'rev:tip',
            'csrf_token': self.csrf_token,
        }
        self.app.post(url(controller='forks', action='fork_create',
                          repo_name=repo_name), creation_args)
        repo = Repository.get_by_repo_name(fork_name_full)
        assert repo.fork.repo_name == self.REPO

        # run the check page that triggers the flash message
        response = self.app.get(url('repo_check_home', repo_name=fork_name_full))
        # test if we have a message that fork is ok
        assert_session_flash(response,
                'Forked repository %s as <a href="/%s">%s</a>'
                % (repo_name, fork_name_full, fork_name_full))

        # test if the fork was created in the database
        fork_repo = Session().query(Repository)\
            .filter(Repository.repo_name == fork_name_full).one()

        assert fork_repo.repo_name == fork_name_full
        assert fork_repo.fork.repo_name == repo_name

        # test if the repository is visible in the list ?
        response = self.app.get(url('summary_home', repo_name=fork_name_full))
        response.mustcontain(fork_name_full)
        response.mustcontain(self.REPO_TYPE)

        response.mustcontain('Fork of')
        response.mustcontain('<a href="/%s">%s</a>' % (repo_name, repo_name))

        fixture.destroy_repo(fork_name_full)
        fixture.destroy_repo_group(group_id)

    def test_z_fork_create(self):
        self.log_user()
        fork_name = self.REPO_FORK
        description = 'fork of vcs test'
        repo_name = self.REPO
        source_repo = Repository.get_by_repo_name(repo_name)
        creation_args = {
            'repo_name': fork_name,
            'repo_group': '',
            'fork_parent_id': source_repo.repo_id,
            'repo_type': self.REPO_TYPE,
            'description': description,
            'private': 'False',
            'landing_rev': 'rev:tip',
            'csrf_token': self.csrf_token,
        }
        self.app.post(url(controller='forks', action='fork_create',
                          repo_name=repo_name), creation_args)
        repo = Repository.get_by_repo_name(self.REPO_FORK)
        assert repo.fork.repo_name == self.REPO

        # run the check page that triggers the flash message
        response = self.app.get(url('repo_check_home', repo_name=fork_name))
        # test if we have a message that fork is ok
        assert_session_flash(response,
                'Forked repository %s as <a href="/%s">%s</a>'
                % (repo_name, fork_name, fork_name))

        # test if the fork was created in the database
        fork_repo = Session().query(Repository)\
            .filter(Repository.repo_name == fork_name).one()

        assert fork_repo.repo_name == fork_name
        assert fork_repo.fork.repo_name == repo_name

        # test if the repository is visible in the list ?
        response = self.app.get(url('summary_home', repo_name=fork_name))
        response.mustcontain(fork_name)
        response.mustcontain(self.REPO_TYPE)
        response.mustcontain('Fork of')
        response.mustcontain('<a href="/%s">%s</a>' % (repo_name, repo_name))

    def test_zz_fork_permission_page(self):
        usr = self.log_user(self.username, self.password)['user_id']
        repo_name = self.REPO

        forks = Repository.query()\
            .filter(Repository.repo_type == self.REPO_TYPE)\
            .filter(Repository.fork_id != None).all()
        assert 1 == len(forks)

        # set read permissions for this
        RepoModel().grant_user_permission(repo=forks[0],
                                          user=usr,
                                          perm='repository.read')
        Session().commit()

        response = self.app.get(url(controller='forks', action='forks',
                                    repo_name=repo_name))

        response.mustcontain('fork of vcs test')

    def test_zzz_fork_permission_page(self):
        usr = self.log_user(self.username, self.password)['user_id']
        repo_name = self.REPO

        forks = Repository.query()\
            .filter(Repository.repo_type == self.REPO_TYPE)\
            .filter(Repository.fork_id != None).all()
        assert 1 == len(forks)

        # set none
        RepoModel().grant_user_permission(repo=forks[0],
                                          user=usr, perm='repository.none')
        Session().commit()
        # fork shouldn't be there
        response = self.app.get(url(controller='forks', action='forks',
                                    repo_name=repo_name))
        response.mustcontain('There are no forks yet')


class TestGIT(_BaseTest):
    REPO = GIT_REPO
    NEW_REPO = NEW_GIT_REPO
    REPO_TYPE = 'git'
    REPO_FORK = GIT_FORK


class TestHG(_BaseTest):
    REPO = HG_REPO
    NEW_REPO = NEW_HG_REPO
    REPO_TYPE = 'hg'
    REPO_FORK = HG_FORK


@pytest.mark.usefixtures('app', 'autologin_user')
@pytest.mark.skip_backends('git','hg')
class TestSVNFork:

    def test_fork_redirects(self, backend):
        denied_actions = ['fork','fork_create']
        for action in denied_actions:
            response = self.app.get(url(
                controller='forks', action=action,
                repo_name=backend.repo_name))
            assert response.status_int == 302

            # Not allowed, redirect to the summary
            redirected = response.follow()
            summary_url = url('summary_home', repo_name=backend.repo_name)

            # URL adds leading slash and path doesn't have it
            assert redirected.req.path == summary_url
