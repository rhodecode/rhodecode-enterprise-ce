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
import stat
import sys

import pytest
from mock import Mock, patch, DEFAULT

import rhodecode
from rhodecode.model import db, scm


def test_scm_instance_config(backend):
    repo = backend.create_repo()
    with patch.multiple('rhodecode.model.db.Repository',
                        _get_instance=DEFAULT,
                        _get_instance_cached=DEFAULT) as mocks:
        repo.scm_instance()
        mocks['_get_instance'].assert_called_with(
            config=None, cache=False)

        config = {'some': 'value'}
        repo.scm_instance(config=config)
        mocks['_get_instance'].assert_called_with(
            config=config, cache=False)

        with patch.dict(rhodecode.CONFIG, {'vcs_full_cache': 'true'}):
            repo.scm_instance(config=config)
            mocks['_get_instance_cached'].assert_called()


def test__get_instance_config(backend):
    repo = backend.create_repo()
    vcs_class = Mock()
    with patch.multiple('rhodecode.model.db',
                        get_scm=DEFAULT,
                        get_backend=DEFAULT) as mocks:
        mocks['get_scm'].return_value = backend.alias
        mocks['get_backend'].return_value = vcs_class
        with patch('rhodecode.model.db.Repository._config') as config_mock:
            repo._get_instance()
            vcs_class.assert_called_with(
                repo.repo_full_path, config=config_mock, create=False,
                with_wire={'cache': True})

        new_config = {'override': 'old_config'}
        repo._get_instance(config=new_config)
        vcs_class.assert_called_with(
            repo.repo_full_path, config=new_config, create=False,
            with_wire={'cache': True})


def test_mark_for_invalidation_config(backend):
    repo = backend.create_repo()
    with patch('rhodecode.model.db.Repository.update_commit_cache') as _mock:
        scm.ScmModel().mark_for_invalidation(repo.repo_name)
        _, kwargs = _mock.call_args
        assert kwargs['config'].__dict__ == repo._config.__dict__


def test_strip_with_multiple_heads(backend_hg):
    commits = [
        {'message': 'A'},
        {'message': 'a'},
        {'message': 'b'},
        {'message': 'B', 'parents': ['A']},
        {'message': 'a1'},
    ]
    repo = backend_hg.create_repo(commits=commits)
    commit_ids = backend_hg.commit_ids

    model = scm.ScmModel()
    model.strip(repo, commit_ids['b'], branch=None)

    vcs_repo = repo.scm_instance()
    rest_commit_ids = [c.raw_id for c in vcs_repo.get_changesets()]
    assert len(rest_commit_ids) == 4
    assert commit_ids['b'] not in rest_commit_ids


def test_strip_with_single_heads(backend_hg):
    commits = [
        {'message': 'A'},
        {'message': 'a'},
        {'message': 'b'},
    ]
    repo = backend_hg.create_repo(commits=commits)
    commit_ids = backend_hg.commit_ids

    model = scm.ScmModel()
    model.strip(repo, commit_ids['b'], branch=None)

    vcs_repo = repo.scm_instance()
    rest_commit_ids = [c.raw_id for c in vcs_repo.get_changesets()]
    assert len(rest_commit_ids) == 2
    assert commit_ids['b'] not in rest_commit_ids


def test_get_nodes_returns_unicode_flat(backend_random):
    repo = backend_random.repo
    directories, files = scm.ScmModel().get_nodes(
        repo.repo_name, repo.get_commit(commit_idx=0).raw_id,
        flat=True)
    assert_contains_only_unicode(directories)
    assert_contains_only_unicode(files)


def test_get_nodes_returns_unicode_non_flat(backend_random):
    repo = backend_random.repo
    directories, files = scm.ScmModel().get_nodes(
        repo.repo_name, repo.get_commit(commit_idx=0).raw_id,
        flat=False)
    # johbo: Checking only the names for now, since that is the critical
    # part.
    assert_contains_only_unicode([d['name'] for d in directories])
    assert_contains_only_unicode([f['name'] for f in files])


def assert_contains_only_unicode(structure):
    assert structure
    for value in structure:
        assert isinstance(value, unicode)


@pytest.mark.backends("hg", "git")
def test_get_non_unicode_reference(backend):
    model = scm.ScmModel()
    non_unicode_list = ["Adını".decode("cp1254")]

    def scm_instance():
        return Mock(
            branches=non_unicode_list, bookmarks=non_unicode_list,
            tags=non_unicode_list, alias=backend.alias)

    repo = Mock(__class__=db.Repository, scm_instance=scm_instance)
    choices, __ = model.get_repo_landing_revs(repo=repo)
    if backend.alias == 'hg':
        valid_choices = [
            'rev:tip', u'branch:Ad\xc4\xb1n\xc4\xb1',
            u'book:Ad\xc4\xb1n\xc4\xb1', u'tag:Ad\xc4\xb1n\xc4\xb1']
    else:
        valid_choices = [
            'rev:tip', u'branch:Ad\xc4\xb1n\xc4\xb1',
            u'tag:Ad\xc4\xb1n\xc4\xb1']

    assert choices == valid_choices


