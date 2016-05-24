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

import json
import multiprocessing
import os

import mock
import py
import pytest

from rhodecode.lib import caching_query
from rhodecode.lib import utils
from rhodecode.lib.utils2 import md5
from rhodecode.model import db
from rhodecode.model import meta
from rhodecode.model.repo import RepoModel
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.scm import ScmModel
from rhodecode.model.settings import UiSetting, SettingsModel
from rhodecode.tests.fixture import Fixture
from rhodecode.tests import TEST_USER_ADMIN_LOGIN


fixture = Fixture()


def extract_hooks(config):
    """Return a dictionary with the hook entries of the given config."""
    hooks = {}
    config_items = config.serialize()
    for section, name, value in config_items:
        if section != 'hooks':
            continue
        hooks[name] = value

    return hooks


def disable_hooks(request, hooks):
    """Disables the given hooks from the UI settings."""
    session = meta.Session()

    model = SettingsModel()
    for hook_key in hooks:
        sett = model.get_ui_by_key(hook_key)
        sett.ui_active = False
        session.add(sett)

    # Invalidate cache
    ui_settings = session.query(db.RhodeCodeUi).options(
        caching_query.FromCache('sql_cache_short', 'get_hg_ui_settings'))
    ui_settings.invalidate()

    ui_settings = session.query(db.RhodeCodeUi).options(
        caching_query.FromCache(
            'sql_cache_short', 'get_hook_settings', 'get_hook_settings'))
    ui_settings.invalidate()

    @request.addfinalizer
    def rollback():
        session.rollback()


HOOK_PRE_PUSH = db.RhodeCodeUi.HOOK_PRE_PUSH
HOOK_PUSH = db.RhodeCodeUi.HOOK_PUSH
HOOK_PRE_PULL = db.RhodeCodeUi.HOOK_PRE_PULL
HOOK_PULL = db.RhodeCodeUi.HOOK_PULL
HOOK_REPO_SIZE = db.RhodeCodeUi.HOOK_REPO_SIZE

HG_HOOKS = frozenset(
    (HOOK_PRE_PULL, HOOK_PULL, HOOK_PRE_PUSH, HOOK_PUSH, HOOK_REPO_SIZE))


@pytest.mark.parametrize('disabled_hooks,expected_hooks', [
    ([], HG_HOOKS),
    ([HOOK_PRE_PUSH, HOOK_REPO_SIZE], [HOOK_PRE_PULL, HOOK_PULL, HOOK_PUSH]),
    (HG_HOOKS, []),
    # When a pull/push hook is disabled, its pre-pull/push counterpart should
    # be disabled too.
    ([HOOK_PUSH], [HOOK_PRE_PULL, HOOK_PULL, HOOK_REPO_SIZE]),
    ([HOOK_PULL], [HOOK_PRE_PUSH, HOOK_PUSH, HOOK_REPO_SIZE]),
])
def test_make_db_config_hg_hooks(pylonsapp, request, disabled_hooks,
                                 expected_hooks):
    disable_hooks(request, disabled_hooks)

    config = utils.make_db_config()
    hooks = extract_hooks(config)

    assert set(hooks.iterkeys()).intersection(HG_HOOKS) == set(expected_hooks)


@pytest.mark.parametrize('disabled_hooks,expected_hooks', [
    ([], ['pull', 'push']),
    ([HOOK_PUSH], ['pull']),
    ([HOOK_PULL], ['push']),
    ([HOOK_PULL, HOOK_PUSH], []),
])
def test_get_enabled_hook_classes(disabled_hooks, expected_hooks):
    hook_keys = (HOOK_PUSH, HOOK_PULL)
    ui_settings = [
        ('hooks', key, 'some value', key not in disabled_hooks)
        for key in hook_keys]

    result = utils.get_enabled_hook_classes(ui_settings)
    assert sorted(result) == expected_hooks


def test_get_filesystem_repos_finds_repos(tmpdir, pylonsapp):
    _stub_git_repo(tmpdir.ensure('repo', dir=True))
    repos = list(utils.get_filesystem_repos(str(tmpdir)))
    assert repos == [('repo', ('git', tmpdir.join('repo')))]


def test_get_filesystem_repos_skips_directories(tmpdir, pylonsapp):
    tmpdir.ensure('not-a-repo', dir=True)
    repos = list(utils.get_filesystem_repos(str(tmpdir)))
    assert repos == []


