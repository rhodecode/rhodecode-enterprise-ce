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

import mock
import pytest

from rhodecode.lib import helpers as h
from rhodecode.model.db import User, Gist
from rhodecode.model.gist import GistModel
from rhodecode.model.meta import Session
from rhodecode.tests import (
    TEST_USER_ADMIN_LOGIN, TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS,
    TestController, assert_session_flash, url)
from rhodecode.tests.utils import AssertResponse


class GistUtility(object):

    def __init__(self):
        self._gist_ids = []

    def __call__(
            self, f_name, content='some gist', lifetime=-1,
            description='gist-desc', gist_type='public',
            acl_level=Gist.GIST_PUBLIC, owner=TEST_USER_ADMIN_LOGIN):
        gist_mapping = {
            f_name: {'content': content}
        }
        user = User.get_by_username(owner)
        gist = GistModel().create(
            description, owner=user, gist_mapping=gist_mapping,
            gist_type=gist_type, lifetime=lifetime, gist_acl_level=acl_level)
        Session().commit()
        self._gist_ids.append(gist.gist_id)
        return gist

    def cleanup(self):
        for gist_id in self._gist_ids:
            gist = Gist.get(gist_id)
            if gist:
                Session().delete(gist)

        Session().commit()


@pytest.fixture
def create_gist(request):
    gist_utility = GistUtility()
    request.addfinalizer(gist_utility.cleanup)
    return gist_utility


