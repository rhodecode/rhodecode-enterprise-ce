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


from pyramid_debugtoolbar.panels import DebugPanel


class PylonsContextPanel(DebugPanel):
    """
    Shows the attributes in the Pylons context.
    """

    name = 'PylonsContext'
    has_content = True
    template = 'rhodecode.utils.debugtoolbar:templates/pylons_context.dbtmako'

    nav_title = 'Pylons Context'
    title = 'Pylons Context'

    def process_response(self, response):
        context = self._environ.get('debugtoolbar.pylons_context')
        if context:
            self.data['pylons_context'] = context.__dict__
        else:
            self.data['pylons_context'] = None

    def wrap_handler(self, handler):
        def wrapper(request):
            self._environ = request.environ
            request.environ['debugtoolbar.wants_pylons_context'] = True
            return handler(request)
        return wrapper


def includeme(config):
    config.registry.settings['debugtoolbar.panels'].append(PylonsContextPanel)
