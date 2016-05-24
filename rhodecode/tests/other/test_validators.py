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


import formencode
import pytest

from rhodecode.tests import (
    HG_REPO, TEST_USER_REGULAR2_EMAIL, TEST_USER_REGULAR2_LOGIN,
    TEST_USER_REGULAR2_PASS, TEST_USER_ADMIN_LOGIN, TESTS_TMP_PATH,
    ldap_lib_installed)

from rhodecode.model import validators as v
from rhodecode.model.user_group import UserGroupModel

from rhodecode.model.meta import Session
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.db import ChangesetStatus, Repository
from rhodecode.model.changeset_status import ChangesetStatusModel
from rhodecode.tests.fixture import Fixture

fixture = Fixture()

pytestmark = pytest.mark.usefixtures('pylonsapp')


def test_Message_extractor():
    validator = v.ValidUsername()
    pytest.raises(formencode.Invalid, validator.to_python, 'default')

    class StateObj(object):
        pass

    pytest.raises(
        formencode.Invalid, validator.to_python, 'default', StateObj)


def test_ValidUsername():
    validator = v.ValidUsername()

    pytest.raises(formencode.Invalid, validator.to_python, 'default')
    pytest.raises(formencode.Invalid, validator.to_python, 'new_user')
    pytest.raises(formencode.Invalid, validator.to_python, '.,')
    pytest.raises(
        formencode.Invalid, validator.to_python, TEST_USER_ADMIN_LOGIN)
    assert 'test' == validator.to_python('test')

    validator = v.ValidUsername(edit=True, old_data={'user_id': 1})


def test_ValidRepoUser():
    validator = v.ValidRepoUser()
    pytest.raises(formencode.Invalid, validator.to_python, 'nouser')
    assert TEST_USER_ADMIN_LOGIN == \
        validator.to_python(TEST_USER_ADMIN_LOGIN)


def test_ValidUserGroup():
    validator = v.ValidUserGroup()
    pytest.raises(formencode.Invalid, validator.to_python, 'default')
    pytest.raises(formencode.Invalid, validator.to_python, '.,')

    gr = fixture.create_user_group('test')
    gr2 = fixture.create_user_group('tes2')
    Session().commit()
    pytest.raises(formencode.Invalid, validator.to_python, 'test')
    assert gr.users_group_id is not None
    validator = v.ValidUserGroup(
        edit=True,
        old_data={'users_group_id': gr2.users_group_id})

    pytest.raises(formencode.Invalid, validator.to_python, 'test')
    pytest.raises(formencode.Invalid, validator.to_python, 'TesT')
    pytest.raises(formencode.Invalid, validator.to_python, 'TEST')
    UserGroupModel().delete(gr)
    UserGroupModel().delete(gr2)
    Session().commit()


@pytest.fixture(scope='function')
def repo_group(request):
    model = RepoGroupModel()
    gr = model.create(
        group_name='test_gr', group_description='desc', just_db=True,
        owner=TEST_USER_ADMIN_LOGIN)

    def cleanup():
        model.delete(gr)

    request.addfinalizer(cleanup)

    return gr


def test_ValidRepoGroup_same_name_as_repo():
    validator = v.ValidRepoGroup()
    with pytest.raises(formencode.Invalid) as excinfo:
        validator.to_python({'group_name': HG_REPO})
    expected_msg = 'Repository with name "vcs_test_hg" already exists'
    assert expected_msg in str(excinfo.value)


def test_ValidRepoGroup_group_exists(repo_group):
    validator = v.ValidRepoGroup()
    with pytest.raises(formencode.Invalid) as excinfo:
        validator.to_python({'group_name': repo_group.group_name})
    expected_msg = 'Group "test_gr" already exists'
    assert expected_msg in str(excinfo.value)


def test_ValidRepoGroup_invalid_parent(repo_group):
    validator = v.ValidRepoGroup(edit=True,
                                 old_data={'group_id': repo_group.group_id})
    with pytest.raises(formencode.Invalid) as excinfo:
        validator.to_python({
            'group_name': repo_group.group_name + 'n',
            'group_parent_id': repo_group.group_id,
        })
    expected_msg = 'Cannot assign this group as parent'
    assert expected_msg in str(excinfo.value)


def test_ValidRepoGroup_edit_group_no_root_permission(repo_group):
    validator = v.ValidRepoGroup(
        edit=True, old_data={'group_id': repo_group.group_id},
        can_create_in_root=False)

    # Cannot change parent
    with pytest.raises(formencode.Invalid) as excinfo:
        validator.to_python({'group_parent_id': '25'})
    expected_msg = 'no permission to store repository group in root location'
    assert expected_msg in str(excinfo.value)

    # Chaning all the other fields is allowed
    validator.to_python({'group_name': 'foo', 'group_parent_id': '-1'})
    validator.to_python(
        {'user': TEST_USER_REGULAR2_LOGIN, 'group_parent_id': '-1'})
    validator.to_python({'group_description': 'bar', 'group_parent_id': '-1'})
    validator.to_python({'enable_locking': 'true', 'group_parent_id': '-1'})


