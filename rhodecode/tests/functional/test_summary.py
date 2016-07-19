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

import re
import os

import mock
import pytest

from rhodecode.controllers import summary
from rhodecode.lib import vcs
from rhodecode.lib import helpers as h
from rhodecode.lib.compat import OrderedDict
from rhodecode.lib.vcs.exceptions import RepositoryRequirementError
from rhodecode.model.db import Repository
from rhodecode.model.meta import Session
from rhodecode.model.repo import RepoModel
from rhodecode.model.scm import ScmModel
from rhodecode.tests import (
    TestController, url, HG_REPO, assert_session_flash, TESTS_TMP_PATH)
from rhodecode.tests.fixture import Fixture
from rhodecode.tests.utils import AssertResponse


fixture = Fixture()


class TestSummaryController(TestController):
    def test_index(self, backend):
        self.log_user()
        repo_id = backend.repo.repo_id
        repo_name = backend.repo_name
        with mock.patch('rhodecode.lib.helpers.is_svn_without_proxy',
                        return_value=False):
            response = self.app.get(url('summary_home', repo_name=repo_name))

        # repo type
        response.mustcontain(
            '<i class="icon-%s">' % (backend.alias, )
        )
        # public/private
        response.mustcontain(
            """<i class="icon-unlock-alt">"""
        )

        # clone url...
        response.mustcontain(
            'id="clone_url" readonly="readonly"'
            ' value="http://test_admin@test.example.com:80/%s"' % (repo_name, ))
        response.mustcontain(
            'id="clone_url_id" readonly="readonly"'
            ' value="http://test_admin@test.example.com:80/_%s"' % (repo_id, ))

    def test_index_svn_without_proxy(self, backend_svn):
        self.log_user()
        repo_id = backend_svn.repo.repo_id
        repo_name = backend_svn.repo_name
        response = self.app.get(url('summary_home', repo_name=repo_name))
        # clone url...
        response.mustcontain(
            'id="clone_url" disabled'
            ' value="http://test_admin@test.example.com:80/%s"' % (repo_name, ))
        response.mustcontain(
            'id="clone_url_id" disabled'
            ' value="http://test_admin@test.example.com:80/_%s"' % (repo_id, ))

    def test_index_with_trailing_slash(self, autologin_user, backend):
        repo_id = backend.repo.repo_id
        repo_name = backend.repo_name
        with mock.patch('rhodecode.lib.helpers.is_svn_without_proxy',
                        return_value=False):
            response = self.app.get(
                url('summary_home', repo_name=repo_name) + '/',
                status=200)

        # clone url...
        response.mustcontain(
            'id="clone_url" readonly="readonly"'
            ' value="http://test_admin@test.example.com:80/%s"' % (repo_name, ))
        response.mustcontain(
            'id="clone_url_id" readonly="readonly"'
            ' value="http://test_admin@test.example.com:80/_%s"' % (repo_id, ))

    def test_index_by_id(self, backend):
        self.log_user()
        repo_id = backend.repo.repo_id
        response = self.app.get(url(
            'summary_home', repo_name='_%s' % (repo_id,)))

        # repo type
        response.mustcontain(
            '<i class="icon-%s">' % (backend.alias, )
        )
        # public/private
        response.mustcontain(
            """<i class="icon-unlock-alt">"""
        )

    def test_index_by_repo_having_id_path_in_name_hg(self):
        self.log_user()
        fixture.create_repo(name='repo_1')
        response = self.app.get(url('summary_home', repo_name='repo_1'))

        try:
            response.mustcontain("repo_1")
        finally:
            RepoModel().delete(Repository.get_by_repo_name('repo_1'))
            Session().commit()

    def test_index_with_anonymous_access_disabled(self):
        with fixture.anon_access(False):
            response = self.app.get(url('summary_home', repo_name=HG_REPO),
                                    status=302)
            assert 'login' in response.location

    def _enable_stats(self, repo):
        r = Repository.get_by_repo_name(repo)
        r.enable_statistics = True
        Session().add(r)
        Session().commit()

    expected_trending = {
        'hg': {
            "py": {"count": 68, "desc": ["Python"]},
            "rst": {"count": 16, "desc": ["Rst"]},
            "css": {"count": 2, "desc": ["Css"]},
            "sh": {"count": 2, "desc": ["Bash"]},
            "bat": {"count": 1, "desc": ["Batch"]},
            "cfg": {"count": 1, "desc": ["Ini"]},
            "html": {"count": 1, "desc": ["EvoqueHtml", "Html"]},
            "ini": {"count": 1, "desc": ["Ini"]},
            "js": {"count": 1, "desc": ["Javascript"]},
            "makefile": {"count": 1, "desc": ["Makefile", "Makefile"]}
        },
        'git': {
            "py": {"count": 68, "desc": ["Python"]},
            "rst": {"count": 16, "desc": ["Rst"]},
            "css": {"count": 2, "desc": ["Css"]},
            "sh": {"count": 2, "desc": ["Bash"]},
            "bat": {"count": 1, "desc": ["Batch"]},
            "cfg": {"count": 1, "desc": ["Ini"]},
            "html": {"count": 1, "desc": ["EvoqueHtml", "Html"]},
            "ini": {"count": 1, "desc": ["Ini"]},
            "js": {"count": 1, "desc": ["Javascript"]},
            "makefile": {"count": 1, "desc": ["Makefile", "Makefile"]}
        },
        'svn': {
            "py": {"count": 75, "desc": ["Python"]},
            "rst": {"count": 16, "desc": ["Rst"]},
            "html": {"count": 11, "desc": ["EvoqueHtml", "Html"]},
            "css": {"count": 2, "desc": ["Css"]},
            "bat": {"count": 1, "desc": ["Batch"]},
            "cfg": {"count": 1, "desc": ["Ini"]},
            "ini": {"count": 1, "desc": ["Ini"]},
            "js": {"count": 1, "desc": ["Javascript"]},
            "makefile": {"count": 1, "desc": ["Makefile", "Makefile"]},
            "sh": {"count": 1, "desc": ["Bash"]}
        },
    }

    def test_repo_stats(self, backend, xhr_header):
        self.log_user()
        response = self.app.get(
            url('repo_stats',
                repo_name=backend.repo_name, commit_id='tip'),
            extra_environ=xhr_header,
            status=200)
        assert re.match(r'6[\d\.]+ KiB', response.json['size'])

    def test_repo_stats_code_stats_enabled(self, backend, xhr_header):
        self.log_user()
        repo_name = backend.repo_name

        # codes stats
        self._enable_stats(repo_name)
        ScmModel().mark_for_invalidation(repo_name)

        response = self.app.get(
            url('repo_stats',
                repo_name=backend.repo_name, commit_id='tip'),
            extra_environ=xhr_header,
            status=200)

        expected_data = self.expected_trending[backend.alias]
        returned_stats = response.json['code_stats']
        for k, v in expected_data.items():
            assert v == returned_stats[k]

    def test_repo_refs_data(self, backend):
        response = self.app.get(
            url('repo_refs_data', repo_name=backend.repo_name),
            status=200)

        # Ensure that there is the correct amount of items in the result
        repo = backend.repo.scm_instance()
        data = response.json['results']
        items = sum(len(section['children']) for section in data)
        repo_refs = len(repo.branches) + len(repo.tags) + len(repo.bookmarks)
        assert items == repo_refs

    def test_index_shows_missing_requirements_message(
            self, backend, autologin_user):
        repo_name = backend.repo_name
        scm_patcher = mock.patch.object(
            Repository, 'scm_instance', side_effect=RepositoryRequirementError)

        with scm_patcher:
            response = self.app.get(url('summary_home', repo_name=repo_name))
        assert_response = AssertResponse(response)
        assert_response.element_contains(
            '.main .alert-warning strong', 'Missing requirements')
        assert_response.element_contains(
            '.main .alert-warning',
            'These commits cannot be displayed, because this repository'
            ' uses the Mercurial largefiles extension, which was not enabled.')

    def test_missing_requirements_page_does_not_contains_switch_to(
            self, backend):
        self.log_user()
        repo_name = backend.repo_name
        scm_patcher = mock.patch.object(
            Repository, 'scm_instance', side_effect=RepositoryRequirementError)

        with scm_patcher:
            response = self.app.get(url('summary_home', repo_name=repo_name))
        response.mustcontain(no='Switch To')


