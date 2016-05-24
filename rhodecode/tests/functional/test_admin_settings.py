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

import rhodecode
from rhodecode.lib.utils2 import md5
from rhodecode.model.db import RhodeCodeUi
from rhodecode.model.meta import Session
from rhodecode.model.settings import SettingsModel, IssueTrackerSettingsModel
from rhodecode.tests import url, assert_session_flash
from rhodecode.tests.utils import AssertResponse


UPDATE_DATA_QUALNAME = (
    'rhodecode.controllers.admin.settings.SettingsController.get_update_data')


@pytest.mark.usefixtures('autologin_user', 'app')
class TestAdminSettingsController:

    @pytest.mark.parametrize('urlname', [
        'admin_settings_vcs',
        'admin_settings_mapping',
        'admin_settings_global',
        'admin_settings_visual',
        'admin_settings_email',
        'admin_settings_hooks',
        'admin_settings_search',
        'admin_settings_system',
    ])
    def test_simple_get(self, urlname, app):
        app.get(url(urlname))

    def test_create_custom_hook(self, csrf_token):
        response = self.app.post(
            url('admin_settings_hooks'),
            params={
                'new_hook_ui_key': 'test_hooks_1',
                'new_hook_ui_value': 'cd /tmp',
                'csrf_token': csrf_token})

        response = response.follow()
        response.mustcontain('test_hooks_1')
        response.mustcontain('cd /tmp')

    def test_create_custom_hook_delete(self, csrf_token):
        response = self.app.post(
            url('admin_settings_hooks'),
            params={
                'new_hook_ui_key': 'test_hooks_2',
                'new_hook_ui_value': 'cd /tmp2',
                'csrf_token': csrf_token})

        response = response.follow()
        response.mustcontain('test_hooks_2')
        response.mustcontain('cd /tmp2')

        hook_id = SettingsModel().get_ui_by_key('test_hooks_2').ui_id

        # delete
        self.app.post(
            url('admin_settings_hooks'),
            params={'hook_id': hook_id, 'csrf_token': csrf_token})
        response = self.app.get(url('admin_settings_hooks'))
        response.mustcontain(no=['test_hooks_2'])
        response.mustcontain(no=['cd /tmp2'])

    def test_system_update_new_version(self):
        update_data = {
            'versions': [
                {
                    'version': '100.3.1415926535',
                    'general': 'The latest version we are ever going to ship'
                },
                {
                    'version': '0.0.0',
                    'general': 'The first version we ever shipped'
                }
            ]
        }
        with mock.patch(UPDATE_DATA_QUALNAME, return_value=update_data):
            response = self.app.get(url('admin_settings_system_update'))
            response.mustcontain('A <b>new version</b> is available')

    def test_system_update_nothing_new(self):
        update_data = {
            'versions': [
                {
                    'version': '0.0.0',
                    'general': 'The first version we ever shipped'
                }
            ]
        }
        with mock.patch(UPDATE_DATA_QUALNAME, return_value=update_data):
            response = self.app.get(url('admin_settings_system_update'))
            response.mustcontain(
                'You already have the <b>latest</b> stable version.')

    def test_system_update_bad_response(self):
        with mock.patch(UPDATE_DATA_QUALNAME, side_effect=ValueError('foo')):
            response = self.app.get(url('admin_settings_system_update'))
            response.mustcontain(
                'Bad data sent from update server')


