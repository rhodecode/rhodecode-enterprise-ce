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
RhodeCode error controller
"""

import cgi
import logging
import os
import paste.fileapp

from pylons import tmpl_context as c, request, config, url
from pylons.i18n.translation import _
from pylons.middleware import media_path
from webob.exc import HTTPNotFound

from rhodecode.lib.base import BaseController, render
from rhodecode.lib.utils2 import AttributeDict
from rhodecode.model.settings import SettingsModel

log = logging.getLogger(__name__)


class ErrorController(BaseController):
    """Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behavior can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.
    """

    def __before__(self):

        try:
            rc_config = SettingsModel().get_all_settings()
        except Exception:
            log.exception('failed to fetch settings')
            rc_config = {}

        c.visual = AttributeDict({})
        c.visual.rhodecode_support_url = (
            rc_config.get('rhodecode_support_url') or url('rhodecode_support'))
        return

    def document(self):
        resp = request.environ.get('pylons.original_response', None)
        if not resp:
            raise HTTPNotFound()

        c.rhodecode_name = config.get('rhodecode_title')

        log.debug('### %s ###' % resp.status)

        e = request.environ
        c.serv_p = r'%(protocol)s://%(host)s/' % {
            'protocol': e.get('wsgi.url_scheme'),
            'host': e.get('HTTP_HOST'),
        }

        c.error_message = cgi.escape(request.GET.get('code', str(resp.status)))
        c.error_explanation = self.get_error_explanation(resp.status_int)

        #  redirect to when error with given seconds
        c.redirect_time = 0
        c.redirect_module = _('Home page')
        c.url_redirect = "/"

        return render('/errors/error_document.html')

    def img(self, id):
        """Serve Pylons' stock images"""
        return self._serve_file(os.path.join(media_path, 'img', id))

    def style(self, id):
        """Serve Pylons' stock stylesheets"""
        return self._serve_file(os.path.join(media_path, 'style', id))

    def _serve_file(self, path):
        """Call Paste's FileApp (a WSGI application) to serve the file
        at the specified path
        """
        fapp = paste.fileapp.FileApp(path)
        return fapp(request.environ, self.start_response)

    def get_error_explanation(self, code):
        """ get the error explanations of int codes
            [400, 401, 403, 404, 500]"""
        try:
            code = int(code)
        except Exception:
            code = 500

        if code == 400:
            return _('The request could not be understood by the server'
                     ' due to malformed syntax.')
        if code == 401:
            return _('Unauthorized access to resource')
        if code == 403:
            return _("You don't have permission to view this page")
        if code == 404:
            return _('The resource could not be found')
        if code == 500:
            return _('The server encountered an unexpected condition'
                     ' which prevented it from fulfilling the request.')

    def vcs_unavailable(self):
        c.rhodecode_name = config.get('rhodecode_title')
        c.error_message = _('VCS Server Required')
        c.error_explanation = _(
            'A VCS Server is required for this action. '
            'There is currently no VCS Server configured.')
        c.error_docs_link = 'https://docs.rhodecode.com/RhodeCode-Control/'\
            'tasks/upgrade-from-cli.html#manually-changing-vcs-server-settings'
        #  redirect to when error with given seconds
        c.redirect_time = 0
        c.redirect_module = _('Home page')
        c.url_redirect = "/"
        return render('/errors/error_document.html')