def test_get_filesystem_repos_skips_directories_with_repos(tmpdir, pylonsapp):
    _stub_git_repo(tmpdir.ensure('subdir/repo', dir=True))
    repos = list(utils.get_filesystem_repos(str(tmpdir)))
    assert repos == []


def test_get_filesystem_repos_finds_repos_in_subdirectories(tmpdir, pylonsapp):
    _stub_git_repo(tmpdir.ensure('subdir/repo', dir=True))
    repos = list(utils.get_filesystem_repos(str(tmpdir), recursive=True))
    assert repos == [('subdir/repo', ('git', tmpdir.join('subdir', 'repo')))]


def test_get_filesystem_repos_skips_names_starting_with_dot(tmpdir):
    _stub_git_repo(tmpdir.ensure('.repo', dir=True))
    repos = list(utils.get_filesystem_repos(str(tmpdir)))
    assert repos == []


def test_get_filesystem_repos_skips_files(tmpdir):
    tmpdir.ensure('test-file')
    repos = list(utils.get_filesystem_repos(str(tmpdir)))
    assert repos == []


def test_get_filesystem_repos_skips_removed_repositories(tmpdir):
    removed_repo_name = 'rm__00000000_000000_000000__.stub'
    assert utils.REMOVED_REPO_PAT.match(removed_repo_name)
    _stub_git_repo(tmpdir.ensure(removed_repo_name, dir=True))
    repos = list(utils.get_filesystem_repos(str(tmpdir)))
    assert repos == []


def _stub_git_repo(repo_path):
    """
    Make `repo_path` look like a Git repository.
    """
    repo_path.ensure('.git', dir=True)


@pytest.mark.parametrize('str_class', [str, unicode], ids=['str', 'unicode'])
def test_get_dirpaths_returns_all_paths(tmpdir, str_class):
    tmpdir.ensure('test-file')
    dirpaths = utils._get_dirpaths(str_class(tmpdir))
    assert dirpaths == ['test-file']


def test_get_dirpaths_returns_all_paths_bytes(
        tmpdir, platform_encodes_filenames):
    if platform_encodes_filenames:
        pytest.skip("This platform seems to encode filenames.")
    tmpdir.ensure('repo-a-umlaut-\xe4')
    dirpaths = utils._get_dirpaths(str(tmpdir))
    assert dirpaths == ['repo-a-umlaut-\xe4']


def test_get_dirpaths_skips_paths_it_cannot_decode(
        tmpdir, platform_encodes_filenames):
    if platform_encodes_filenames:
        pytest.skip("This platform seems to encode filenames.")
    path_with_latin1 = 'repo-a-umlaut-\xe4'
    tmpdir.ensure(path_with_latin1)
    dirpaths = utils._get_dirpaths(unicode(tmpdir))
    assert dirpaths == []


@pytest.fixture(scope='session')
def platform_encodes_filenames():
    """
    Boolean indicator if the current platform changes filename encodings.
    """
    path_with_latin1 = 'repo-a-umlaut-\xe4'
    tmpdir = py.path.local.mkdtemp()
    tmpdir.ensure(path_with_latin1)
    read_path = tmpdir.listdir()[0].basename
    tmpdir.remove()
    return path_with_latin1 != read_path


def test_action_logger_action_size(pylonsapp, test_repo):
    action = 'x' * 1200001
    utils.action_logger(TEST_USER_ADMIN_LOGIN, action, test_repo, commit=True)


@pytest.fixture
def repo_groups(request):
    session = meta.Session()
    zombie_group = fixture.create_repo_group('zombie')
    parent_group = fixture.create_repo_group('parent')
    child_group = fixture.create_repo_group('parent/child')
    groups_in_db = session.query(db.RepoGroup).all()
    assert len(groups_in_db) == 3
    assert child_group.group_parent_id == parent_group.group_id

    @request.addfinalizer
    def cleanup():
        fixture.destroy_repo_group(zombie_group)
        fixture.destroy_repo_group(child_group)
        fixture.destroy_repo_group(parent_group)

    return (zombie_group, parent_group, child_group)