@pytest.mark.usefixtures('autologin_user', 'app')
class TestAdminSettingsGlobal:

    def test_pre_post_code_code_active(self, csrf_token):
        pre_code = 'rc-pre-code-187652122'
        post_code = 'rc-postcode-98165231'

        response = self.post_and_verify_settings({
            'rhodecode_pre_code': pre_code,
            'rhodecode_post_code': post_code,
            'csrf_token': csrf_token,
        })

        response = response.follow()
        response.mustcontain(pre_code, post_code)

    def test_pre_post_code_code_inactive(self, csrf_token):
        pre_code = 'rc-pre-code-187652122'
        post_code = 'rc-postcode-98165231'
        response = self.post_and_verify_settings({
            'rhodecode_pre_code': '',
            'rhodecode_post_code': '',
            'csrf_token': csrf_token,
        })

        response = response.follow()
        response.mustcontain(no=[pre_code, post_code])

    def test_captcha_activate(self, csrf_token):
        self.post_and_verify_settings({
            'rhodecode_captcha_private_key': '1234567890',
            'rhodecode_captcha_public_key': '1234567890',
            'csrf_token': csrf_token,
        })

        response = self.app.get(url('register'))
        response.mustcontain('captcha')

    def test_captcha_deactivate(self, csrf_token):
        self.post_and_verify_settings({
            'rhodecode_captcha_private_key': '',
            'rhodecode_captcha_public_key': '1234567890',
            'csrf_token': csrf_token,
        })

        response = self.app.get(url('register'))
        response.mustcontain(no=['captcha'])

    def test_title_change(self, csrf_token):
        old_title = 'RhodeCode'
        new_title = old_title + '_changed'

        for new_title in ['Changed', 'Żółwik', old_title]:
            response = self.post_and_verify_settings({
                'rhodecode_title': new_title,
                'csrf_token': csrf_token,
            })

            response = response.follow()
            response.mustcontain(
                """<div class="branding">- %s</div>""" % new_title)

    def post_and_verify_settings(self, settings):
        old_title = 'RhodeCode'
        old_realm = 'RhodeCode authentication'
        params = {
            'rhodecode_title': old_title,
            'rhodecode_realm': old_realm,
            'rhodecode_pre_code': '',
            'rhodecode_post_code': '',
            'rhodecode_captcha_private_key': '',
            'rhodecode_captcha_public_key': '',
        }
        params.update(settings)
        response = self.app.post(url('admin_settings_global'), params=params)

        assert_session_flash(response, 'Updated application settings')
        app_settings = SettingsModel().get_all_settings()
        del settings['csrf_token']
        for key, value in settings.iteritems():
            assert app_settings[key] == value.decode('utf-8')

        return response