def test_ValidPassword():
    validator = v.ValidPassword()
    assert 'lol' == validator.to_python('lol')
    assert None == validator.to_python(None)
    pytest.raises(formencode.Invalid, validator.to_python, 'ąćżź')


def test_ValidPasswordsMatch():
    validator = v.ValidPasswordsMatch()
    pytest.raises(
        formencode.Invalid,
        validator.to_python, {'password': 'pass',
                              'password_confirmation': 'pass2'})

    pytest.raises(
        formencode.Invalid,
        validator.to_python, {'new_password': 'pass',
                              'password_confirmation': 'pass2'})

    assert {'new_password': 'pass', 'password_confirmation': 'pass'} == \
        validator.to_python({'new_password': 'pass',
                             'password_confirmation': 'pass'})

    assert {'password': 'pass', 'password_confirmation': 'pass'} == \
        validator.to_python({'password': 'pass',
                             'password_confirmation': 'pass'})


def test_ValidAuth(config_stub):
    config_stub.testing_securitypolicy()
    config_stub.include('rhodecode.authentication')

    validator = v.ValidAuth()
    valid_creds = {
        'username': TEST_USER_REGULAR2_LOGIN,
        'password': TEST_USER_REGULAR2_PASS,
    }
    invalid_creds = {
        'username': 'err',
        'password': 'err',
    }
    assert valid_creds == validator.to_python(valid_creds)
    pytest.raises(
        formencode.Invalid, validator.to_python, invalid_creds)


# TODO: johbo: Fix or wipe this test
def test_ValidAuthToken():
    validator = v.ValidAuthToken()
    # this is untestable without a threadlocal
#        pytest.raises(formencode.Invalid,
#                          validator.to_python, 'BadToken')
    validator


def test_ValidRepoName():
    validator = v.ValidRepoName()

    pytest.raises(
        formencode.Invalid, validator.to_python, {'repo_name': ''})

    pytest.raises(
        formencode.Invalid, validator.to_python, {'repo_name': HG_REPO})

    gr = RepoGroupModel().create(group_name='group_test',
                                 group_description='desc',
                                 owner=TEST_USER_ADMIN_LOGIN)
    pytest.raises(
        formencode.Invalid, validator.to_python, {'repo_name': gr.group_name})

    #TODO: write an error case for that ie. create a repo withinh a group
#        pytest.raises(formencode.Invalid,
#                          validator.to_python, {'repo_name': 'some',
#                                                'repo_group': gr.group_id})


def test_ValidForkName():
    # this uses ValidRepoName validator
    assert True

@pytest.mark.parametrize("name, expected", [
    ('test', 'test'), ('lolz!', 'lolz'), ('  aavv', 'aavv'),
    ('ala ma kota', 'ala-ma-kota'), ('@nooo', 'nooo'),
    ('$!haha lolz !', 'haha-lolz'), ('$$$$$', ''), ('{}OK!', 'OK'),
    ('/]re po', 're-po')])
def test_SlugifyName(name, expected):
    validator = v.SlugifyName()
    assert expected == validator.to_python(name)


def test_ValidForkType():
        validator = v.ValidForkType(old_data={'repo_type': 'hg'})
        assert 'hg' == validator.to_python('hg')
        pytest.raises(formencode.Invalid, validator.to_python, 'git')


def test_ValidSettings():
    validator = v.ValidSettings()
    assert {'pass': 'pass'} == \
         validator.to_python(value={'user': 'test',
                                    'pass': 'pass'})

    assert {'user2': 'test', 'pass': 'pass'} == \
         validator.to_python(value={'user2': 'test',
                                    'pass': 'pass'})


def test_ValidPath():
        validator = v.ValidPath()
        assert TESTS_TMP_PATH == validator.to_python(TESTS_TMP_PATH)
        pytest.raises(
            formencode.Invalid, validator.to_python, '/no_such_dir')


def test_UniqSystemEmail():
    validator = v.UniqSystemEmail(old_data={})

    assert 'mail@python.org' == validator.to_python('MaiL@Python.org')

    email = TEST_USER_REGULAR2_EMAIL
    pytest.raises(formencode.Invalid, validator.to_python, email)


def test_ValidSystemEmail():
    validator = v.ValidSystemEmail()
    email = TEST_USER_REGULAR2_EMAIL

    assert email == validator.to_python(email)
    pytest.raises(formencode.Invalid, validator.to_python, 'err')


def test_NotReviewedRevisions():
    repo_id = Repository.get_by_repo_name(HG_REPO).repo_id
    validator = v.NotReviewedRevisions(repo_id)
    rev = '0' * 40
    # add status for a rev, that should throw an error because it is already
    # reviewed
    new_status = ChangesetStatus()
    new_status.author = ChangesetStatusModel()._get_user(TEST_USER_ADMIN_LOGIN)
    new_status.repo = ChangesetStatusModel()._get_repo(HG_REPO)
    new_status.status = ChangesetStatus.STATUS_APPROVED
    new_status.comment = None
    new_status.revision = rev
    Session().add(new_status)
    Session().commit()
    try:
        pytest.raises(formencode.Invalid, validator.to_python, [rev])
    finally:
        Session().delete(new_status)
        Session().commit()