class TestGistsController(TestController):

    def test_index_empty(self, create_gist):
        self.log_user()
        response = self.app.get(url('gists'))
        response.mustcontain('data: [],')

    def test_index(self, create_gist):
        self.log_user()
        g1 = create_gist('gist1')
        g2 = create_gist('gist2', lifetime=1400)
        g3 = create_gist('gist3', description='gist3-desc')
        g4 = create_gist('gist4', gist_type='private').gist_access_id
        response = self.app.get(url('gists'))

        response.mustcontain('gist: %s' % g1.gist_access_id)
        response.mustcontain('gist: %s' % g2.gist_access_id)
        response.mustcontain('gist: %s' % g3.gist_access_id)
        response.mustcontain('gist3-desc')
        response.mustcontain(no=['gist: %s' % g4])

        # Expiration information should be visible
        expires_tag = '%s' % h.age_component(
            h.time_to_datetime(g2.gist_expires))
        response.mustcontain(expires_tag.replace('"', '\\"'))

    def test_index_private_gists(self, create_gist):
        self.log_user()
        gist = create_gist('gist5', gist_type='private')
        response = self.app.get(url('gists', private=1))

        # and privates
        response.mustcontain('gist: %s' % gist.gist_access_id)

    def test_index_show_all(self, create_gist):
        self.log_user()
        create_gist('gist1')
        create_gist('gist2', lifetime=1400)
        create_gist('gist3', description='gist3-desc')
        create_gist('gist4', gist_type='private')

        response = self.app.get(url('gists', all=1))

        assert len(GistModel.get_all()) == 4
        # and privates
        for gist in GistModel.get_all():
            response.mustcontain('gist: %s' % gist.gist_access_id)

    def test_index_show_all_hidden_from_regular(self, create_gist):
        self.log_user(TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        create_gist('gist2', gist_type='private')
        create_gist('gist3', gist_type='private')
        create_gist('gist4', gist_type='private')

        response = self.app.get(url('gists', all=1))

        assert len(GistModel.get_all()) == 3
        # since we don't have access to private in this view, we
        # should see nothing
        for gist in GistModel.get_all():
            response.mustcontain(no=['gist: %s' % gist.gist_access_id])

    def test_create_missing_description(self):
        self.log_user()
        response = self.app.post(
            url('gists'),
            params={'lifetime': -1, 'csrf_token': self.csrf_token},
            status=200)

        response.mustcontain('Missing value')

    def test_create(self):
        self.log_user()
        response = self.app.post(url('gists'),
                                 params={'lifetime': -1,
                                         'content': 'gist test',
                                         'filename': 'foo',
                                         'public': 'public',
                                         'acl_level': Gist.ACL_LEVEL_PUBLIC,
                                         'csrf_token': self.csrf_token},
                                 status=302)
        response = response.follow()
        response.mustcontain('added file: foo')
        response.mustcontain('gist test')

    def test_create_with_path_with_dirs(self):
        self.log_user()
        response = self.app.post(url('gists'),
                                 params={'lifetime': -1,
                                         'content': 'gist test',
                                         'filename': '/home/foo',
                                         'public': 'public',
                                         'acl_level': Gist.ACL_LEVEL_PUBLIC,
                                         'csrf_token': self.csrf_token},
                                 status=200)
        response.mustcontain('Filename cannot be inside a directory')

    def test_access_expired_gist(self, create_gist):
        self.log_user()
        gist = create_gist('never-see-me')
        gist.gist_expires = 0  # 1970
        Session().add(gist)
        Session().commit()

        self.app.get(url('gist', gist_id=gist.gist_access_id), status=404)

    def test_create_private(self):
        self.log_user()
        response = self.app.post(url('gists'),
                                 params={'lifetime': -1,
                                         'content': 'private gist test',
                                         'filename': 'private-foo',
                                         'private': 'private',
                                         'acl_level': Gist.ACL_LEVEL_PUBLIC,
                                         'csrf_token': self.csrf_token},
                                 status=302)
        response = response.follow()
        response.mustcontain('added file: private-foo<')
        response.mustcontain('private gist test')
        response.mustcontain('Private Gist')
        # Make sure private gists are not indexed by robots
        response.mustcontain(
            '<meta name="robots" content="noindex, nofollow">')

    def test_create_private_acl_private(self):
        self.log_user()
        response = self.app.post(url('gists'),
                                 params={'lifetime': -1,
                                         'content': 'private gist test',
                                         'filename': 'private-foo',
                                         'private': 'private',
                                         'acl_level': Gist.ACL_LEVEL_PRIVATE,
                                         'csrf_token': self.csrf_token},
                                 status=302)
        response = response.follow()
        response.mustcontain('added file: private-foo<')
        response.mustcontain('private gist test')
        response.mustcontain('Private Gist')
        # Make sure private gists are not indexed by robots
        response.mustcontain(
            '<meta name="robots" content="noindex, nofollow">')

    def test_create_with_description(self):
        self.log_user()
        response = self.app.post(url('gists'),
                                 params={'lifetime': -1,
                                         'content': 'gist test',
                                         'filename': 'foo-desc',
                                         'description': 'gist-desc',
                                         'public': 'public',
                                         'acl_level': Gist.ACL_LEVEL_PUBLIC,
                                         'csrf_token': self.csrf_token},
                                 status=302)
        response = response.follow()
        response.mustcontain('added file: foo-desc')
        response.mustcontain('gist test')
        response.mustcontain('gist-desc')

    def test_create_public_with_anonymous_access(self):
        self.log_user()
        params = {
            'lifetime': -1,
            'content': 'gist test',
            'filename': 'foo-desc',
            'description': 'gist-desc',
            'public': 'public',
            'acl_level': Gist.ACL_LEVEL_PUBLIC,
            'csrf_token': self.csrf_token
        }
        response = self.app.post(url('gists'), params=params, status=302)
        self.logout_user()
        response = response.follow()
        response.mustcontain('added file: foo-desc')
        response.mustcontain('gist test')
        response.mustcontain('gist-desc')

    def test_new(self):
        self.log_user()
        self.app.get(url('new_gist'))

    def test_delete(self, create_gist):
        self.log_user()
        gist = create_gist('delete-me')
        response = self.app.post(
            url('gist', gist_id=gist.gist_id),
            params={'_method': 'delete', 'csrf_token': self.csrf_token})
        assert_session_flash(response, 'Deleted gist %s' % gist.gist_id)

    def test_delete_normal_user_his_gist(self, create_gist):
        self.log_user(TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        gist = create_gist('delete-me', owner=TEST_USER_REGULAR_LOGIN)
        response = self.app.post(
            url('gist', gist_id=gist.gist_id),
            params={'_method': 'delete', 'csrf_token': self.csrf_token})
        assert_session_flash(response, 'Deleted gist %s' % gist.gist_id)

    def test_delete_normal_user_not_his_own_gist(self, create_gist):
        self.log_user(TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        gist = create_gist('delete-me')
        self.app.post(
            url('gist', gist_id=gist.gist_id),
            params={'_method': 'delete', 'csrf_token': self.csrf_token},
            status=403)

    def test_show(self, create_gist):
        gist = create_gist('gist-show-me')
        response = self.app.get(url('gist', gist_id=gist.gist_access_id))

        response.mustcontain('added file: gist-show-me<')

        assert_response = AssertResponse(response)
        assert_response.element_equals_to(
            'div.rc-user span.user',
            '<span class="user"> %s</span>' % h.link_to_user('test_admin'))

        response.mustcontain('gist-desc')

    def test_show_without_hg(self, create_gist):
        with mock.patch(
                'rhodecode.lib.vcs.settings.ALIASES', ['git']):
            gist = create_gist('gist-show-me-again')
            self.app.get(url('gist', gist_id=gist.gist_access_id), status=200)

    def test_show_acl_private(self, create_gist):
        gist = create_gist('gist-show-me-only-when-im-logged-in',
                           acl_level=Gist.ACL_LEVEL_PRIVATE)
        self.app.get(url('gist', gist_id=gist.gist_access_id), status=404)

        # now we log-in we should see thi gist
        self.log_user()
        response = self.app.get(url('gist', gist_id=gist.gist_access_id))
        response.mustcontain('added file: gist-show-me-only-when-im-logged-in')

        assert_response = AssertResponse(response)
        assert_response.element_equals_to(
            'div.rc-user span.user',
            '<span class="user"> %s</span>' % h.link_to_user('test_admin'))
        response.mustcontain('gist-desc')

    def test_show_as_raw(self, create_gist):
        gist = create_gist('gist-show-me', content='GIST CONTENT')
        response = self.app.get(url('formatted_gist',
                                    gist_id=gist.gist_access_id, format='raw'))
        assert response.body == 'GIST CONTENT'

    def test_show_as_raw_individual_file(self, create_gist):
        gist = create_gist('gist-show-me-raw', content='GIST BODY')
        response = self.app.get(url('formatted_gist_file',
                                    gist_id=gist.gist_access_id, format='raw',
                                    revision='tip', f_path='gist-show-me-raw'))
        assert response.body == 'GIST BODY'

    def test_edit_page(self, create_gist):
        self.log_user()
        gist = create_gist('gist-for-edit', content='GIST EDIT BODY')
        response = self.app.get(url('edit_gist', gist_id=gist.gist_access_id))
        response.mustcontain('GIST EDIT BODY')

    def test_edit_page_non_logged_user(self, create_gist):
        gist = create_gist('gist-for-edit', content='GIST EDIT BODY')
        self.app.get(url('edit_gist', gist_id=gist.gist_access_id), status=302)

    def test_edit_normal_user_his_gist(self, create_gist):
        self.log_user(TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        gist = create_gist('gist-for-edit', owner=TEST_USER_REGULAR_LOGIN)
        self.app.get(url('edit_gist', gist_id=gist.gist_access_id, status=200))

    def test_edit_normal_user_not_his_own_gist(self, create_gist):
        self.log_user(TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS)
        gist = create_gist('delete-me')
        self.app.get(url('edit_gist', gist_id=gist.gist_access_id), status=403)

    def test_user_first_name_is_escaped(self, user_util, create_gist):
        xss_atack_string = '"><script>alert(\'First Name\')</script>'
        xss_escaped_string = (
            '&#34;&gt;&lt;script&gt;alert(&#39;First Name&#39;)&lt;/script'
            '&gt;')
        password = 'test'
        user = user_util.create_user(
            firstname=xss_atack_string, password=password)
        create_gist('gist', gist_type='public', owner=user.username)
        response = self.app.get(url('gists'))
        response.mustcontain(xss_escaped_string)

    def test_user_last_name_is_escaped(self, user_util, create_gist):
        xss_atack_string = '"><script>alert(\'Last Name\')</script>'
        xss_escaped_string = (
            '&#34;&gt;&lt;script&gt;alert(&#39;Last Name&#39;)&lt;/script&gt;')
        password = 'test'
        user = user_util.create_user(
            lastname=xss_atack_string, password=password)
        create_gist('gist', gist_type='public', owner=user.username)
        response = self.app.get(url('gists'))
        response.mustcontain(xss_escaped_string)
