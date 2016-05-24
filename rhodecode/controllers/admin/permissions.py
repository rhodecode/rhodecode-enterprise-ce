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
permissions controller for RhodeCode Enterprise
"""


import logging

import formencode
from formencode import htmlfill
from pylons import request, tmpl_context as c, url
from pylons.controllers.util import redirect
from pylons.i18n.translation import _

from rhodecode.lib import helpers as h
from rhodecode.lib import auth
from rhodecode.lib.auth import (LoginRequired, HasPermissionAllDecorator)
from rhodecode.lib.base import BaseController, render
from rhodecode.model.db import User, UserIpMap
from rhodecode.model.forms import (
    ApplicationPermissionsForm, ObjectPermissionsForm, UserPermissionsForm)
from rhodecode.model.meta import Session
from rhodecode.model.permission import PermissionModel
from rhodecode.model.settings import SettingsModel

log = logging.getLogger(__name__)


class PermissionsController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('permission', 'permissions')

    @LoginRequired()
    def __before__(self):
        super(PermissionsController, self).__before__()

    def __load_data(self):
        PermissionModel().set_global_permission_choices(c, translator=_)

    @HasPermissionAllDecorator('hg.admin')
    def permission_application(self):
        c.active = 'application'
        self.__load_data()

        c.user = User.get_default_user()

        # TODO: johbo: The default user might be based on outdated state which
        # has been loaded from the cache. A call to refresh() ensures that the
        # latest state from the database is used.
        Session().refresh(c.user)

        app_settings = SettingsModel().get_all_settings()
        defaults = {
            'anonymous': c.user.active,
            'default_register_message': app_settings.get(
                'rhodecode_register_message')
        }
        defaults.update(c.user.get_default_perms())

        return htmlfill.render(
            render('admin/permissions/permissions.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def permission_application_update(self):
        c.active = 'application'
        self.__load_data()
        _form = ApplicationPermissionsForm(
            [x[0] for x in c.register_choices],
            [x[0] for x in c.extern_activate_choices])()

        try:
            form_result = _form.to_python(dict(request.POST))
            form_result.update({'perm_user_name': User.DEFAULT_USER})
            PermissionModel().update_application_permissions(form_result)

            settings = [
                ('register_message', 'default_register_message'),
            ]
            for setting, form_key in settings:
                sett = SettingsModel().create_or_update_setting(
                    setting, form_result[form_key])
                Session().add(sett)

            Session().commit()
            h.flash(_('Application permissions updated successfully'),
                    category='success')

        except formencode.Invalid as errors:
            defaults = errors.value

            return htmlfill.render(
                render('admin/permissions/permissions.html'),
                defaults=defaults,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except Exception:
            log.exception("Exception during update of permissions")
            h.flash(_('Error occurred during update of permissions'),
                    category='error')

        return redirect(url('admin_permissions_application'))

    @HasPermissionAllDecorator('hg.admin')
    def permission_objects(self):
        c.active = 'objects'
        self.__load_data()
        c.user = User.get_default_user()
        defaults = {}
        defaults.update(c.user.get_default_perms())
        return htmlfill.render(
            render('admin/permissions/permissions.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def permission_objects_update(self):
        c.active = 'objects'
        self.__load_data()
        _form = ObjectPermissionsForm(
            [x[0] for x in c.repo_perms_choices],
            [x[0] for x in c.group_perms_choices],
            [x[0] for x in c.user_group_perms_choices])()

        try:
            form_result = _form.to_python(dict(request.POST))
            form_result.update({'perm_user_name': User.DEFAULT_USER})
            PermissionModel().update_object_permissions(form_result)

            Session().commit()
            h.flash(_('Object permissions updated successfully'),
                    category='success')

        except formencode.Invalid as errors:
            defaults = errors.value

            return htmlfill.render(
                render('admin/permissions/permissions.html'),
                defaults=defaults,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except Exception:
            log.exception("Exception during update of permissions")
            h.flash(_('Error occurred during update of permissions'),
                    category='error')

        return redirect(url('admin_permissions_object'))

    @HasPermissionAllDecorator('hg.admin')
    def permission_global(self):
        c.active = 'global'
        self.__load_data()

        c.user = User.get_default_user()
        defaults = {}
        defaults.update(c.user.get_default_perms())

        return htmlfill.render(
            render('admin/permissions/permissions.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False)

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def permission_global_update(self):
        c.active = 'global'
        self.__load_data()
        _form = UserPermissionsForm(
            [x[0] for x in c.repo_create_choices],
            [x[0] for x in c.repo_create_on_write_choices],
            [x[0] for x in c.repo_group_create_choices],
            [x[0] for x in c.user_group_create_choices],
            [x[0] for x in c.fork_choices],
            [x[0] for x in c.inherit_default_permission_choices])()

        try:
            form_result = _form.to_python(dict(request.POST))
            form_result.update({'perm_user_name': User.DEFAULT_USER})
            PermissionModel().update_user_permissions(form_result)

            Session().commit()
            h.flash(_('Global permissions updated successfully'),
                    category='success')

        except formencode.Invalid as errors:
            defaults = errors.value

            return htmlfill.render(
                render('admin/permissions/permissions.html'),
                defaults=defaults,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except Exception:
            log.exception("Exception during update of permissions")
            h.flash(_('Error occurred during update of permissions'),
                    category='error')

        return redirect(url('admin_permissions_global'))

    @HasPermissionAllDecorator('hg.admin')
    def permission_ips(self):
        c.active = 'ips'
        c.user = User.get_default_user()
        c.user_ip_map = (
            UserIpMap.query().filter(UserIpMap.user == c.user).all())

        return render('admin/permissions/permissions.html')

    @HasPermissionAllDecorator('hg.admin')
    def permission_perms(self):
        c.active = 'perms'
        c.user = User.get_default_user()
        c.perm_user = c.user.AuthUser
        return render('admin/permissions/permissions.html')