@pytest.mark.usefixtures('autologin_user', 'app')
class TestAdminSettingsVcs:

    def test_contains_svn_default_patterns(self, app):
        response = app.get(url('admin_settings_vcs'))
        expected_patterns = [
            '/trunk',
            '/branches/*',
            '/tags/*',
        ]
        for pattern in expected_patterns:
            response.mustcontain(pattern)

    def test_add_new_svn_branch_and_tag_pattern(
            self, app, backend_svn, form_defaults, disable_sql_cache,
            csrf_token):
        form_defaults.update({
            'new_svn_branch': '/exp/branches/*',
            'new_svn_tag': '/important_tags/*',
            'csrf_token': csrf_token,
        })

        response = app.post(
            url('admin_settings_vcs'), params=form_defaults, status=302)
        response = response.follow()

        # Expect to find the new values on the page
        response.mustcontain('/exp/branches/*')
        response.mustcontain('/important_tags/*')

        # Expect that those patterns are used to match branches and tags now
        repo = backend_svn['svn-simple-layout'].scm_instance()
        assert 'exp/branches/exp-sphinx-docs' in repo.branches
        assert 'important_tags/v0.5' in repo.tags

    def test_add_same_svn_value_twice_shows_an_error_message(
            self, app, form_defaults, csrf_token, settings_util):
        settings_util.create_rhodecode_ui('vcs_svn_branch', '/test')
        settings_util.create_rhodecode_ui('vcs_svn_tag', '/test')

        response = app.post(
            url('admin_settings_vcs'),
            params={
                'paths_root_path': form_defaults['paths_root_path'],
                'new_svn_branch': '/test',
                'new_svn_tag': '/test',
                'csrf_token': csrf_token,
            },
            status=200)

        response.mustcontain("Pattern already exists")
        response.mustcontain("Some form inputs contain invalid data.")

    @pytest.mark.parametrize('section', [
        'vcs_svn_branch',
        'vcs_svn_tag',
    ])
    def test_delete_svn_patterns(
            self, section, app, csrf_token, settings_util):
        setting = settings_util.create_rhodecode_ui(
            section, '/test_delete', cleanup=False)

        app.post(
            url('admin_settings_vcs'),
            params={
                '_method': 'delete',
                'delete_svn_pattern': setting.ui_id,
                'csrf_token': csrf_token},
            headers={'X-REQUESTED-WITH': 'XMLHttpRequest'})

    @pytest.mark.parametrize('section', [
        'vcs_svn_branch',
        'vcs_svn_tag',
    ])
    def test_delete_svn_patterns_raises_400_when_no_xhr(
            self, section, app, csrf_token, settings_util):
        setting = settings_util.create_rhodecode_ui(section, '/test_delete')

        app.post(
            url('admin_settings_vcs'),
            params={
                '_method': 'delete',
                'delete_svn_pattern': setting.ui_id,
                'csrf_token': csrf_token},
            status=400)

    def test_extensions_hgsubversion(self, app, form_defaults, csrf_token):
        form_defaults.update({
            'csrf_token': csrf_token,
            'extensions_hgsubversion': 'True',
        })
        response = app.post(
            url('admin_settings_vcs'),
            params=form_defaults,
            status=302)

        response = response.follow()
        extensions_input = (
            '<input id="extensions_hgsubversion" '
            'name="extensions_hgsubversion" type="checkbox" '
            'value="True" checked="checked" />')
        response.mustcontain(extensions_input)

    def test_has_a_section_for_pull_request_settings(self, app):
        response = app.get(url('admin_settings_vcs'))
        response.mustcontain('Pull Request Settings')

    def test_has_an_input_for_invalidation_of_inline_comments(
            self, app):
        response = app.get(url('admin_settings_vcs'))
        assert_response = AssertResponse(response)
        assert_response.one_element_exists(
            '[name=rhodecode_use_outdated_comments]')

    @pytest.mark.parametrize('new_value', [True, False])
    def test_allows_to_change_invalidation_of_inline_comments(
            self, app, form_defaults, csrf_token, new_value):
        setting_key = 'use_outdated_comments'
        setting = SettingsModel().create_or_update_setting(
            setting_key, not new_value, 'bool')
        Session().add(setting)
        Session().commit()

        form_defaults.update({
            'csrf_token': csrf_token,
            'rhodecode_use_outdated_comments': str(new_value),
        })
        response = app.post(
            url('admin_settings_vcs'),
            params=form_defaults,
            status=302)
        response = response.follow()
        setting = SettingsModel().get_setting_by_name(setting_key)
        assert setting.app_settings_value is new_value

    @pytest.fixture
    def disable_sql_cache(self, request):
        patcher = mock.patch(
            'rhodecode.lib.caching_query.FromCache.process_query')
        request.addfinalizer(patcher.stop)
        patcher.start()

    @pytest.fixture
    def form_defaults(self):
        from rhodecode.controllers.admin.settings import SettingsController
        controller = SettingsController()
        return controller._form_defaults()

    # TODO: johbo: What we really want is to checkpoint before a test run and
    # reset the session afterwards.
    @pytest.fixture(scope='class', autouse=True)
    def cleanup_settings(self, request, pylonsapp):
        ui_id = RhodeCodeUi.ui_id
        original_ids = list(
            r.ui_id for r in RhodeCodeUi.query().values(ui_id))

        @request.addfinalizer
        def cleanup():
            RhodeCodeUi.query().filter(
                ui_id.notin_(original_ids)).delete(False)


