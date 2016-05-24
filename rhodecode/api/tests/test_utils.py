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
from mock import Mock, patch

from rhodecode.api import utils
from rhodecode.api import JSONRPCError
from rhodecode.lib.vcs.exceptions import RepositoryError


class TestGetCommitOrError(object):
    def setup(self):
        self.commit_hash = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa10'

    @pytest.mark.parametrize("ref", ['ref', '12345', 'a:b:c:d', 'branch:name'])
    def test_ref_cannot_be_parsed(self, ref):
        repo = Mock()
        with pytest.raises(JSONRPCError) as excinfo:
            utils.get_commit_or_error(ref, repo)
        expected_message = (
            'Ref `{ref}` given in a wrong format. Please check the API'
            ' documentation for more details'.format(ref=ref)
        )
        assert excinfo.value.message == expected_message

    def test_success_with_hash_specified(self):
        repo = Mock()
        ref_type = 'branch'
        ref = '{}:master:{}'.format(ref_type, self.commit_hash)

        with patch('rhodecode.api.utils.get_commit_from_ref_name') as get_commit:
            result = utils.get_commit_or_error(ref, repo)
            get_commit.assert_called_once_with(
                repo, self.commit_hash)
            assert result == get_commit()

    def test_raises_an_error_when_commit_not_found(self):
        repo = Mock()
        ref = 'branch:master:{}'.format(self.commit_hash)

        with patch('rhodecode.api.utils.get_commit_from_ref_name') as get_commit:
            get_commit.side_effect = RepositoryError('Commit not found')
            with pytest.raises(JSONRPCError) as excinfo:
                utils.get_commit_or_error(ref, repo)
            expected_message = 'Ref `{}` does not exist'.format(ref)
            assert excinfo.value.message == expected_message


class TestResolveRefOrError(object):
    def setup(self):
        self.commit_hash = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa10'

    def test_success_with_no_hash_specified(self):
        repo = Mock()
        ref_type = 'branch'
        ref_name = 'master'
        ref = '{}:{}'.format(ref_type, ref_name)

        with patch('rhodecode.api.utils._get_ref_hash') \
                as _get_ref_hash:
            _get_ref_hash.return_value = self.commit_hash
            result = utils.resolve_ref_or_error(ref, repo)
            _get_ref_hash.assert_called_once_with(repo, ref_type, ref_name)
            assert result == '{}:{}'.format(ref, self.commit_hash)

    def test_non_supported_refs(self):
        repo = Mock()
        ref = 'ancestor:ref'
        with pytest.raises(JSONRPCError) as excinfo:
            utils.resolve_ref_or_error(ref, repo)
        expected_message = 'The specified ancestor `ref` does not exist'
        assert excinfo.value.message == expected_message

    def test_branch_is_not_found(self):
        repo = Mock()
        ref = 'branch:non-existing-one'
        with patch('rhodecode.api.utils._get_ref_hash')\
                as _get_ref_hash:
            _get_ref_hash.side_effect = KeyError()
            with pytest.raises(JSONRPCError) as excinfo:
                utils.resolve_ref_or_error(ref, repo)
        expected_message = (
            'The specified branch `non-existing-one` does not exist')
        assert excinfo.value.message == expected_message

    def test_bookmark_is_not_found(self):
        repo = Mock()
        ref = 'bookmark:non-existing-one'
        with patch('rhodecode.api.utils._get_ref_hash')\
                as _get_ref_hash:
            _get_ref_hash.side_effect = KeyError()
            with pytest.raises(JSONRPCError) as excinfo:
                utils.resolve_ref_or_error(ref, repo)
        expected_message = (
            'The specified bookmark `non-existing-one` does not exist')
        assert excinfo.value.message == expected_message

    @pytest.mark.parametrize("ref", ['ref', '12345', 'a:b:c:d'])
    def test_ref_cannot_be_parsed(self, ref):
        repo = Mock()
        with pytest.raises(JSONRPCError) as excinfo:
            utils.resolve_ref_or_error(ref, repo)
        expected_message = (
            'Ref `{ref}` given in a wrong format. Please check the API'
            ' documentation for more details'.format(ref=ref)
        )
        assert excinfo.value.message == expected_message


