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


import pylons

from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request

from rhodecode.translation import _ as tsf


def add_renderer_globals(event):
    # Put pylons stuff into the context. This will be removed as soon as
    # migration to pyramid is finished.
    conf = pylons.config._current_obj()
    event['h'] = conf.get('pylons.h')
    event['c'] = pylons.tmpl_context
    event['url'] = pylons.url

    # TODO: When executed in pyramid view context the request is not available
    # in the event. Find a better solution to get the request.
    request = event['request'] or get_current_request()

    # Add Pyramid translation as '_' to context
    event['_'] = request.translate
    event['localizer'] = request.localizer


def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)

    def auto_translate(*args, **kwargs):
        return localizer.translate(tsf(*args, **kwargs))

    request.localizer = localizer
    request.translate = auto_translate