def test_repo2db_mapper_groups(repo_groups):
    session = meta.Session()
    zombie_group, parent_group, child_group = repo_groups
    zombie_path = os.path.join(
        RepoGroupModel().repos_path, zombie_group.full_path)
    os.rmdir(zombie_path)

    # Avoid removing test repos when calling repo2db_mapper
    repo_list = {
        repo.repo_name: 'test' for repo in session.query(db.Repository).all()
    }
    utils.repo2db_mapper(repo_list, remove_obsolete=True)

    groups_in_db = session.query(db.RepoGroup).all()
    assert child_group in groups_in_db
    assert parent_group in groups_in_db
    assert zombie_path not in groups_in_db


def test_repo2db_mapper_enables_largefiles(backend):
    repo = backend.create_repo()
    repo_list = {repo.repo_name: 'test'}
    with mock.patch('rhodecode.model.db.Repository.scm_instance') as scm_mock:
        with mock.patch.multiple('rhodecode.model.scm.ScmModel',
                                 install_git_hook=mock.DEFAULT,
                                 install_svn_hooks=mock.DEFAULT):
            utils.repo2db_mapper(repo_list, remove_obsolete=False)
            _, kwargs = scm_mock.call_args
            assert kwargs['config'].get('extensions', 'largefiles') == ''


@pytest.mark.backends("git", "svn")
def test_repo2db_mapper_installs_hooks_for_repos_in_db(backend):
    repo = backend.create_repo()
    repo_list = {repo.repo_name: 'test'}
    with mock.patch.object(ScmModel, 'install_hooks') as install_hooks_mock:
        utils.repo2db_mapper(repo_list, remove_obsolete=False)
    install_hooks_mock.assert_called_once_with(
        repo.scm_instance(), repo_type=backend.alias)


@pytest.mark.backends("git", "svn")
def test_repo2db_mapper_installs_hooks_for_newly_added_repos(backend):
    repo = backend.create_repo()
    RepoModel().delete(repo, fs_remove=False)
    meta.Session().commit()
    repo_list = {repo.repo_name: repo.scm_instance()}
    with mock.patch.object(ScmModel, 'install_hooks') as install_hooks_mock:
        utils.repo2db_mapper(repo_list, remove_obsolete=False)
    assert install_hooks_mock.call_count == 1
    install_hooks_args, _ = install_hooks_mock.call_args
    assert install_hooks_args[0].name == repo.repo_name


class TestPasswordChanged(object):
    def setup(self):
        self.session = {
            'rhodecode_user': {
                'password': '0cc175b9c0f1b6a831c399e269772661'
            }
        }
        self.auth_user = mock.Mock()
        self.auth_user.userame = 'test'
        self.auth_user.password = 'abc123'

    def test_returns_false_for_default_user(self):
        self.auth_user.username = db.User.DEFAULT_USER
        result = utils.password_changed(self.auth_user, self.session)
        assert result is False

    def test_returns_false_if_password_was_not_changed(self):
        self.session['rhodecode_user']['password'] = md5(
            self.auth_user.password)
        result = utils.password_changed(self.auth_user, self.session)
        assert result is False

    def test_returns_true_if_password_was_changed(self):
        result = utils.password_changed(self.auth_user, self.session)
        assert result is True

    def test_returns_true_if_auth_user_password_is_empty(self):
        self.auth_user.password = None
        result = utils.password_changed(self.auth_user, self.session)
        assert result is True

    def test_returns_true_if_session_password_is_empty(self):
        self.session['rhodecode_user'].pop('password')
        result = utils.password_changed(self.auth_user, self.session)
        assert result is True


class TestReadOpensourceLicenses(object):
    def test_success(self):
        utils._license_cache = None
        json_data = '''
        {
            "python2.7-pytest-2.7.1": {"UNKNOWN": null},
            "python2.7-Markdown-2.6.2": {
                "BSD-3-Clause": "http://spdx.org/licenses/BSD-3-Clause"
            }
        }
        '''
        resource_string_patch = mock.patch.object(
            utils.pkg_resources, 'resource_string', return_value=json_data)
        with resource_string_patch:
            result = utils.read_opensource_licenses()
        assert result == json.loads(json_data)

    def test_caching(self):
        utils._license_cache = {
            "python2.7-pytest-2.7.1": {
                "UNKNOWN": None
            },
            "python2.7-Markdown-2.6.2": {
                "BSD-3-Clause": "http://spdx.org/licenses/BSD-3-Clause"
            }
        }
        resource_patch = mock.patch.object(
            utils.pkg_resources, 'resource_string', side_effect=Exception)
        json_patch = mock.patch.object(
            utils.json, 'loads', side_effect=Exception)

        with resource_patch as resource_mock, json_patch as json_mock:
            result = utils.read_opensource_licenses()

        assert resource_mock.call_count == 0
        assert json_mock.call_count == 0
        assert result == utils._license_cache

    def test_licenses_file_contains_no_unknown_licenses(self):
        utils._license_cache = None
        result = utils.read_opensource_licenses()
        license_names = []
        for licenses in result.values():
            license_names.extend(licenses.keys())
        assert 'UNKNOWN' not in license_names


