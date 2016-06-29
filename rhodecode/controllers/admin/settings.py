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


"""
settings controller for rhodecode admin
"""

import collections
import logging
import urllib2

import datetime
import formencode
from formencode import htmlfill
import packaging.version
from pylons import request, tmpl_context as c, url, config
from pylons.controllers.util import redirect
from pylons.i18n.translation import _, lazy_ugettext
from webob.exc import HTTPBadRequest

import rhodecode
from rhodecode.admin.navigation import navigation
from rhodecode.lib import auth
from rhodecode.lib import helpers as h
from rhodecode.lib.auth import LoginRequired, HasPermissionAllDecorator
from rhodecode.lib.base import BaseController, render
from rhodecode.lib.celerylib import tasks, run_task
from rhodecode.lib.utils import repo2db_mapper
from rhodecode.lib.utils2 import (
    str2bool, safe_unicode, AttributeDict, safe_int)
from rhodecode.lib.compat import OrderedDict
from rhodecode.lib.ext_json import json
from rhodecode.lib.utils import jsonify

from rhodecode.model.db import RhodeCodeUi, Repository
from rhodecode.model.forms import ApplicationSettingsForm, \
    ApplicationUiSettingsForm, ApplicationVisualisationForm, \
    LabsSettingsForm, IssueTrackerPatternsForm

from rhodecode.model.scm import ScmModel
from rhodecode.model.notification import EmailNotificationModel
from rhodecode.model.meta import Session
from rhodecode.model.settings import (
    IssueTrackerSettingsModel, VcsSettingsModel, SettingNotFound,
    SettingsModel)

from rhodecode.model.supervisor import SupervisorModel, SUPERVISOR_MASTER


log = logging.getLogger(__name__)


