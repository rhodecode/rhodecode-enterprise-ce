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

from rhodecode.lib.auth import AuthUser
from rhodecode.model.db import (
    RepoGroup, User, UserGroupRepoGroupToPerm, Permission, UserToPerm,
    UserGroupToPerm)
from rhodecode.model.meta import Session
from rhodecode.model.permission import PermissionModel
from rhodecode.model.repo import RepoModel
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.user import UserModel
from rhodecode.model.user_group import UserGroupModel
from rhodecode.tests.fixture import Fixture


fixture = Fixture()


@pytest.fixture
def repo_name(backend_hg):
    return backend_hg.repo_name


class TestPermissions(object):

    @pytest.fixture(scope='class', autouse=True)
    def default_permissions(self, request, pylonsapp):
        # recreate default user to get a clean start
        PermissionModel().create_default_user_permissions(
            user=User.DEFAULT_USER, force=True)
        Session().commit()

    @pytest.fixture(autouse=True)
    def prepare_users(self, request):
        # TODO: User creation is a duplicate of test_nofitications, check
        # if that can be unified
        self.u1 = UserModel().create_or_update(
            username=u'u1', password=u'qweqwe',
            email=u'u1@rhodecode.org', firstname=u'u1', lastname=u'u1'
        )
        self.u2 = UserModel().create_or_update(
            username=u'u2', password=u'qweqwe',
            email=u'u2@rhodecode.org', firstname=u'u2', lastname=u'u2'
        )
        self.u3 = UserModel().create_or_update(
            username=u'u3', password=u'qweqwe',
            email=u'u3@rhodecode.org', firstname=u'u3', lastname=u'u3'
        )
        self.anon = User.get_default_user()
        self.a1 = UserModel().create_or_update(
            username=u'a1', password=u'qweqwe',
            email=u'a1@rhodecode.org', firstname=u'a1', lastname=u'a1',
            admin=True
        )
        Session().commit()

        request.addfinalizer(self.cleanup)

    def cleanup(self):
        if hasattr(self, 'test_repo'):
            RepoModel().delete(repo=self.test_repo)

        if hasattr(self, 'g1'):
            RepoGroupModel().delete(self.g1.group_id)
        if hasattr(self, 'g2'):
            RepoGroupModel().delete(self.g2.group_id)

        UserModel().delete(self.u1)
        UserModel().delete(self.u2)
        UserModel().delete(self.u3)
        UserModel().delete(self.a1)

        if hasattr(self, 'ug1'):
            UserGroupModel().delete(self.ug1, force=True)

        Session().commit()

    def test_default_perms_set(self, repo_name):
        assert repo_perms(self.u1)[repo_name] == 'repository.read'
        new_perm = 'repository.write'
        RepoModel().grant_user_permission(repo=repo_name, user=self.u1,
                                          perm=new_perm)
        Session().commit()
        assert repo_perms(self.u1)[repo_name] == new_perm

    def test_default_admin_perms_set(self, repo_name):
        assert repo_perms(self.a1)[repo_name] == 'repository.admin'
        RepoModel().grant_user_permission(repo=repo_name, user=self.a1,
                                          perm='repository.write')
        Session().commit()
        # cannot really downgrade admins permissions !? they still gets set as
        # admin !
        assert repo_perms(self.a1)[repo_name] == 'repository.admin'

    def test_default_group_perms(self, repo_name):
        self.g1 = fixture.create_repo_group('test1', skip_if_exists=True)
        self.g2 = fixture.create_repo_group('test2', skip_if_exists=True)

        assert repo_perms(self.u1)[repo_name] == 'repository.read'
        assert group_perms(self.u1) == {
            'test1': 'group.read', 'test2': 'group.read'}
        assert global_perms(self.u1) == set(
            Permission.DEFAULT_USER_PERMISSIONS)

    def test_default_admin_group_perms(self, repo_name):
        self.g1 = fixture.create_repo_group('test1', skip_if_exists=True)
        self.g2 = fixture.create_repo_group('test2', skip_if_exists=True)

        assert repo_perms(self.a1)[repo_name] == 'repository.admin'
        assert group_perms(self.a1) == {
            'test1': 'group.admin', 'test2': 'group.admin'}

    def test_default_owner_group_perms(self):
        # "u1" shall be owner without any special permission assigned
        self.g1 = fixture.create_repo_group('test1')
        assert group_perms(self.u1) == {'test1': 'group.read'}

        # Make him owner, but do not add any special permissions
        self.g1.user = self.u1
        assert group_perms(self.u1) == {'test1': 'group.admin'}

    def test_propagated_permission_from_users_group_by_explicit_perms_exist(
            self, repo_name):
        # make group
        self.ug1 = fixture.create_user_group('G1')
        UserGroupModel().add_user_to_group(self.ug1, self.u1)

        # set permission to lower
        new_perm = 'repository.none'
        RepoModel().grant_user_permission(
            repo=repo_name, user=self.u1, perm=new_perm)
        Session().commit()
        assert repo_perms(self.u1)[repo_name] == new_perm

        # grant perm for group this should not override permission from user
        # since it has explicitly set
        new_perm_gr = 'repository.write'
        RepoModel().grant_user_group_permission(
            repo=repo_name, group_name=self.ug1, perm=new_perm_gr)

        assert repo_perms(self.u1)[repo_name] == new_perm
        assert group_perms(self.u1) == {}

    def test_propagated_permission_from_users_group(self, repo_name):
        # make group
        self.ug1 = fixture.create_user_group('G1')
        UserGroupModel().add_user_to_group(self.ug1, self.u3)

        # grant perm for group
        # this should override default permission from user
        new_perm_gr = 'repository.write'
        RepoModel().grant_user_group_permission(
            repo=repo_name, group_name=self.ug1, perm=new_perm_gr)

        assert repo_perms(self.u3)[repo_name] == new_perm_gr
        assert group_perms(self.u3) == {}

    def test_propagated_permission_from_users_group_lower_weight(
            self, repo_name):
        # make group with user
        self.ug1 = fixture.create_user_group('G1')
        UserGroupModel().add_user_to_group(self.ug1, self.u1)

        # set permission to lower
        new_perm_h = 'repository.write'
        RepoModel().grant_user_permission(
            repo=repo_name, user=self.u1, perm=new_perm_h)
        Session().commit()

        assert repo_perms(self.u1)[repo_name] == new_perm_h

        # grant perm for group this should NOT override permission from user
        # since it's lower than granted
        new_perm_l = 'repository.read'
        RepoModel().grant_user_group_permission(
            repo=repo_name, group_name=self.ug1, perm=new_perm_l)

        assert repo_perms(self.u1)[repo_name] == new_perm_h
        assert group_perms(self.u1) == {}

    def test_repo_in_group_permissions(self):
        self.g1 = fixture.create_repo_group('group1', skip_if_exists=True)
        self.g2 = fixture.create_repo_group('group2', skip_if_exists=True)
        # both perms should be read !
        assert group_perms(self.u1) == \
            {u'group1': u'group.read', u'group2': u'group.read'}

        assert group_perms(self.anon) == \
            {u'group1': u'group.read', u'group2': u'group.read'}

        # Change perms to none for both groups
        RepoGroupModel().grant_user_permission(
            repo_group=self.g1, user=self.anon, perm='group.none')
        RepoGroupModel().grant_user_permission(
            repo_group=self.g2, user=self.anon, perm='group.none')

        assert group_perms(self.u1) == \
            {u'group1': u'group.none', u'group2': u'group.none'}
        assert group_perms(self.anon) == \
            {u'group1': u'group.none', u'group2': u'group.none'}

        # add repo to group
        name = RepoGroup.url_sep().join([self.g1.group_name, 'test_perm'])
        self.test_repo = fixture.create_repo(name=name,
                                             repo_type='hg',
                                             repo_group=self.g1,
                                             cur_user=self.u1,)

        assert group_perms(self.u1) == \
            {u'group1': u'group.none', u'group2': u'group.none'}
        assert group_perms(self.anon) == \
            {u'group1': u'group.none', u'group2': u'group.none'}

        # grant permission for u2 !
        RepoGroupModel().grant_user_permission(
            repo_group=self.g1, user=self.u2, perm='group.read')
        RepoGroupModel().grant_user_permission(
            repo_group=self.g2, user=self.u2, perm='group.read')
        Session().commit()
        assert self.u1 != self.u2

        # u1 and anon should have not change perms while u2 should !
        assert group_perms(self.u1) == \
            {u'group1': u'group.none', u'group2': u'group.none'}
        assert group_perms(self.u2) == \
            {u'group1': u'group.read', u'group2': u'group.read'}
        assert group_perms(self.anon) == \
            {u'group1': u'group.none', u'group2': u'group.none'}

    def test_repo_group_user_as_user_group_member(self):
        # create Group1
        self.g1 = fixture.create_repo_group('group1', skip_if_exists=True)
        assert group_perms(self.anon) == {u'group1': u'group.read'}

        # set default permission to none
        RepoGroupModel().grant_user_permission(
            repo_group=self.g1, user=self.anon, perm='group.none')
        # make group
        self.ug1 = fixture.create_user_group('G1')
        # add user to group
        UserGroupModel().add_user_to_group(self.ug1, self.u1)
        Session().commit()

        # check if user is in the group
        ug1 = UserGroupModel().get(self.ug1.users_group_id)
        members = [x.user_id for x in ug1.members]
        assert members == [self.u1.user_id]
        # add some user to that group

        # check his permissions
        assert group_perms(self.anon) == {u'group1': u'group.none'}
        assert group_perms(self.u1) == {u'group1': u'group.none'}

        # grant ug1 read permissions for
        RepoGroupModel().grant_user_group_permission(
            repo_group=self.g1, group_name=self.ug1, perm='group.read')
        Session().commit()

        # check if the
        obj = Session().query(UserGroupRepoGroupToPerm)\
            .filter(UserGroupRepoGroupToPerm.group == self.g1)\
            .filter(UserGroupRepoGroupToPerm.users_group == self.ug1)\
            .scalar()
        assert obj.permission.permission_name == 'group.read'

        assert group_perms(self.anon) == {u'group1': u'group.none'}
        assert group_perms(self.u1) == {u'group1': u'group.read'}

    def test_inherited_permissions_from_default_on_user_enabled(self):
        # enable fork and create on default user
        _form_result = {
            'default_repo_create': 'hg.create.repository',
            'default_fork_create': 'hg.fork.repository'
        }
        PermissionModel().set_new_user_perms(
            User.get_default_user(), _form_result)
        Session().commit()

        # make sure inherit flag is turned on
        self.u1.inherit_default_permissions = True
        Session().commit()

        # this user will have inherited permissions from default user
        assert global_perms(self.u1) == default_perms()

    def test_inherited_permissions_from_default_on_user_disabled(self):
        # disable fork and create on default user
        _form_result = {
            'default_repo_create': 'hg.create.none',
            'default_fork_create': 'hg.fork.none'
        }
        PermissionModel().set_new_user_perms(
            User.get_default_user(), _form_result)
        Session().commit()

        # make sure inherit flag is turned on
        self.u1.inherit_default_permissions = True
        Session().commit()

        # this user will have inherited permissions from default user
        expected_perms = default_perms(
            added=['hg.create.none', 'hg.fork.none'],
            removed=['hg.create.repository', 'hg.fork.repository'])
        assert global_perms(self.u1) == expected_perms

    def test_non_inherited_permissions_from_default_on_user_enabled(self):
        user_model = UserModel()
        # enable fork and create on default user
        usr = User.DEFAULT_USER
        user_model.revoke_perm(usr, 'hg.create.none')
        user_model.grant_perm(usr, 'hg.create.repository')
        user_model.revoke_perm(usr, 'hg.fork.none')
        user_model.grant_perm(usr, 'hg.fork.repository')

        # disable global perms on specific user
        user_model.revoke_perm(self.u1, 'hg.create.repository')
        user_model.grant_perm(self.u1, 'hg.create.none')
        user_model.revoke_perm(self.u1, 'hg.fork.repository')
        user_model.grant_perm(self.u1, 'hg.fork.none')

        # make sure inherit flag is turned off
        self.u1.inherit_default_permissions = False
        Session().commit()

        # this user will have non inherited permissions from he's
        # explicitly set permissions
        assert global_perms(self.u1) == set([
            'hg.create.none',
            'hg.fork.none',
            'hg.register.manual_activate',
            'hg.extern_activate.auto',
            'repository.read',
            'group.read',
            'usergroup.read',
            ])

    def test_non_inherited_permissions_from_default_on_user_disabled(self):
        user_model = UserModel()
        # disable fork and create on default user
        usr = User.DEFAULT_USER
        user_model.revoke_perm(usr, 'hg.create.repository')
        user_model.grant_perm(usr, 'hg.create.none')
        user_model.revoke_perm(usr, 'hg.fork.repository')
        user_model.grant_perm(usr, 'hg.fork.none')

        # enable global perms on specific user
        user_model.revoke_perm(self.u1, 'hg.create.none')
        user_model.grant_perm(self.u1, 'hg.create.repository')
        user_model.revoke_perm(self.u1, 'hg.fork.none')
        user_model.grant_perm(self.u1, 'hg.fork.repository')

        # make sure inherit flag is turned off
        self.u1.inherit_default_permissions = False
        Session().commit()

        # this user will have non inherited permissions from he's
        # explicitly set permissions
        assert global_perms(self.u1) == set([
            'hg.create.repository',
            'hg.fork.repository',
            'hg.register.manual_activate',
            'hg.extern_activate.auto',
            'repository.read',
            'group.read',
            'usergroup.read',
            ])

    @pytest.mark.parametrize('perm, expected_perm', [
        ('hg.inherit_default_perms.false', 'repository.none', ),
        ('hg.inherit_default_perms.true', 'repository.read', ),
    ])
    def test_inherited_permissions_on_objects(self, perm, expected_perm):
        _form_result = {
            'default_inherit_default_permissions': perm,
        }
        PermissionModel().set_new_user_perms(
            User.get_default_user(), _form_result)
        Session().commit()

        # make sure inherit flag is turned on
        self.u1.inherit_default_permissions = True
        Session().commit()

        # this user will have inherited permissions from default user
        assert global_perms(self.u1) == set([
            'hg.create.none',
            'hg.fork.none',
            'hg.register.manual_activate',
            'hg.extern_activate.auto',
            'repository.read',
            'group.read',
            'usergroup.read',
            'hg.create.write_on_repogroup.true',
            'hg.usergroup.create.false',
            'hg.repogroup.create.false',
            perm,
            ])

        assert set(repo_perms(self.u1).values()) == set([expected_perm])

    def test_repo_owner_permissions_not_overwritten_by_group(self):
        # create repo as USER,
        self.test_repo = fixture.create_repo(name='myownrepo',
                                             repo_type='hg',
                                             cur_user=self.u1)

        # he has permissions of admin as owner
        assert repo_perms(self.u1)['myownrepo'] == 'repository.admin'

        # set his permission as user group, he should still be admin
        self.ug1 = fixture.create_user_group('G1')
        UserGroupModel().add_user_to_group(self.ug1, self.u1)
        RepoModel().grant_user_group_permission(
            self.test_repo,
            group_name=self.ug1,
            perm='repository.none')
        Session().commit()

        assert repo_perms(self.u1)['myownrepo'] == 'repository.admin'

    def test_repo_owner_permissions_not_overwritten_by_others(self):
        # create repo as USER,
        self.test_repo = fixture.create_repo(name='myownrepo',
                                             repo_type='hg',
                                             cur_user=self.u1)

        # he has permissions of admin as owner
        assert repo_perms(self.u1)['myownrepo'] == 'repository.admin'

        # set his permission as user, he should still be admin
        RepoModel().grant_user_permission(
            self.test_repo, user=self.u1, perm='repository.none')
        Session().commit()

        assert repo_perms(self.u1)['myownrepo'] == 'repository.admin'

    def test_repo_group_owner_permissions_not_overwritten_by_group(self):
        # "u1" shall be owner without any special permission assigned
        self.g1 = fixture.create_repo_group('test1')

        # Make user group and grant a permission to user group
        self.ug1 = fixture.create_user_group('G1')
        UserGroupModel().add_user_to_group(self.ug1, self.u1)
        RepoGroupModel().grant_user_group_permission(
            repo_group=self.g1, group_name=self.ug1, perm='group.write')

        # Verify that user does not get any special permission if he is not
        # owner
        assert group_perms(self.u1) == {'test1': 'group.write'}

        # Make him owner of the repo group
        self.g1.user = self.u1
        assert group_perms(self.u1) == {'test1': 'group.admin'}

    def test_repo_group_owner_permissions_not_overwritten_by_others(self):
        # "u1" shall be owner without any special permission assigned
        self.g1 = fixture.create_repo_group('test1')
        RepoGroupModel().grant_user_permission(
            repo_group=self.g1, user=self.u1, perm='group.write')

        # Verify that user does not get any special permission if he is not
        # owner
        assert group_perms(self.u1) == {'test1': 'group.write'}

        # Make him owner of the repo group
        self.g1.user = self.u1
        assert group_perms(self.u1) == {u'test1': 'group.admin'}

    def _test_def_user_perm_equal(
            self, user, change_factor=0, compare_keys=None):
        perms = UserToPerm.query().filter(UserToPerm.user == user).all()
        assert len(perms) == \
            len(Permission.DEFAULT_USER_PERMISSIONS) + change_factor
        if compare_keys:
            assert set(
                x.permissions.permission_name for x in perms) == compare_keys

    def _test_def_user_group_perm_equal(
            self, user_group, change_factor=0, compare_keys=None):
        perms = UserGroupToPerm.query().filter(
            UserGroupToPerm.users_group == user_group).all()
        assert len(perms) == \
            len(Permission.DEFAULT_USER_PERMISSIONS) + change_factor
        if compare_keys:
            assert set(
                x.permissions.permission_name for x in perms) == compare_keys

    def test_set_default_permissions(self):
        PermissionModel().create_default_user_permissions(user=self.u1)
        self._test_def_user_perm_equal(user=self.u1)

    def test_set_default_permissions_after_one_is_missing(self):
        PermissionModel().create_default_user_permissions(user=self.u1)
        self._test_def_user_perm_equal(user=self.u1)
        # now we delete one, it should be re-created after another call
        perms = UserToPerm.query().filter(UserToPerm.user == self.u1).all()
        Session().delete(perms[0])
        Session().commit()

        self._test_def_user_perm_equal(user=self.u1, change_factor=-1)

        # create missing one !
        PermissionModel().create_default_user_permissions(user=self.u1)
        self._test_def_user_perm_equal(user=self.u1)

    @pytest.mark.parametrize("perm, modify_to", [
        ('repository.read', 'repository.none'),
        ('group.read', 'group.none'),
        ('usergroup.read', 'usergroup.none'),
        ('hg.create.repository', 'hg.create.none'),
        ('hg.fork.repository', 'hg.fork.none'),
        ('hg.register.manual_activate', 'hg.register.auto_activate',)
    ])
    def test_set_default_permissions_after_modification(self, perm, modify_to):
        PermissionModel().create_default_user_permissions(user=self.u1)
        self._test_def_user_perm_equal(user=self.u1)

        old = Permission.get_by_key(perm)
        new = Permission.get_by_key(modify_to)
        assert old is not None
        assert new is not None

        # now modify permissions
        p = UserToPerm.query().filter(
            UserToPerm.user == self.u1).filter(
            UserToPerm.permission == old).one()
        p.permission = new
        Session().add(p)
        Session().commit()

        PermissionModel().create_default_user_permissions(user=self.u1)
        self._test_def_user_perm_equal(user=self.u1)

    def test_clear_user_perms(self):
        PermissionModel().create_default_user_permissions(user=self.u1)
        self._test_def_user_perm_equal(user=self.u1)

        # now clear permissions
        cleared = PermissionModel()._clear_user_perms(self.u1.user_id)
        self._test_def_user_perm_equal(user=self.u1,
                                       change_factor=len(cleared)*-1)

    def test_clear_user_group_perms(self):
        self.ug1 = fixture.create_user_group('G1')
        PermissionModel().create_default_user_group_permissions(
            user_group=self.ug1)
        self._test_def_user_group_perm_equal(user_group=self.ug1)

        # now clear permissions
        cleared = PermissionModel()._clear_user_group_perms(
            self.ug1.users_group_id)
        self._test_def_user_group_perm_equal(user_group=self.ug1,
                                             change_factor=len(cleared)*-1)

    @pytest.mark.parametrize("form_result", [
        {},
        {'default_repo_create': 'hg.create.repository'},
        {'default_repo_create': 'hg.create.repository',
         'default_repo_perm': 'repository.read'},
        {'default_repo_create': 'hg.create.none',
         'default_repo_perm': 'repository.write',
         'default_fork_create': 'hg.fork.none'},
    ])
    def test_set_new_user_permissions(self, form_result):
        _form_result = {}
        _form_result.update(form_result)
        PermissionModel().set_new_user_perms(self.u1, _form_result)
        Session().commit()
        change_factor = -1 * (len(Permission.DEFAULT_USER_PERMISSIONS)
                              - len(form_result.keys()))
        self._test_def_user_perm_equal(
            self.u1, change_factor=change_factor)

    @pytest.mark.parametrize("form_result", [
        {},
        {'default_repo_create': 'hg.create.repository'},
        {'default_repo_create': 'hg.create.repository',
         'default_repo_perm': 'repository.read'},
        {'default_repo_create': 'hg.create.none',
         'default_repo_perm': 'repository.write',
         'default_fork_create': 'hg.fork.none'},
    ])
    def test_set_new_user_group_permissions(self, form_result):
        _form_result = {}
        _form_result.update(form_result)
        self.ug1 = fixture.create_user_group('G1')
        PermissionModel().set_new_user_group_perms(self.ug1, _form_result)
        Session().commit()
        change_factor = -1 * (len(Permission.DEFAULT_USER_PERMISSIONS)
                              - len(form_result.keys()))
        self._test_def_user_group_perm_equal(
            self.ug1, change_factor=change_factor)

    @pytest.mark.parametrize("group_active, expected_perm", [
        (True, 'repository.admin'),
        (False, 'repository.read'),
    ])
    def test_get_default_repo_perms_from_user_group_with_active_group(
            self, backend, user_util, group_active, expected_perm):
        repo = backend.create_repo()
        user = user_util.create_user()
        user_group = user_util.create_user_group(
            members=[user], users_group_active=group_active)

        user_util.grant_user_group_permission_to_repo(
            repo, user_group, 'repository.admin')
        permissions = repo_perms(user)
        repo_permission = permissions.get(repo.repo_name)
        assert repo_permission == expected_perm

    @pytest.mark.parametrize("group_active, expected_perm", [
        (True, 'group.admin'),
        (False, 'group.read')
    ])
    def test_get_default_group_perms_from_user_group_with_active_group(
            self, user_util, group_active, expected_perm):
        user = user_util.create_user()
        repo_group = user_util.create_repo_group()
        user_group = user_util.create_user_group(
            members=[user], users_group_active=group_active)

        user_util.grant_user_group_permission_to_repo_group(
            repo_group, user_group, 'group.admin')
        permissions = group_perms(user)
        group_permission = permissions.get(repo_group.name)
        assert group_permission == expected_perm

    @pytest.mark.parametrize("group_active, expected_perm", [
        (True, 'usergroup.admin'),
        (False, 'usergroup.read')
    ])
    def test_get_default_user_group_perms_from_user_group_with_active_group(
            self, user_util, group_active, expected_perm):
        user = user_util.create_user()
        user_group = user_util.create_user_group(
            members=[user], users_group_active=group_active)
        target_user_group = user_util.create_user_group()

        user_util.grant_user_group_permission_to_user_group(
            target_user_group, user_group, 'usergroup.admin')
        permissions = user_group_perms(user)
        group_permission = permissions.get(target_user_group.users_group_name)
        assert group_permission == expected_perm


def repo_perms(user):
    auth_user = AuthUser(user_id=user.user_id)
    return auth_user.permissions['repositories']


def group_perms(user):
    auth_user = AuthUser(user_id=user.user_id)
    return auth_user.permissions['repositories_groups']


def user_group_perms(user):
    auth_user = AuthUser(user_id=user.user_id)
    return auth_user.permissions['user_groups']


def global_perms(user):
    auth_user = AuthUser(user_id=user.user_id)
    return auth_user.permissions['global']


def default_perms(added=None, removed=None):
    expected_perms = set(Permission.DEFAULT_USER_PERMISSIONS)
    if removed:
        expected_perms.difference_update(removed)
    if added:
        expected_perms.update(added)
    return expected_perms
