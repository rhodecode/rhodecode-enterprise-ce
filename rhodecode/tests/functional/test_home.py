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

from mock import patch
import pytest

import rhodecode
from rhodecode.lib.utils import map_groups
from rhodecode.model.db import Repository, User, RepoGroup
from rhodecode.model.meta import Session
from rhodecode.model.repo import RepoModel
from rhodecode.model.repo_group import RepoGroupModel
from rhodecode.model.settings import SettingsModel
from rhodecode.tests import TestController, url, TEST_USER_ADMIN_LOGIN
from rhodecode.tests.fixture import Fixture


fixture = Fixture()


class TestHomeController(TestController):

    def test_index(self):
        self.log_user()
        response = self.app.get(url(controller='home', action='index'))
        # if global permission is set
        response.mustcontain('Add Repository')

        # search for objects inside the JavaScript JSON
        for repo in Repository.getAll():
            response.mustcontain('"name_raw": "%s"' % repo.repo_name)

    def test_index_contains_backend_specific_details(self, backend):
        self.log_user()
        response = self.app.get(url(controller='home', action='index'))
        tip = backend.repo.get_commit().raw_id

        # html in javascript variable:
        response.mustcontain(r'<i class=\"icon-%s\"' % (backend.alias, ))
        response.mustcontain(r'href=\"/%s\"' % (backend.repo_name, ))

        response.mustcontain("""/%s/changeset/%s""" % (backend.repo_name, tip))
        response.mustcontain("""Added a symlink""")

    def test_index_with_anonymous_access_disabled(self):
        with fixture.anon_access(False):
            response = self.app.get(url(controller='home', action='index'),
                                    status=302)
            assert 'login' in response.location

    def test_index_page_on_groups(self, autologin_user, repo_group):
        response = self.app.get(url('repo_group_home', group_name='gr1'))
        response.mustcontain("gr1/repo_in_group")

    def test_index_page_on_group_with_trailing_slash(
            self, autologin_user, repo_group):
        response = self.app.get(url('repo_group_home', group_name='gr1') + '/')
        response.mustcontain("gr1/repo_in_group")

    @pytest.fixture(scope='class')
    def repo_group(self, request):
        gr = fixture.create_repo_group('gr1')
        fixture.create_repo(name='gr1/repo_in_group', repo_group=gr)

        @request.addfinalizer
        def cleanup():
            RepoModel().delete('gr1/repo_in_group')
            RepoGroupModel().delete(repo_group='gr1', force_delete=True)
            Session().commit()

    def test_index_with_name_with_tags(self, autologin_user):
        user = User.get_by_username('test_admin')
        user.name = '<img src="/image1" onload="alert(\'Hello, World!\');">'
        user.lastname = (
            '<img src="/image2" onload="alert(\'Hello, World!\');">')
        Session().add(user)
        Session().commit()

        response = self.app.get(url(controller='home', action='index'))
        response.mustcontain(
            '&lt;img src=&#34;/image1&#34; onload=&#34;'
            'alert(&#39;Hello, World!&#39;);&#34;&gt;')
        response.mustcontain(
            '&lt;img src=&#34;/image2&#34; onload=&#34;'
            'alert(&#39;Hello, World!&#39;);&#34;&gt;')

    @pytest.mark.parametrize("name, state", [
        ('Disabled', False),
        ('Enabled', True),
    ])
    def test_index_show_version(self, autologin_user, name, state):
        version_string = 'RhodeCode Enterprise %s' % rhodecode.__version__

        show = SettingsModel().get_setting_by_name('show_version')
        show.app_settings_value = state
        Session().add(show)
        Session().commit()
        response = self.app.get(url(controller='home', action='index'))
        if state is True:
            response.mustcontain(version_string)
        if state is False:
            response.mustcontain(no=[version_string])


