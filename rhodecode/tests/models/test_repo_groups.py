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

from sqlalchemy.exc import IntegrityError
import pytest

from rhodecode.tests import TESTS_TMP_PATH
from rhodecode.tests.fixture import Fixture

from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.repo import RepoModel
from rhodecode.model.db import RepoGroup
from rhodecode.model.meta import Session


fixture = Fixture()


def _update_group(id_, group_name, desc='desc', parent_id=None):
    form_data = fixture._get_group_create_params(group_name=group_name,
                                                 group_desc=desc,
                                                 group_parent_id=parent_id)
    gr = RepoGroupModel().update(id_, form_data)
    return gr


def _update_repo(name, **kwargs):
    form_data = fixture._get_repo_create_params(**kwargs)
    if 'repo_name' not in kwargs:
        form_data['repo_name'] = name

    if 'perm_additions' not in kwargs:
        form_data['perm_additions'] = []
    if 'perm_updates' not in kwargs:
        form_data['perm_updates'] = []
    if 'perm_deletions' not in kwargs:
        form_data['perm_deletions'] = []

    r = RepoModel().update(name, **form_data)
    return r


class TestRepoGroups:

    @pytest.fixture(autouse=True)
    def prepare(self, request):
        self.g1 = fixture.create_repo_group('test1', skip_if_exists=True)
        self.g2 = fixture.create_repo_group('test2', skip_if_exists=True)
        self.g3 = fixture.create_repo_group('test3', skip_if_exists=True)
        request.addfinalizer(Session.remove)

    def __check_path(self, *path):
        """
        Checks the path for existance !
        """
        path = [TESTS_TMP_PATH] + list(path)
        path = os.path.join(*path)
        return os.path.isdir(path)

    def __delete_group(self, id_):
        RepoGroupModel().delete(id_)

    def test_create_group(self):
        g = fixture.create_repo_group('newGroup')
        Session().commit()
        assert g.full_path == 'newGroup'

        assert self.__check_path('newGroup')

    def test_create_same_name_group(self):
        with pytest.raises(IntegrityError):
            fixture.create_repo_group('newGroup')
        Session().rollback()

    def test_same_subgroup(self):
        sg1 = fixture.create_repo_group('test1/sub1')
        assert sg1.parent_group == self.g1
        assert sg1.full_path == 'test1/sub1'
        assert self.__check_path('test1', 'sub1')

        ssg1 = fixture.create_repo_group('test1/sub1/subsub1')
        assert ssg1.parent_group == sg1
        assert ssg1.full_path == 'test1/sub1/subsub1'
        assert self.__check_path('test1', 'sub1', 'subsub1')

    def test_remove_group(self):
        sg1 = fixture.create_repo_group('deleteme')
        self.__delete_group(sg1.group_id)

        assert RepoGroup.get(sg1.group_id) is None
        assert not self.__check_path('deteteme')

        sg1 = fixture.create_repo_group('test1/deleteme')
        self.__delete_group(sg1.group_id)

        assert RepoGroup.get(sg1.group_id) is None
        assert not self.__check_path('test1', 'deteteme')

    def test_rename_single_group(self):
        sg1 = fixture.create_repo_group('initial')

        _update_group(sg1.group_id, 'after')
        assert self.__check_path('after')
        assert RepoGroup.get_by_group_name('initial') is None

    def test_update_group_parent(self):

        sg1 = fixture.create_repo_group('test1/initial')

        _update_group(sg1.group_id, 'after', parent_id=self.g1.group_id)
        assert self.__check_path('test1', 'after')
        assert RepoGroup.get_by_group_name('test1/initial') is None

        _update_group(sg1.group_id, 'after', parent_id=self.g3.group_id)
        assert self.__check_path('test3', 'after')
        assert RepoGroup.get_by_group_name('test3/initial') is None

        new_sg1 = _update_group(sg1.group_id, 'hello')
        assert self.__check_path('hello')

        assert RepoGroup.get_by_group_name('hello') == new_sg1

    def test_subgrouping_with_repo(self):

        g1 = fixture.create_repo_group('g1')
        g2 = fixture.create_repo_group('g2')
        # create new repo
        r = fixture.create_repo('john')

        assert r.repo_name == 'john'
        # put repo into group
        r = _update_repo('john', repo_group=g1.group_id)
        Session().commit()
        assert r.repo_name == 'g1/john'

        _update_group(g1.group_id, 'g1', parent_id=g2.group_id)
        assert self.__check_path('g2', 'g1')

        # test repo
        assert r.repo_name == RepoGroup.url_sep().join(
            ['g2', 'g1', r.just_name])

    def test_move_to_root(self):
        fixture.create_repo_group('t11')
        g2 = fixture.create_repo_group('t11/t22')

        assert g2.full_path == 't11/t22'
        assert self.__check_path('t11', 't22')

        g2 = _update_group(g2.group_id, 'g22', parent_id=None)
        Session().commit()

        assert g2.group_name == 'g22'
        # we moved out group from t1 to '' so it's full path should be 'g2'
        assert g2.full_path == 'g22'
        assert not self.__check_path('t11', 't22')
        assert self.__check_path('g22')

    def test_rename_top_level_group_in_nested_setup(self):
        g1 = fixture.create_repo_group('L1')
        g2 = fixture.create_repo_group('L1/L2')
        g3 = fixture.create_repo_group('L1/L2/L3')

        r = fixture.create_repo('L1/L2/L3/L3_REPO', repo_group=g3.group_id)

        # rename L1 all groups should be now changed
        _update_group(g1.group_id, 'L1_NEW')
        Session().commit()
        assert g1.full_path == 'L1_NEW'
        assert g2.full_path == 'L1_NEW/L2'
        assert g3.full_path == 'L1_NEW/L2/L3'
        assert r.repo_name == 'L1_NEW/L2/L3/L3_REPO'

    def test_change_parent_of_top_level_group_in_nested_setup(self):
        g1 = fixture.create_repo_group('R1')
        g2 = fixture.create_repo_group('R1/R2')
        g3 = fixture.create_repo_group('R1/R2/R3')
        g4 = fixture.create_repo_group('R1_NEW')

        r = fixture.create_repo('R1/R2/R3/R3_REPO', repo_group=g3.group_id)
        # rename L1 all groups should be now changed
        _update_group(g1.group_id, 'R1', parent_id=g4.group_id)
        Session().commit()
        assert g1.full_path == 'R1_NEW/R1'
        assert g2.full_path == 'R1_NEW/R1/R2'
        assert g3.full_path == 'R1_NEW/R1/R2/R3'
        assert r.repo_name == 'R1_NEW/R1/R2/R3/R3_REPO'

    def test_change_parent_of_top_level_group_in_nested_setup_with_rename(
            self):
        g1 = fixture.create_repo_group('X1')
        g2 = fixture.create_repo_group('X1/X2')
        g3 = fixture.create_repo_group('X1/X2/X3')
        g4 = fixture.create_repo_group('X1_NEW')

        r = fixture.create_repo('X1/X2/X3/X3_REPO', repo_group=g3.group_id)

        # rename L1 all groups should be now changed
        _update_group(g1.group_id, 'X1_PRIM', parent_id=g4.group_id)
        Session().commit()
        assert g1.full_path == 'X1_NEW/X1_PRIM'
        assert g2.full_path == 'X1_NEW/X1_PRIM/X2'
        assert g3.full_path == 'X1_NEW/X1_PRIM/X2/X3'
        assert r.repo_name == 'X1_NEW/X1_PRIM/X2/X3/X3_REPO'