@pytest.mark.usefixtures('autologin_user', 'app')
class TestLabsSettings(object):
    def test_get_settings_page_disabled(self):
        with mock.patch.dict(rhodecode.CONFIG,
                             {'labs_settings_active': 'false'}):
            response = self.app.get(url('admin_settings_labs'), status=302)

        assert response.location.endswith(url('admin_settings'))

    def test_get_settings_page_enabled(self):
        from rhodecode.controllers.admin import settings
        lab_settings = [
            settings.LabSetting(
                key='rhodecode_bool',
                type='bool',
                group='bool group',
                label='bool label',
                help='bool help'
            ),
            settings.LabSetting(
                key='rhodecode_text',
                type='unicode',
                group='text group',
                label='text label',
                help='text help'
            ),
        ]
        with mock.patch.dict(rhodecode.CONFIG,
                             {'labs_settings_active': 'true'}):
            with mock.patch.object(settings, '_LAB_SETTINGS', lab_settings):
                response = self.app.get(url('admin_settings_labs'))

        assert '<label>bool group:</label>' in response
        assert '<label for="rhodecode_bool">bool label</label>' in response
        assert '<p class="help-block">bool help</p>' in response
        assert 'name="rhodecode_bool" type="checkbox"' in response

        assert '<label>text group:</label>' in response
        assert '<label for="rhodecode_text">text label</label>' in response
        assert '<p class="help-block">text help</p>' in response
        assert 'name="rhodecode_text" size="60" type="text"' in response

    @pytest.mark.parametrize('setting_name', [
        'proxy_subversion_http_requests',
        'hg_use_rebase_for_merging',
    ])
    def test_update_boolean_settings(self, csrf_token, setting_name):
        self.app.post(
            url('admin_settings_labs'),
            params={
                'rhodecode_{}'.format(setting_name): 'true',
                'csrf_token': csrf_token,
            })
        setting = SettingsModel().get_setting_by_name(setting_name)
        assert setting.app_settings_value

        self.app.post(
            url('admin_settings_labs'),
            params={
                'rhodecode_{}'.format(setting_name): 'false',
                'csrf_token': csrf_token,
            })
        setting = SettingsModel().get_setting_by_name(setting_name)
        assert not setting.app_settings_value

    @pytest.mark.parametrize('setting_name', [
        'subversion_http_server_url',
    ])
    def test_update_string_settings(self, csrf_token, setting_name):
        self.app.post(
            url('admin_settings_labs'),
            params={
                'rhodecode_{}'.format(setting_name): 'Test 1',
                'csrf_token': csrf_token,
            })
        setting = SettingsModel().get_setting_by_name(setting_name)
        assert setting.app_settings_value == 'Test 1'

        self.app.post(
            url('admin_settings_labs'),
            params={
                'rhodecode_{}'.format(setting_name): ' Test 2 ',
                'csrf_token': csrf_token,
            })
        setting = SettingsModel().get_setting_by_name(setting_name)
        assert setting.app_settings_value == 'Test 2'


@pytest.mark.usefixtures('app')
class TestOpenSourceLicenses(object):
    def test_records_are_displayed(self, autologin_user):
        sample_licenses = {
            "python2.7-pytest-2.7.1": {
                "UNKNOWN": None
            },
            "python2.7-Markdown-2.6.2": {
                "BSD-3-Clause": "http://spdx.org/licenses/BSD-3-Clause"
            }
        }
        read_licenses_patch = mock.patch(
            'rhodecode.controllers.admin.settings.read_opensource_licenses',
            return_value=sample_licenses)
        with read_licenses_patch:
            response = self.app.get(
                url('admin_settings_open_source'), status=200)

        assert_response = AssertResponse(response)
        assert_response.element_contains(
            '.panel-heading', 'Licenses of Third Party Packages')
        for name in sample_licenses:
            response.mustcontain(name)
            for license in sample_licenses[name]:
                assert_response.element_contains('.panel-body', license)

    def test_records_can_be_read(self, autologin_user):
        response = self.app.get(url('admin_settings_open_source'), status=200)
        assert_response = AssertResponse(response)
        assert_response.element_contains(
            '.panel-heading', 'Licenses of Third Party Packages')

    def test_forbidden_when_normal_user(self, autologin_regular_user):
        self.app.get(
            url('admin_settings_open_source'), status=403)


