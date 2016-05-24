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
default settings controller for RhodeCode Enterprise
"""

import logging
import formencode
from formencode import htmlfill

from pylons import request, tmpl_context as c, url
from pylons.controllers.util import redirect
from pylons.i18n.translation import _

from rhodecode.lib import auth
from rhodecode.lib import helpers as h
from rhodecode.lib.auth import LoginRequired, HasPermissionAllDecorator
from rhodecode.lib.base import BaseController, render
from rhodecode.model.forms import DefaultsForm
from rhodecode.model.meta import Session
from rhodecode import BACKENDS
from rhodecode.model.settings import SettingsModel

log = logging.getLogger(__name__)


class DefaultsController(BaseController):

    @LoginRequired()
    def __before__(self):
        super(DefaultsController, self).__before__()

    @HasPermissionAllDecorator('hg.admin')
    def index(self):
        """GET /defaults: All items in the collection"""
        # url('admin_defaults_repositories')
        c.backends = BACKENDS.keys()
        c.active = 'repositories'
        defaults = SettingsModel().get_default_repo_settings()

        return htmlfill.render(
            render('admin/defaults/defaults.html'),
            defaults=defaults,
            encoding="UTF-8",
            force_defaults=False
        )

    @HasPermissionAllDecorator('hg.admin')
    @auth.CSRFRequired()
    def update_repository_defaults(self):
        """PUT /defaults/repositories: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        # Or using helpers:
        #    h.form(url('admin_defaults_repositories'),
        #           method='post')
        # url('admin_defaults_repositories')
        c.active = 'repositories'
        _form = DefaultsForm()()

        try:
            form_result = _form.to_python(dict(request.POST))
            for k, v in form_result.iteritems():
                setting = SettingsModel().create_or_update_setting(k, v)
                Session().add(setting)
            Session().commit()
            h.flash(_('Default settings updated successfully'),
                    category='success')

        except formencode.Invalid as errors:
            defaults = errors.value

            return htmlfill.render(
                render('admin/defaults/defaults.html'),
                defaults=defaults,
                errors=errors.error_dict or {},
                prefix_error=False,
                encoding="UTF-8",
                force_defaults=False)
        except Exception:
            log.exception('Exception in update action')
            h.flash(_('Error occurred during update of default values'),
                    category='error')

        return redirect(url('admin_defaults_repositories'))