class TestUserAutocompleteData(TestController):
    def test_returns_list_of_users(self, user_util):
        self.log_user()
        user = user_util.create_user(is_active=True)
        user_name = user.username
        response = self.app.get(
            url(controller='home', action='user_autocomplete_data'),
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest', }, status=200)
        result = json.loads(response.body)
        values = [suggestion['value'] for suggestion in result['suggestions']]
        assert user_name in values

    def test_returns_groups_when_user_groups_sent(self, user_util):
        self.log_user()
        group = user_util.create_user_group(user_groups_active=True)
        group_name = group.users_group_name
        response = self.app.get(
            url(controller='home', action='user_autocomplete_data',
                user_groups='true'),
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest', }, status=200)
        result = json.loads(response.body)
        values = [suggestion['value'] for suggestion in result['suggestions']]
        assert group_name in values

    def test_result_is_limited_when_query_is_sent(self):
        self.log_user()
        fake_result = [
            {
                'first_name': 'John',
                'value_display': 'hello{} (John Smith)'.format(i),
                'icon_link': '/images/user14.png',
                'value': 'hello{}'.format(i),
                'last_name': 'Smith',
                'username': 'hello{}'.format(i),
                'id': i,
                'value_type': u'user'
            }
            for i in range(10)
        ]
        users_patcher = patch.object(
            RepoModel, 'get_users', return_value=fake_result)
        groups_patcher = patch.object(
            RepoModel, 'get_user_groups', return_value=fake_result)

        query = 'hello'
        with users_patcher as users_mock, groups_patcher as groups_mock:
            response = self.app.get(
                url(controller='home', action='user_autocomplete_data',
                    user_groups='true', query=query),
                headers={'X-REQUESTED-WITH': 'XMLHttpRequest', }, status=200)

        result = json.loads(response.body)
        users_mock.assert_called_once_with(name_contains=query)
        groups_mock.assert_called_once_with(name_contains=query)
        assert len(result['suggestions']) == 20


def assert_and_get_content(result):
    repos = []
    groups = []
    for data in result:
        for data_item in data['children']:
            assert data_item['id']
            assert data_item['text']
            if data_item['type'] == 'repo':
                repos.append(data_item)
            else:
                groups.append(data_item)

    return repos, groups


class TestRepoSwitcherData(TestController):
    required_repos_with_groups = [
        'abc',
        'abc-fork',
        'forks/abcd',
        'abcd',
        'abcde',
        'a/abc',
        'aa/abc',
        'aaa/abc',
        'aaaa/abc',
        'repos_abc/aaa/abc',
        'abc_repos/abc',
        'abc_repos/abcd',
        'xxx/xyz',
        'forked-abc/a/abc'
    ]

    @pytest.fixture(autouse=True, scope='class')
    def prepare(self, request, pylonsapp):
        for repo_and_group in self.required_repos_with_groups:
            # create structure of groups and return the last group

            repo_group = map_groups(repo_and_group)

            RepoModel()._create_repo(
                repo_and_group, 'hg', 'test-ac', TEST_USER_ADMIN_LOGIN,
                repo_group=getattr(repo_group, 'group_id', None))

            Session().commit()

        request.addfinalizer(self.cleanup)

    def cleanup(self):
        # first delete all repos
        for repo_and_groups in self.required_repos_with_groups:
            repo = Repository.get_by_repo_name(repo_and_groups)
            if repo:
                RepoModel().delete(repo)
                Session().commit()

        # then delete all empty groups
        for repo_and_groups in self.required_repos_with_groups:
            if '/' in repo_and_groups:
                r_group = repo_and_groups.rsplit('/', 1)[0]
                repo_group = RepoGroup.get_by_group_name(r_group)
                if not repo_group:
                    continue
                parents = repo_group.parents
                RepoGroupModel().delete(repo_group, force_delete=True)
                Session().commit()

                for el in reversed(parents):
                    RepoGroupModel().delete(el, force_delete=True)
                    Session().commit()

    def test_returns_list_of_repos_and_groups(self):
        self.log_user()

        response = self.app.get(
            url(controller='home', action='repo_switcher_data'),
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest', }, status=200)
        result = json.loads(response.body)['results']

        repos, groups = assert_and_get_content(result)

        assert len(repos) == len(Repository.get_all())
        assert len(groups) == len(RepoGroup.get_all())

    def test_returns_list_of_repos_and_groups_filtered(self):
        self.log_user()

        response = self.app.get(
            url(controller='home', action='repo_switcher_data'),
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest', },
            params={'query': 'abc'}, status=200)
        result = json.loads(response.body)['results']

        repos, groups = assert_and_get_content(result)

        assert len(repos) == 13
        assert len(groups) == 5

    def test_returns_list_of_properly_sorted_and_filtered(self):
        self.log_user()

        response = self.app.get(
            url(controller='home', action='repo_switcher_data'),
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest', },
            params={'query': 'abc'}, status=200)
        result = json.loads(response.body)['results']

        repos, groups = assert_and_get_content(result)

        test_repos = [x['text'] for x in repos[:4]]
        assert ['abc', 'abcd', 'a/abc', 'abcde'] == test_repos

        test_groups = [x['text'] for x in groups[:4]]
        assert ['abc_repos', 'repos_abc',
                'forked-abc', 'forked-abc/a'] == test_groups


class TestRepoListData(TestController):
    def test_returns_list_of_repos_and_groups(self, user_util):
        self.log_user()

        response = self.app.get(
            url(controller='home', action='repo_switcher_data'),
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest', }, status=200)
        result = json.loads(response.body)['results']

        repos, groups = assert_and_get_content(result)

        assert len(repos) == len(Repository.get_all())
        assert len(groups) == 0

    def test_returns_list_of_repos_and_groups_filtered(self):
        self.log_user()

        response = self.app.get(
            url(controller='home', action='repo_switcher_data'),
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest', },
            params={'query': 'vcs_test_git'}, status=200)
        result = json.loads(response.body)['results']

        repos, groups = assert_and_get_content(result)

        assert len(repos) == len(Repository.query().filter(
            Repository.repo_name.ilike('%vcs_test_git%')).all())
        assert len(groups) == 0

    def test_returns_list_of_repos_and_groups_filtered_with_type(self):
        self.log_user()

        response = self.app.get(
            url(controller='home', action='repo_switcher_data'),
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest', },
            params={'query': 'vcs_test_git', 'repo_type': 'git'}, status=200)
        result = json.loads(response.body)['results']

        repos, groups = assert_and_get_content(result)

        assert len(repos) == len(Repository.query().filter(
            Repository.repo_name.ilike('%vcs_test_git%')).all())
        assert len(groups) == 0

    def test_returns_list_of_repos_non_ascii_query(self):
        self.log_user()
        response = self.app.get(
            url(controller='home', action='repo_switcher_data'),
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest', },
            params={'query': 'ć_vcs_test_ą', 'repo_type': 'git'}, status=200)
        result = json.loads(response.body)['results']

        repos, groups = assert_and_get_content(result)

        assert len(repos) == 0
        assert len(groups) == 0