@pytest.mark.usefixtures("app")
class TestAdminSettingsIssueTracker:
    RC_PREFIX = 'rhodecode_'
    SHORT_PATTERN_KEY = 'issuetracker_pat_'
    PATTERN_KEY = RC_PREFIX + SHORT_PATTERN_KEY

    def test_issuetracker_index(self, autologin_user):
        response = self.app.get(url('admin_settings_issuetracker'))
        assert response.status_code == 200

    def test_add_issuetracker_pattern(
            self, request, autologin_user, csrf_token):
        pattern = 'issuetracker_pat'
        another_pattern = pattern+'1'
        post_url = url('admin_settings_issuetracker_save')
        post_data = {
            'new_pattern_pattern_0': pattern,
            'new_pattern_url_0': 'url',
            'new_pattern_prefix_0': 'prefix',
            'new_pattern_description_0': 'description',
            'new_pattern_pattern_1': another_pattern,
            'new_pattern_url_1': 'url1',
            'new_pattern_prefix_1': 'prefix1',
            'new_pattern_description_1': 'description1',
            'csrf_token': csrf_token
        }
        self.app.post(post_url, post_data, status=302)
        settings = SettingsModel().get_all_settings()
        self.uid = md5(pattern)
        assert settings[self.PATTERN_KEY+self.uid] == pattern
        self.another_uid = md5(another_pattern)
        assert settings[self.PATTERN_KEY+self.another_uid] == another_pattern

        @request.addfinalizer
        def cleanup():
            defaults = SettingsModel().get_all_settings()

            entries = [name for name in defaults if (
                (self.uid in name) or (self.another_uid) in name)]
            start = len(self.RC_PREFIX)
            for del_key in entries:
                # TODO: anderson: get_by_name needs name without prefix
                entry = SettingsModel().get_setting_by_name(del_key[start:])
                Session().delete(entry)

            Session().commit()

    def test_edit_issuetracker_pattern(
            self, autologin_user, backend, csrf_token, request):
        old_pattern = 'issuetracker_pat'
        old_uid = md5(old_pattern)
        pattern = 'issuetracker_pat_new'
        self.new_uid = md5(pattern)

        SettingsModel().create_or_update_setting(
            self.SHORT_PATTERN_KEY+old_uid, old_pattern, 'unicode')

        post_url = url('admin_settings_issuetracker_save')
        post_data = {
            'new_pattern_pattern_0': pattern,
            'new_pattern_url_0': 'url',
            'new_pattern_prefix_0': 'prefix',
            'new_pattern_description_0': 'description',
            'uid': old_uid,
            'csrf_token': csrf_token
        }
        self.app.post(post_url, post_data, status=302)
        settings = SettingsModel().get_all_settings()
        assert settings[self.PATTERN_KEY+self.new_uid] == pattern
        assert self.PATTERN_KEY+old_uid not in settings

        @request.addfinalizer
        def cleanup():
            IssueTrackerSettingsModel().delete_entries(self.new_uid)

    def test_replace_issuetracker_pattern_description(
            self, autologin_user, csrf_token, request, settings_util):
        prefix = 'issuetracker'
        pattern = 'issuetracker_pat'
        self.uid = md5(pattern)
        pattern_key = '_'.join([prefix, 'pat', self.uid])
        rc_pattern_key = '_'.join(['rhodecode', pattern_key])
        desc_key = '_'.join([prefix, 'desc', self.uid])
        rc_desc_key = '_'.join(['rhodecode', desc_key])
        new_description = 'new_description'

        settings_util.create_rhodecode_setting(
            pattern_key, pattern, 'unicode', cleanup=False)
        settings_util.create_rhodecode_setting(
            desc_key, 'old description', 'unicode', cleanup=False)

        post_url = url('admin_settings_issuetracker_save')
        post_data = {
            'new_pattern_pattern_0': pattern,
            'new_pattern_url_0': 'url',
            'new_pattern_prefix_0': 'prefix',
            'new_pattern_description_0': new_description,
            'uid': self.uid,
            'csrf_token': csrf_token
        }
        self.app.post(post_url, post_data, status=302)
        settings = SettingsModel().get_all_settings()
        assert settings[rc_pattern_key] == pattern
        assert settings[rc_desc_key] == new_description

        @request.addfinalizer
        def cleanup():
            IssueTrackerSettingsModel().delete_entries(self.uid)

    def test_delete_issuetracker_pattern(
            self, autologin_user, backend, csrf_token, settings_util):
        pattern = 'issuetracker_pat'
        uid = md5(pattern)
        settings_util.create_rhodecode_setting(
            self.SHORT_PATTERN_KEY+uid, pattern, 'unicode', cleanup=False)

        post_url = url('admin_issuetracker_delete')
        post_data = {
            '_method': 'delete',
            'uid': uid,
            'csrf_token': csrf_token
        }
        self.app.post(post_url, post_data, status=302)
        settings = SettingsModel().get_all_settings()
        assert 'rhodecode_%s%s' % (self.SHORT_PATTERN_KEY, uid) not in settings
