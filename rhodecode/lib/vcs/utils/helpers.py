# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016  RhodeCode GmbH
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
Utilities aimed to help achieve mostly basic tasks.
"""


from __future__ import division

import re
import os
import time
import datetime
import logging

from rhodecode.lib.vcs.conf import settings
from rhodecode.lib.vcs.exceptions import VCSError, VCSBackendNotSupportedError


log = logging.getLogger(__name__)


def get_scm(path, search_path_up=False, explicit_alias=None):
    """
    Returns one of alias from ``ALIASES`` (in order of precedence same as
    shortcuts given in ``ALIASES``) and top working dir path for the given
    argument. If no scm-specific directory is found or more than one scm is
    found at that directory, ``VCSError`` is raised.

    :param search_path_up: if set to ``True``, this function would try to
      move up to parent directory every time no scm is recognized for the
      currently checked path. Default: ``False``.
    :param explicit_alias: can be one of available backend aliases, when given
      it will return given explicit alias in repositories under more than one
      version control, if explicit_alias is different than found it will raise
      VCSError
    """
    if not os.path.isdir(path):
        raise VCSError("Given path %s is not a directory" % path)

    def get_scms(path):
        return [(scm, path) for scm in get_scms_for_path(path)]

    found_scms = get_scms(path)
    while not found_scms and search_path_up:
        newpath = os.path.abspath(os.path.join(path, os.pardir))
        if newpath == path:
            break
        path = newpath
        found_scms = get_scms(path)

    if len(found_scms) > 1:
        for scm in found_scms:
            if scm[0] == explicit_alias:
                return scm
        found = ', '.join((x[0] for x in found_scms))
        raise VCSError(
            'More than one [%s] scm found at given path %s' % (found, path))

    if len(found_scms) is 0:
        raise VCSError('No scm found at given path %s' % path)

    return found_scms[0]


def get_scm_backend(backend_type):
    from rhodecode.lib.vcs.backends import get_backend
    return get_backend(backend_type)


def get_scms_for_path(path):
    """
    Returns all scm's found at the given path. If no scm is recognized
    - empty list is returned.

    :param path: path to directory which should be checked. May be callable.

    :raises VCSError: if given ``path`` is not a directory
    """
    from rhodecode.lib.vcs.backends import get_backend
    if hasattr(path, '__call__'):
        path = path()
    if not os.path.isdir(path):
        raise VCSError("Given path %r is not a directory" % path)

    result = []
    for key in settings.available_aliases():
        try:
            backend = get_backend(key)
        except VCSBackendNotSupportedError:
            log.warning('VCSBackendNotSupportedError: %s not supported', key)
            continue
        if backend.is_valid_repository(path):
            result.append(key)
    return result


def parse_datetime(text):
    """
    Parses given text and returns ``datetime.datetime`` instance or raises
    ``ValueError``.

    :param text: string of desired date/datetime or something more verbose,
      like *yesterday*, *2weeks 3days*, etc.
    """

    text = text.strip().lower()

    INPUT_FORMATS = (
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y %H:%M',
        '%m/%d/%Y',
        '%m/%d/%y %H:%M:%S',
        '%m/%d/%y %H:%M',
        '%m/%d/%y',
    )
    for format in INPUT_FORMATS:
        try:
            return datetime.datetime(*time.strptime(text, format)[:6])
        except ValueError:
            pass

    # Try descriptive texts
    if text == 'tomorrow':
        future = datetime.datetime.now() + datetime.timedelta(days=1)
        args = future.timetuple()[:3] + (23, 59, 59)
        return datetime.datetime(*args)
    elif text == 'today':
        return datetime.datetime(*datetime.datetime.today().timetuple()[:3])
    elif text == 'now':
        return datetime.datetime.now()
    elif text == 'yesterday':
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        return datetime.datetime(*past.timetuple()[:3])
    else:
        days = 0
        matched = re.match(
            r'^((?P<weeks>\d+) ?w(eeks?)?)? ?((?P<days>\d+) ?d(ays?)?)?$', text)
        if matched:
            groupdict = matched.groupdict()
            if groupdict['days']:
                days += int(matched.groupdict()['days'])
            if groupdict['weeks']:
                days += int(matched.groupdict()['weeks']) * 7
            past = datetime.datetime.now() - datetime.timedelta(days=days)
            return datetime.datetime(*past.timetuple()[:3])

    raise ValueError('Wrong date: "%s"' % text)