@pytest.mark.usefixtures('pylonsapp')
class TestSwitcherReferenceData:

    def test_creates_reference_urls_based_on_name(self):
        references = {
            'name': 'commit_id',
        }
        controller = summary.SummaryController()
        is_svn = False
        result = controller._switcher_reference_data(
            'repo_name', references, is_svn)
        expected_url = h.url(
            'files_home', repo_name='repo_name', revision='name',
            at='name')
        assert result[0]['files_url'] == expected_url

    def test_urls_contain_commit_id_if_slash_in_name(self):
        references = {
            'name/with/slash': 'commit_id',
        }
        controller = summary.SummaryController()
        is_svn = False
        result = controller._switcher_reference_data(
            'repo_name', references, is_svn)
        expected_url = h.url(
            'files_home', repo_name='repo_name', revision='commit_id',
            at='name/with/slash')
        assert result[0]['files_url'] == expected_url

    def test_adds_reference_to_path_for_svn(self):
        references = {
            'name/with/slash': 'commit_id',
        }
        controller = summary.SummaryController()
        is_svn = True
        result = controller._switcher_reference_data(
            'repo_name', references, is_svn)
        expected_url = h.url(
            'files_home', repo_name='repo_name', f_path='name/with/slash',
            revision='commit_id', at='name/with/slash')
        assert result[0]['files_url'] == expected_url