class SettingsController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('setting', 'settings', controller='admin/settings',
    #         path_prefix='/admin', name_prefix='admin_')

    @LoginRequired()
    def __before__(self):
        super(SettingsController, self).__before__()
        c.labs_active = str2bool(
            rhodecode.CONFIG.get('labs_settings_active', 'false'))
        c.navlist = navigation.get_navlist(request)

    def _get_hg_ui_settings(self):
        ret = RhodeCodeUi.query().all()

        if not ret:
            raise Exception('Could not get application ui settings !')
        settings = {}
        for each in ret:
            k = each.ui_key
            v = each.ui_value
            if k == '/':
                k = 'root_path'

            if k in ['push_ssl', 'publish']:
                v = str2bool(v)

            if k.find('.') != -1:
                k = k.replace('.', '_')

            if each.ui_section in ['hooks', 'extensions']:
                v = each.ui_active

            settings[each.ui_section + '_' + k] = v
        return settings

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    @jsonify
    def delete_svn_pattern(self):
        if not request.is_xhr:
            raise HTTPBadRequest()

        delete_pattern_id = request.POST.get('delete_svn_pattern')
        model = VcsSettingsModel()
        try:
            model.delete_global_svn_pattern(delete_pattern_id)
        except SettingNotFound:
            raise HTTPBadRequest()

        Session().commit()
        return True

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def settings_vcs_update(self):
        """POST /admin/settings: All items in the collection"""
        # url('admin_settings_vcs')
        c.active = 'vcs'

        model = VcsSettingsModel()
        c.svn_branch_patterns = model.get_global_svn_branch_patterns()
        c.svn_tag_patterns = model.get_global_svn_tag_patterns()

        application_form = ApplicationUiSettingsForm()()
        try:
            form_result = application_form.to_python(dict(request.POST))
        except formencode.Invalid as errors:
            h.flash(
                _("Some form inputs contain invalid data."),
                category='error')
            return htmlfill.render(
                render('admin/settings/settings.html'),
                defaults=errors.value,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False
            )

        try:
            model.update_global_ssl_setting(form_result['web_push_ssl'])
            if c.visual.allow_repo_location_change:
                model.update_global_path_setting(
                    form_result['paths_root_path'])
            model.update_global_hook_settings(form_result)
            model.create_global_svn_settings(form_result)
            model.create_or_update_global_hg_settings(form_result)
            model.create_or_update_global_pr_settings(form_result)
        except Exception:
            log.exception("Exception while updating settings")
            h.flash(_('Error occurred during updating '
                      'application settings'), category='error')
        else:
            Session().commit()
            h.flash(_('Updated VCS settings'), category='success')
            return redirect(url('admin_settings_vcs'))

        return htmlfill.render(
            render('admin/settings/settings.html'),
            defaults=self._form_defaults(),
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    def settings_vcs(self):
        """GET /admin/settings: All items in the collection"""
        # url('admin_settings_vcs')
        c.active = 'vcs'
        model = VcsSettingsModel()
        c.svn_branch_patterns = model.get_global_svn_branch_patterns()
        c.svn_tag_patterns = model.get_global_svn_tag_patterns()

        return htmlfill.render(
            render('admin/settings/settings.html'),
            defaults=self._form_defaults(),
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def settings_mapping_update(self):
        """POST /admin/settings/mapping: All items in the collection"""
        # url('admin_settings_mapping')
        c.active = 'mapping'
        rm_obsolete = request.POST.get('destroy', False)
        invalidate_cache = request.POST.get('invalidate', False)
        log.debug(
            'rescanning repo location with destroy obsolete=%s', rm_obsolete)

        if invalidate_cache:
            log.debug('invalidating all repositories cache')
            for repo in Repository.get_all():
                ScmModel().mark_for_invalidation(repo.repo_name, delete=True)

        filesystem_repos = ScmModel().repo_scan()
        added, removed = repo2db_mapper(filesystem_repos, rm_obsolete)
        _repr = lambda l: ', '.join(map(safe_unicode, l)) or '-'
        h.flash(_('Repositories successfully '
                  'rescanned added: %s ; removed: %s') %
                (_repr(added), _repr(removed)),
                category='success')
        return redirect(url('admin_settings_mapping'))

    @HasPermissionAllDecorator('hg.admin')
    def settings_mapping(self):
        """GET /admin/settings/mapping: All items in the collection"""
        # url('admin_settings_mapping')
        c.active = 'mapping'

        return htmlfill.render(
            render('admin/settings/settings.html'),
            defaults=self._form_defaults(),
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def settings_global_update(self):
        """POST /admin/settings/global: All items in the collection"""
        # url('admin_settings_global')
        c.active = 'global'
        application_form = ApplicationSettingsForm()()
        try:
            form_result = application_form.to_python(dict(request.POST))
        except formencode.Invalid as errors:
            return htmlfill.render(
                render('admin/settings/settings.html'),
                defaults=errors.value,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)

        try:
            settings = [
                ('title', 'rhodecode_title'),
                ('realm', 'rhodecode_realm'),
                ('pre_code', 'rhodecode_pre_code'),
                ('post_code', 'rhodecode_post_code'),
                ('captcha_public_key', 'rhodecode_captcha_public_key'),
                ('captcha_private_key', 'rhodecode_captcha_private_key'),
            ]
            for setting, form_key in settings:
                sett = SettingsModel().create_or_update_setting(
                    setting, form_result[form_key])
                Session().add(sett)

            Session().commit()
            SettingsModel().invalidate_settings_cache()
            h.flash(_('Updated application settings'), category='success')
        except Exception:
            log.exception("Exception while updating application settings")
            h.flash(
                _('Error occurred during updating application settings'),
                category='error')

        return redirect(url('admin_settings_global'))

    @HasPermissionAllDecorator('hg.admin')
    def settings_global(self):
        """GET /admin/settings/global: All items in the collection"""
        # url('admin_settings_global')
        c.active = 'global'

        return htmlfill.render(
            render('admin/settings/settings.html'),
            defaults=self._form_defaults(),
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def settings_visual_update(self):
        """POST /admin/settings/visual: All items in the collection"""
        # url('admin_settings_visual')
        c.active = 'visual'
        application_form = ApplicationVisualisationForm()()
        try:
            form_result = application_form.to_python(dict(request.POST))
        except formencode.Invalid as errors:
            return htmlfill.render(
                render('admin/settings/settings.html'),
                defaults=errors.value,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False
            )

        try:
            settings = [
                ('show_public_icon', 'rhodecode_show_public_icon', 'bool'),
                ('show_private_icon', 'rhodecode_show_private_icon', 'bool'),
                ('stylify_metatags', 'rhodecode_stylify_metatags', 'bool'),
                ('repository_fields', 'rhodecode_repository_fields', 'bool'),
                ('dashboard_items', 'rhodecode_dashboard_items', 'int'),
                ('admin_grid_items', 'rhodecode_admin_grid_items', 'int'),
                ('show_version', 'rhodecode_show_version', 'bool'),
                ('use_gravatar', 'rhodecode_use_gravatar', 'bool'),
                ('markup_renderer', 'rhodecode_markup_renderer', 'unicode'),
                ('gravatar_url', 'rhodecode_gravatar_url', 'unicode'),
                ('clone_uri_tmpl', 'rhodecode_clone_uri_tmpl', 'unicode'),
                ('support_url', 'rhodecode_support_url', 'unicode'),
                ('show_revision_number', 'rhodecode_show_revision_number', 'bool'),
                ('show_sha_length', 'rhodecode_show_sha_length', 'int'),
            ]
            for setting, form_key, type_ in settings:
                sett = SettingsModel().create_or_update_setting(
                    setting, form_result[form_key], type_)
                Session().add(sett)

            Session().commit()
            SettingsModel().invalidate_settings_cache()
            h.flash(_('Updated visualisation settings'), category='success')
        except Exception:
            log.exception("Exception updating visualization settings")
            h.flash(_('Error occurred during updating '
                      'visualisation settings'),
                    category='error')

        return redirect(url('admin_settings_visual'))

    @HasPermissionAllDecorator('hg.admin')
    def settings_visual(self):
        """GET /admin/settings/visual: All items in the collection"""
        # url('admin_settings_visual')
        c.active = 'visual'

        return htmlfill.render(
            render('admin/settings/settings.html'),
            defaults=self._form_defaults(),
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def settings_issuetracker_test(self):
        if request.is_xhr:
            return h.urlify_commit_message(
                request.POST.get('test_text', ''),
                'repo_group/test_repo1')
        else:
            raise HTTPBadRequest()

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def settings_issuetracker_delete(self):
        uid = request.POST.get('uid')
        IssueTrackerSettingsModel().delete_entries(uid)
        h.flash(_('Removed issue tracker entry'), category='success')
        return redirect(url('admin_settings_issuetracker'))

    @HasPermissionAllDecorator('hg.admin')
    def settings_issuetracker(self):
        """GET /admin/settings/issue-tracker: All items in the collection"""
        # url('admin_settings_issuetracker')
        c.active = 'issuetracker'
        defaults = SettingsModel().get_all_settings()

        entry_key = 'rhodecode_issuetracker_pat_'

        c.issuetracker_entries = {}
        for k, v in defaults.items():
            if k.startswith(entry_key):
                uid = k[len(entry_key):]
                c.issuetracker_entries[uid] = None

        for uid in c.issuetracker_entries:
            c.issuetracker_entries[uid] = AttributeDict({
                'pat': defaults.get('rhodecode_issuetracker_pat_' + uid),
                'url': defaults.get('rhodecode_issuetracker_url_' + uid),
                'pref': defaults.get('rhodecode_issuetracker_pref_' + uid),
                'desc': defaults.get('rhodecode_issuetracker_desc_' + uid),
            })

        return render('admin/settings/settings.html')

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def settings_issuetracker_save(self):
        settings_model = IssueTrackerSettingsModel()

        form = IssueTrackerPatternsForm()().to_python(request.POST)
        for uid in form['delete_patterns']:
            settings_model.delete_entries(uid)

        for pattern in form['patterns']:
            for setting, value, type_ in pattern:
                sett = settings_model.create_or_update_setting(
                    setting, value, type_)
                Session().add(sett)

            Session().commit()

        SettingsModel().invalidate_settings_cache()
        h.flash(_('Updated issue tracker entries'), category='success')
        return redirect(url('admin_settings_issuetracker'))

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def settings_email_update(self):
        """POST /admin/settings/email: All items in the collection"""
        # url('admin_settings_email')
        c.active = 'email'

        test_email = request.POST.get('test_email')

        if not test_email:
            h.flash(_('Please enter email address'), category='error')
            return redirect(url('admin_settings_email'))

        email_kwargs = {
            'date': datetime.datetime.now(),
            'user': c.rhodecode_user,
            'rhodecode_version': c.rhodecode_version
        }

        (subject, headers, email_body,
         email_body_plaintext) = EmailNotificationModel().render_email(
            EmailNotificationModel.TYPE_EMAIL_TEST, **email_kwargs)

        recipients = [test_email] if test_email else None

        run_task(tasks.send_email, recipients, subject,
                 email_body_plaintext, email_body)

        h.flash(_('Send email task created'), category='success')
        return redirect(url('admin_settings_email'))

    @HasPermissionAllDecorator('hg.admin')
    def settings_email(self):
        """GET /admin/settings/email: All items in the collection"""
        # url('admin_settings_email')
        c.active = 'email'
        c.rhodecode_ini = rhodecode.CONFIG

        return htmlfill.render(
            render('admin/settings/settings.html'),
            defaults=self._form_defaults(),
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def settings_hooks_update(self):
        """POST or DELETE /admin/settings/hooks: All items in the collection"""
        # url('admin_settings_hooks')
        c.active = 'hooks'
        if c.visual.allow_custom_hooks_settings:
            ui_key = request.POST.get('new_hook_ui_key')
            ui_value = request.POST.get('new_hook_ui_value')

            hook_id = request.POST.get('hook_id')
            new_hook = False

            model = SettingsModel()
            try:
                if ui_value and ui_key:
                    model.create_or_update_hook(ui_key, ui_value)
                    h.flash(_('Added new hook'), category='success')
                    new_hook = True
                elif hook_id:
                    RhodeCodeUi.delete(hook_id)
                    Session().commit()

                # check for edits
                update = False
                _d = request.POST.dict_of_lists()
                for k, v in zip(_d.get('hook_ui_key', []),
                                _d.get('hook_ui_value_new', [])):
                    model.create_or_update_hook(k, v)
                    update = True

                if update and not new_hook:
                    h.flash(_('Updated hooks'), category='success')
                Session().commit()
            except Exception:
                log.exception("Exception during hook creation")
                h.flash(_('Error occurred during hook creation'),
                        category='error')

        return redirect(url('admin_settings_hooks'))

    @HasPermissionAllDecorator('hg.admin')
    def settings_hooks(self):
        """GET /admin/settings/hooks: All items in the collection"""
        # url('admin_settings_hooks')
        c.active = 'hooks'

        model = SettingsModel()
        c.hooks = model.get_builtin_hooks()
        c.custom_hooks = model.get_custom_hooks()

        return htmlfill.render(
            render('admin/settings/settings.html'),
            defaults=self._form_defaults(),
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    def settings_search(self):
        """GET /admin/settings/search: All items in the collection"""
        # url('admin_settings_search')
        c.active = 'search'

        from rhodecode.lib.index import searcher_from_config
        searcher = searcher_from_config(config)
        c.statistics = searcher.statistics()

        return render('admin/settings/settings.html')

    @HasPermissionAllDecorator('hg.admin')
    def settings_system(self):
        """GET /admin/settings/system: All items in the collection"""
        # url('admin_settings_system')
        snapshot = str2bool(request.GET.get('snapshot'))
        c.active = 'system'

        defaults = self._form_defaults()
        c.rhodecode_ini = rhodecode.CONFIG
        c.rhodecode_update_url = defaults.get('rhodecode_update_url')
        server_info = ScmModel().get_server_info(request.environ)
        for key, val in server_info.iteritems():
            setattr(c, key, val)

        if c.disk['percent'] > 90:
            h.flash(h.literal(_(
                'Critical: your disk space is very low <b>%s%%</b> used' %
                c.disk['percent'])), 'error')
        elif c.disk['percent'] > 70:
            h.flash(h.literal(_(
                'Warning: your disk space is running low <b>%s%%</b> used' %
                c.disk['percent'])), 'warning')

        try:
            c.uptime_age = h._age(
                h.time_to_datetime(c.boot_time), False, show_suffix=False)
        except TypeError:
            c.uptime_age = c.boot_time

        try:
            c.system_memory = '%s/%s, %s%% (%s%%) used%s' % (
                h.format_byte_size_binary(c.memory['used']),
                h.format_byte_size_binary(c.memory['total']),
                c.memory['percent2'],
                c.memory['percent'],
                ' %s' % c.memory['error'] if 'error' in c.memory else '')
        except TypeError:
            c.system_memory = 'NOT AVAILABLE'

        rhodecode_ini_safe = rhodecode.CONFIG.copy()
        blacklist = [
            'rhodecode_license_key',
            'routes.map',
            'pylons.h',
            'pylons.app_globals',
            'pylons.environ_config',
            'sqlalchemy.db1.url',
            ('app_conf', 'sqlalchemy.db1.url')
        ]
        for k in blacklist:
            if isinstance(k, tuple):
                section, key = k
                if section in rhodecode_ini_safe:
                    rhodecode_ini_safe[section].pop(key, None)
            else:
                rhodecode_ini_safe.pop(k, None)

        c.rhodecode_ini_safe = rhodecode_ini_safe

        # TODO: marcink, figure out how to allow only selected users to do this
        c.allowed_to_snapshot = False

        if snapshot:
            if c.allowed_to_snapshot:
                return render('admin/settings/settings_system_snapshot.html')
            else:
                h.flash('You are not allowed to do this', category='warning')

        return htmlfill.render(
            render('admin/settings/settings.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False)

    @staticmethod
    def get_update_data(update_url):
        """Return the JSON update data."""
        ver = rhodecode.__version__
        log.debug('Checking for upgrade on `%s` server', update_url)
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'RhodeCode-SCM/%s' % ver)]
        response = opener.open(update_url)
        response_data = response.read()
        data = json.loads(response_data)

        return data

    @HasPermissionAllDecorator('hg.admin')
    def settings_system_update(self):
        """GET /admin/settings/system/updates: All items in the collection"""
        # url('admin_settings_system_update')
        defaults = self._form_defaults()
        update_url = defaults.get('rhodecode_update_url', '')

        _err = lambda s: '<div style="color:#ff8888; padding:4px 0px">%s</div>' % (s)
        try:
            data = self.get_update_data(update_url)
        except urllib2.URLError as e:
            log.exception("Exception contacting upgrade server")
            return _err('Failed to contact upgrade server: %r' % e)
        except ValueError as e:
            log.exception("Bad data sent from update server")
            return _err('Bad data sent from update server')

        latest = data['versions'][0]

        c.update_url = update_url
        c.latest_data = latest
        c.latest_ver = latest['version']
        c.cur_ver = rhodecode.__version__
        c.should_upgrade = False

        if (packaging.version.Version(c.latest_ver) >
                packaging.version.Version(c.cur_ver)):
            c.should_upgrade = True
        c.important_notices = latest['general']

        return render('admin/settings/settings_system_update.html')

    @HasPermissionAllDecorator('hg.admin')
    def settings_supervisor(self):
        c.rhodecode_ini = rhodecode.CONFIG
        c.active = 'supervisor'

        c.supervisor_procs = OrderedDict([
            (SUPERVISOR_MASTER, {}),
        ])

        c.log_size = 10240
        supervisor = SupervisorModel()

        _connection = supervisor.get_connection(
            c.rhodecode_ini.get('supervisor.uri'))
        c.connection_error = None
        try:
            _connection.supervisor.getAllProcessInfo()
        except Exception as e:
            c.connection_error = str(e)
            log.exception("Exception reading supervisor data")
            return render('admin/settings/settings.html')

        groupid = c.rhodecode_ini.get('supervisor.group_id')

        # feed our group processes to the main
        for proc in supervisor.get_group_processes(_connection, groupid):
            c.supervisor_procs[proc['name']] = {}

        for k in c.supervisor_procs.keys():
            try:
                # master process info
                if k == SUPERVISOR_MASTER:
                    _data = supervisor.get_master_state(_connection)
                    _data['name'] = 'supervisor master'
                    _data['description'] = 'pid %s, id: %s, ver: %s' % (
                        _data['pid'], _data['id'], _data['ver'])
                    c.supervisor_procs[k] = _data
                else:
                    procid = groupid + ":" + k
                    c.supervisor_procs[k] = supervisor.get_process_info(_connection, procid)
            except Exception as e:
                log.exception("Exception reading supervisor data")
                c.supervisor_procs[k] = {'_rhodecode_error': str(e)}

        return render('admin/settings/settings.html')

    @HasPermissionAllDecorator('hg.admin')
    def settings_supervisor_log(self, procid):
        import rhodecode
        c.rhodecode_ini = rhodecode.CONFIG
        c.active = 'supervisor_tail'

        supervisor = SupervisorModel()
        _connection = supervisor.get_connection(c.rhodecode_ini.get('supervisor.uri'))
        groupid = c.rhodecode_ini.get('supervisor.group_id')
        procid = groupid + ":" + procid if procid != SUPERVISOR_MASTER else procid

        c.log_size = 10240
        offset = abs(safe_int(request.GET.get('offset', c.log_size))) * -1
        c.log = supervisor.read_process_log(_connection, procid, offset, 0)

        return render('admin/settings/settings.html')

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def settings_labs_update(self):
        """POST /admin/settings/labs: All items in the collection"""
        # url('admin_settings/labs', method={'POST'})
        c.active = 'labs'

        application_form = LabsSettingsForm()()
        try:
            form_result = application_form.to_python(dict(request.POST))
        except formencode.Invalid as errors:
            h.flash(
                _('Some form inputs contain invalid data.'),
                category='error')
            return htmlfill.render(
                render('admin/settings/settings.html'),
                defaults=errors.value,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding='UTF-8',
                force_defaults=False
            )

        try:
            session = Session()
            for setting in _LAB_SETTINGS:
                setting_name = setting.key[len('rhodecode_'):]
                sett = SettingsModel().create_or_update_setting(
                    setting_name, form_result[setting.key], setting.type)
                session.add(sett)

        except Exception:
            log.exception('Exception while updating lab settings')
            h.flash(_('Error occurred during updating labs settings'),
                    category='error')
        else:
            Session().commit()
            SettingsModel().invalidate_settings_cache()
            h.flash(_('Updated Labs settings'), category='success')
            return redirect(url('admin_settings_labs'))

        return htmlfill.render(
            render('admin/settings/settings.html'),
            defaults=self._form_defaults(),
            encoding='UTF-8',
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    def settings_labs(self):
        """GET /admin/settings/labs: All items in the collection"""
        # url('admin_settings_labs')
        if not c.labs_active:
            redirect(url('admin_settings'))

        c.active = 'labs'
        c.lab_settings = _LAB_SETTINGS

        return htmlfill.render(
            render('admin/settings/settings.html'),
            defaults=self._form_defaults(),
            encoding='UTF-8',
            force_defaults=False)

    def _form_defaults(self):
        defaults = SettingsModel().get_all_settings()
        defaults.update(self._get_hg_ui_settings())
        defaults.update({
            'new_svn_branch': '',
            'new_svn_tag': '',
        })
        return defaults


# :param key: name of the setting including the 'rhodecode_' prefix
# :param type: the RhodeCodeSetting type to use.
# :param group: the i18ned group in which we should dispaly this setting
# :param label: the i18ned label we should display for this setting
# :param help: the i18ned help we should dispaly for this setting
LabSetting = collections.namedtuple(
    'LabSetting', ('key', 'type', 'group', 'label', 'help'))


# This list has to be kept in sync with the form
# rhodecode.model.forms.LabsSettingsForm.
_LAB_SETTINGS = [
    LabSetting(
        key='rhodecode_hg_use_rebase_for_merging',
        type='bool',
        group=lazy_ugettext('Mercurial server-side merge'),
        label=lazy_ugettext('Use rebase instead of creating a merge commit when merging via web interface'),
        help=''  # Do not translate the empty string!
    ),
    LabSetting(
        key='rhodecode_proxy_subversion_http_requests',
        type='bool',
        group=lazy_ugettext('Subversion HTTP Support'),
        label=lazy_ugettext('Proxy subversion HTTP requests'),
        help=''  # Do not translate the empty string!
    ),
    LabSetting(
        key='rhodecode_subversion_http_server_url',
        type='str',
        group=lazy_ugettext('Subversion HTTP Server URL'),
        label='',  # Do not translate the empty string!
        help=lazy_ugettext('e.g. http://localhost:8080/')
    ),
]