class TestMakeDbConfig(object):
    def test_data_from_config_data_from_db_returned(self):
        test_data = [
            ('section1', 'option1', 'value1'),
            ('section2', 'option2', 'value2'),
            ('section3', 'option3', 'value3'),
        ]
        with mock.patch.object(utils, 'config_data_from_db') as config_mock:
            config_mock.return_value = test_data
            kwargs = {'clear_session': False, 'repo': 'test_repo'}
            result = utils.make_db_config(**kwargs)
        config_mock.assert_called_once_with(**kwargs)
        for section, option, expected_value in test_data:
            value = result.get(section, option)
            assert value == expected_value


class TestConfigDataFromDb(object):
    def test_config_data_from_db_returns_active_settings(self):
        test_data = [
            UiSetting('section1', 'option1', 'value1', True),
            UiSetting('section2', 'option2', 'value2', True),
            UiSetting('section3', 'option3', 'value3', False),
        ]
        repo_name = 'test_repo'

        model_patch = mock.patch.object(utils, 'VcsSettingsModel')
        hooks_patch = mock.patch.object(
            utils, 'get_enabled_hook_classes',
            return_value=['pull', 'push', 'repo_size'])
        with model_patch as model_mock, hooks_patch:
            instance_mock = mock.Mock()
            model_mock.return_value = instance_mock
            instance_mock.get_ui_settings.return_value = test_data
            result = utils.config_data_from_db(
                clear_session=False, repo=repo_name)

        self._assert_repo_name_passed(model_mock, repo_name)

        expected_result = [
            ('section1', 'option1', 'value1'),
            ('section2', 'option2', 'value2'),
        ]
        assert result == expected_result

    def _assert_repo_name_passed(self, model_mock, repo_name):
        assert model_mock.call_count == 1
        call_args, call_kwargs = model_mock.call_args
        assert call_kwargs['repo'] == repo_name


class TestIsDirWritable(object):
    def test_returns_false_when_not_writable(self):
        with mock.patch('__builtin__.open', side_effect=OSError):
            assert not utils._is_dir_writable('/stub-path')

    def test_returns_true_when_writable(self, tmpdir):
        assert utils._is_dir_writable(str(tmpdir))

    def test_is_safe_against_race_conditions(self, tmpdir):
        workers = multiprocessing.Pool()
        directories = [str(tmpdir)] * 10
        workers.map(utils._is_dir_writable, directories)


class TestGetEnabledHooks(object):
    def test_only_active_hooks_are_enabled(self):
        ui_settings = [
            UiSetting('hooks', db.RhodeCodeUi.HOOK_PUSH, 'value', True),
            UiSetting('hooks', db.RhodeCodeUi.HOOK_REPO_SIZE, 'value', True),
            UiSetting('hooks', db.RhodeCodeUi.HOOK_PULL, 'value', False)
        ]
        result = utils.get_enabled_hook_classes(ui_settings)
        assert result == ['push', 'repo_size']

    def test_all_hooks_are_enabled(self):
        ui_settings = [
            UiSetting('hooks', db.RhodeCodeUi.HOOK_PUSH, 'value', True),
            UiSetting('hooks', db.RhodeCodeUi.HOOK_REPO_SIZE, 'value', True),
            UiSetting('hooks', db.RhodeCodeUi.HOOK_PULL, 'value', True)
        ]
        result = utils.get_enabled_hook_classes(ui_settings)
        assert result == ['push', 'repo_size', 'pull']

    def test_no_enabled_hooks_when_no_hook_settings_are_found(self):
        ui_settings = []
        result = utils.get_enabled_hook_classes(ui_settings)
        assert result == []