@pytest.mark.usefixtures('pylonsapp')
class TestCreateReferenceData:

    @pytest.fixture
    def example_refs(self):
        section_1_refs = OrderedDict((('a', 'a_id'), ('b', 'b_id')))
        example_refs = [
            ('section_1', section_1_refs, 't1'),
            ('section_2', {'c': 'c_id'}, 't2'),
        ]
        return example_refs

    def test_generates_refs_based_on_commit_ids(self, example_refs):
        repo = mock.Mock()
        repo.name = 'test-repo'
        repo.alias = 'git'
        controller = summary.SummaryController()

        result = controller._create_reference_data(repo, example_refs)

        expected_result = [
            {
                'children': [
                    {
                        'id': 'a', 'raw_id': 'a_id', 'text': 'a', 'type': 't1',
                        'files_url': '/test-repo/files/a/?at=a'
                    },
                    {
                        'id': 'b', 'raw_id': 'b_id', 'text': 'b', 'type': 't1',
                        'files_url': '/test-repo/files/b/?at=b'
                    }
                ],
                'text': 'section_1'
            },
            {
                'children': [
                    {
                        'id': 'c', 'raw_id': 'c_id', 'text': 'c', 'type': 't2',
                        'files_url': '/test-repo/files/c/?at=c'
                    }
                ],
                'text': 'section_2'
            }]
        assert result == expected_result

    def test_generates_refs_with_path_for_svn(self, example_refs):
        repo = mock.Mock()
        repo.name = 'test-repo'
        repo.alias = 'svn'
        controller = summary.SummaryController()
        result = controller._create_reference_data(repo, example_refs)

        expected_result = [
            {
                'children': [
                    {
                        'id': 'a@a_id', 'raw_id': 'a_id',
                        'text': 'a', 'type': 't1',
                        'files_url': '/test-repo/files/a_id/a?at=a'
                    },
                    {
                        'id': 'b@b_id', 'raw_id': 'b_id',
                        'text': 'b', 'type': 't1',
                        'files_url': '/test-repo/files/b_id/b?at=b'
                    }
                ],
                'text': 'section_1'
            },
            {
                'children': [
                    {
                        'id': 'c@c_id', 'raw_id': 'c_id',
                        'text': 'c', 'type': 't2',
                        'files_url': '/test-repo/files/c_id/c?at=c'
                    }
                ],
                'text': 'section_2'
            }
        ]
        assert result == expected_result


@pytest.mark.usefixtures("app")
class TestRepoLocation:

    @pytest.mark.parametrize("suffix", [u'', u'ąęł'], ids=['', 'non-ascii'])
    def test_manual_delete(self, autologin_user, backend, suffix, csrf_token):
        repo = backend.create_repo(name_suffix=suffix)
        repo_name = repo.repo_name

        # delete from file system
        RepoModel()._delete_filesystem_repo(repo)

        # test if the repo is still in the database
        new_repo = RepoModel().get_by_repo_name(repo_name)
        assert new_repo.repo_name == repo_name

        # check if repo is not in the filesystem
        assert not repo_on_filesystem(repo_name)
        self.assert_repo_not_found_redirect(repo_name)

    def assert_repo_not_found_redirect(self, repo_name):
        # run the check page that triggers the other flash message
        response = self.app.get(url('repo_check_home', repo_name=repo_name))
        assert_session_flash(
            response, 'The repository at %s cannot be located.' % repo_name)