class TestInstallSvnHooks(object):
    HOOK_FILES = ('pre-commit', 'post-commit')

    def test_new_hooks_are_created(self, backend_svn):
        model = scm.ScmModel()
        repo = backend_svn.create_repo()
        vcs_repo = repo.scm_instance()
        model.install_svn_hooks(vcs_repo)

        hooks_path = os.path.join(vcs_repo.path, 'hooks')
        assert os.path.isdir(hooks_path)
        for file_name in self.HOOK_FILES:
            file_path = os.path.join(hooks_path, file_name)
            self._check_hook_file_mode(file_path)
            self._check_hook_file_content(file_path)

    def test_rc_hooks_are_replaced(self, backend_svn):
        model = scm.ScmModel()
        repo = backend_svn.create_repo()
        vcs_repo = repo.scm_instance()
        hooks_path = os.path.join(vcs_repo.path, 'hooks')
        file_paths = [os.path.join(hooks_path, f) for f in self.HOOK_FILES]

        for file_path in file_paths:
            self._create_fake_hook(
                file_path, content="RC_HOOK_VER = 'abcde'\n")

        model.install_svn_hooks(vcs_repo)

        for file_path in file_paths:
            self._check_hook_file_content(file_path)

    def test_non_rc_hooks_are_not_replaced_without_force_create(
            self, backend_svn):
        model = scm.ScmModel()
        repo = backend_svn.create_repo()
        vcs_repo = repo.scm_instance()
        hooks_path = os.path.join(vcs_repo.path, 'hooks')
        file_paths = [os.path.join(hooks_path, f) for f in self.HOOK_FILES]
        non_rc_content = "exit 0\n"

        for file_path in file_paths:
            self._create_fake_hook(file_path, content=non_rc_content)

        model.install_svn_hooks(vcs_repo)

        for file_path in file_paths:
            with open(file_path, 'rt') as hook_file:
                content = hook_file.read()
            assert content == non_rc_content

    def test_non_rc_hooks_are_replaced_with_force_create(self, backend_svn):
        model = scm.ScmModel()
        repo = backend_svn.create_repo()
        vcs_repo = repo.scm_instance()
        hooks_path = os.path.join(vcs_repo.path, 'hooks')
        file_paths = [os.path.join(hooks_path, f) for f in self.HOOK_FILES]
        non_rc_content = "exit 0\n"

        for file_path in file_paths:
            self._create_fake_hook(file_path, content=non_rc_content)

        model.install_svn_hooks(vcs_repo, force_create=True)

        for file_path in file_paths:
            self._check_hook_file_content(file_path)

    def _check_hook_file_mode(self, file_path):
        assert os.path.exists(file_path)
        stat_info = os.stat(file_path)

        file_mode = stat.S_IMODE(stat_info.st_mode)
        expected_mode = int('755', 8)
        assert expected_mode == file_mode

    def _check_hook_file_content(self, file_path):
        with open(file_path, 'rt') as hook_file:
            content = hook_file.read()

        expected_env = '#!{}'.format(sys.executable)
        expected_rc_version = "\nRC_HOOK_VER = '{}'\n".format(
            rhodecode.__version__)
        assert content.strip().startswith(expected_env)
        assert expected_rc_version in content

    def _create_fake_hook(self, file_path, content):
        with open(file_path, 'w') as hook_file:
            hook_file.write(content)


class TestCheckRhodecodeHook(object):

    @patch('os.path.exists', Mock(return_value=False))
    def test_returns_true_when_no_hook_found(self):
        result = scm._check_rhodecode_hook('/tmp/fake_hook_file.py')
        assert result

    @pytest.mark.parametrize("file_content, expected_result", [
        ("RC_HOOK_VER = '3.3.3'\n", True),
        ("RC_HOOK = '3.3.3'\n", False),
    ])
    @patch('os.path.exists', Mock(return_value=True))
    def test_signatures(self, file_content, expected_result):
        hook_content_patcher = patch.object(
            scm, '_read_hook', return_value=file_content)
        with hook_content_patcher:
            result = scm._check_rhodecode_hook('/tmp/fake_hook_file.py')

        assert result is expected_result


class TestInstallHooks(object):
    def test_hooks_are_installed_for_git_repo(self, backend_git):
        repo = backend_git.create_repo()
        model = scm.ScmModel()
        scm_repo = repo.scm_instance()
        with patch.object(model, 'install_git_hook') as hooks_mock:
            model.install_hooks(scm_repo, repo_type='git')
        hooks_mock.assert_called_once_with(scm_repo)

    def test_hooks_are_installed_for_svn_repo(self, backend_svn):
        repo = backend_svn.create_repo()
        scm_repo = repo.scm_instance()
        model = scm.ScmModel()
        with patch.object(scm.ScmModel, 'install_svn_hooks') as hooks_mock:
            model.install_hooks(scm_repo, repo_type='svn')
        hooks_mock.assert_called_once_with(scm_repo)

    @pytest.mark.parametrize('hook_method', [
        'install_svn_hooks',
        'install_git_hook'])
    def test_mercurial_doesnt_trigger_hooks(self, backend_hg, hook_method):
        repo = backend_hg.create_repo()
        scm_repo = repo.scm_instance()
        model = scm.ScmModel()
        with patch.object(scm.ScmModel, hook_method) as hooks_mock:
            model.install_hooks(scm_repo, repo_type='hg')
        assert hooks_mock.call_count == 0