class TestGetRefHash(object):
    def setup(self):
        self.commit_hash = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa10'
        self.bookmark_name = 'test-bookmark'

    @pytest.mark.parametrize("alias, branch_name", [
        ("git", "master"),
        ("hg", "default")
    ])
    def test_returns_hash_by_branch_name(self, alias, branch_name):
        with patch('rhodecode.model.db.Repository') as repo:
            repo.scm_instance().alias = alias
            repo.scm_instance().branches = {branch_name: self.commit_hash}
            result_hash = utils._get_ref_hash(repo, 'branch', branch_name)
            assert result_hash == self.commit_hash

    @pytest.mark.parametrize("alias, branch_name", [
        ("git", "master"),
        ("hg", "default")
    ])
    def test_raises_error_when_branch_is_not_found(self, alias, branch_name):
        with patch('rhodecode.model.db.Repository') as repo:
            repo.scm_instance().alias = alias
            repo.scm_instance().branches = {}
            with pytest.raises(KeyError):
                utils._get_ref_hash(repo, 'branch', branch_name)

    def test_returns_hash_when_bookmark_is_specified_for_hg(self):
        with patch('rhodecode.model.db.Repository') as repo:
            repo.scm_instance().alias = 'hg'
            repo.scm_instance().bookmarks = {
                self.bookmark_name: self.commit_hash}
            result_hash = utils._get_ref_hash(
                repo, 'bookmark', self.bookmark_name)
            assert result_hash == self.commit_hash

    def test_raises_error_when_bookmark_is_not_found_in_hg_repo(self):
        with patch('rhodecode.model.db.Repository') as repo:
            repo.scm_instance().alias = 'hg'
            repo.scm_instance().bookmarks = {}
            with pytest.raises(KeyError):
                utils._get_ref_hash(repo, 'bookmark', self.bookmark_name)

    def test_raises_error_when_bookmark_is_specified_for_git(self):
        with patch('rhodecode.model.db.Repository') as repo:
            repo.scm_instance().alias = 'git'
            repo.scm_instance().bookmarks = {
                self.bookmark_name: self.commit_hash}
            with pytest.raises(ValueError):
                utils._get_ref_hash(repo, 'bookmark', self.bookmark_name)


class TestUserByNameOrError(object):
    def test_user_found_by_id(self):
        fake_user = Mock(id=123)
        patcher = patch('rhodecode.model.user.UserModel.get_user')
        with patcher as get_user:
            get_user.return_value = fake_user
            result = utils.get_user_or_error('123')
            assert result == fake_user

    def test_user_found_by_name(self):
        fake_user = Mock(id=123)
        patcher = patch('rhodecode.model.user.UserModel.get_by_username')
        with patcher as get_by_username:
            get_by_username.return_value = fake_user
            result = utils.get_user_or_error('test')
            assert result == fake_user

    def test_user_not_found_by_id(self):
        patcher = patch('rhodecode.model.user.UserModel.get_user')
        with patcher as get_user:
            get_user.return_value = None
            with pytest.raises(JSONRPCError) as excinfo:
                utils.get_user_or_error('123')

        expected_message = 'user `123` does not exist'
        assert excinfo.value.message == expected_message

    def test_user_not_found_by_name(self):
        patcher = patch('rhodecode.model.user.UserModel.get_by_username')
        with patcher as get_by_username:
            get_by_username.return_value = None
            with pytest.raises(JSONRPCError) as excinfo:
                utils.get_user_or_error('test')

        expected_message = 'user `test` does not exist'
        assert excinfo.value.message == expected_message


class TestGetCommitDict:

    @pytest.mark.parametrize('filename, expected', [
        (b'sp\xc3\xa4cial', u'sp\xe4cial'),
        (b'sp\xa4cial', u'sp\ufffdcial'),
    ])
    def test_decodes_filenames_to_unicode(self, filename, expected):
        result = utils._get_commit_dict(filename=filename, op='A')
        assert result['filename'] == expected


class TestRepoAccess(object):
    def setup_method(self, method):

        self.admin_perm_patch = patch(
            'rhodecode.api.utils.HasPermissionAnyApi')
        self.repo_perm_patch = patch(
            'rhodecode.api.utils.HasRepoPermissionAnyApi')

    def test_has_superadmin_permission_checks_for_admin(self):
        admin_mock = Mock()
        with self.admin_perm_patch as amock:
            amock.return_value = admin_mock
            assert utils.has_superadmin_permission('fake_user')
            amock.assert_called_once_with('hg.admin')

        admin_mock.assert_called_once_with(user='fake_user')

    def test_has_repo_permissions_checks_for_repo_access(self):
        repo_mock = Mock()
        fake_repo = Mock()
        with self.repo_perm_patch as rmock:
            rmock.return_value = repo_mock
            assert utils.has_repo_permissions(
                'fake_user', 'fake_repo_id', fake_repo,
                ['perm1', 'perm2'])
            rmock.assert_called_once_with(*['perm1', 'perm2'])

        repo_mock.assert_called_once_with(
            user='fake_user', repo_name=fake_repo.repo_name)

    def test_has_repo_permissions_raises_not_found(self):
        repo_mock = Mock(return_value=False)
        fake_repo = Mock()
        with self.repo_perm_patch as rmock:
            rmock.return_value = repo_mock
            with pytest.raises(JSONRPCError) as excinfo:
                utils.has_repo_permissions(
                    'fake_user', 'fake_repo_id', fake_repo, 'perms')
                assert 'fake_repo_id' in excinfo