def repo_on_filesystem(repo_name):
    try:
        vcs.get_repo(os.path.join(TESTS_TMP_PATH, repo_name))
        return True
    except Exception:
        return False


class TestCreateFilesUrl(object):
    def test_creates_non_svn_url(self):
        controller = summary.SummaryController()
        repo = mock.Mock()
        repo.name = 'abcde'
        full_repo_name = 'test-repo-group/' + repo.name
        ref_name = 'branch1'
        raw_id = 'deadbeef0123456789'
        is_svn = False

        with mock.patch.object(summary.h, 'url') as url_mock:
            result = controller._create_files_url(
                repo, full_repo_name, ref_name, raw_id, is_svn)
        url_mock.assert_called_once_with(
            'files_home', repo_name=full_repo_name, f_path='',
            revision=ref_name, at=ref_name)
        assert result == url_mock.return_value

    def test_creates_svn_url(self):
        controller = summary.SummaryController()
        repo = mock.Mock()
        repo.name = 'abcde'
        full_repo_name = 'test-repo-group/' + repo.name
        ref_name = 'branch1'
        raw_id = 'deadbeef0123456789'
        is_svn = True

        with mock.patch.object(summary.h, 'url') as url_mock:
            result = controller._create_files_url(
                repo, full_repo_name, ref_name, raw_id, is_svn)
        url_mock.assert_called_once_with(
            'files_home', repo_name=full_repo_name, f_path=ref_name,
            revision=raw_id, at=ref_name)
        assert result == url_mock.return_value

    def test_name_has_slashes(self):
        controller = summary.SummaryController()
        repo = mock.Mock()
        repo.name = 'abcde'
        full_repo_name = 'test-repo-group/' + repo.name
        ref_name = 'branch1/branch2'
        raw_id = 'deadbeef0123456789'
        is_svn = False

        with mock.patch.object(summary.h, 'url') as url_mock:
            result = controller._create_files_url(
                repo, full_repo_name, ref_name, raw_id, is_svn)
        url_mock.assert_called_once_with(
            'files_home', repo_name=full_repo_name, f_path='', revision=raw_id,
            at=ref_name)
        assert result == url_mock.return_value


class TestReferenceItems(object):
    repo = mock.Mock()
    ref_type = 'branch'
    fake_url = '/abcde/'

    @staticmethod
    def _format_function(name, id_):
        return 'format_function_{}_{}'.format(name, id_)

    def test_creates_required_amount_of_items(self):
        amount = 100
        refs = {
            'ref{}'.format(i): '{0:040d}'.format(i)
            for i in range(amount)
        }

        controller = summary.SummaryController()

        url_patcher = mock.patch.object(
            controller, '_create_files_url')
        svn_patcher = mock.patch.object(
            summary.h, 'is_svn', return_value=False)

        with url_patcher as url_mock, svn_patcher:
            result = controller._create_reference_items(
                self.repo, refs, self.ref_type, self._format_function)
        assert len(result) == amount
        assert url_mock.call_count == amount

    def test_single_item_details(self):
        ref_name = 'ref1'
        ref_id = 'deadbeef'
        refs = {
            ref_name: ref_id
        }

        controller = summary.SummaryController()
        url_patcher = mock.patch.object(
            controller, '_create_files_url', return_value=self.fake_url)
        svn_patcher = mock.patch.object(
            summary.h, 'is_svn', return_value=False)

        with url_patcher as url_mock, svn_patcher:
            result = controller._create_reference_items(
                self.repo, refs, self.ref_type, self._format_function)

        url_mock.assert_called_once_with(self.repo, ref_name, ref_id, False)
        expected_result = [
            {
                'text': ref_name,
                'id': self._format_function(ref_name, ref_id),
                'raw_id': ref_id,
                'type': self.ref_type,
                'files_url': self.fake_url
            }
        ]
        assert result == expected_result
