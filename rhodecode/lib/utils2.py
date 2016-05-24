# -*- coding: utf-8 -*-

# Copyright (C) 2011-2016  RhodeCode GmbH
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
Some simple helper functions
"""


import collections
import datetime
import dateutil.relativedelta
import hashlib
import logging
import re
import sys
import time
import threading
import urllib
import urlobject
import uuid

import pygments.lexers
import sqlalchemy
import sqlalchemy.engine.url
import webob

import rhodecode


def md5(s):
    return hashlib.md5(s).hexdigest()


def md5_safe(s):
    return md5(safe_str(s))


def __get_lem():
    """
    Get language extension map based on what's inside pygments lexers
    """
    d = collections.defaultdict(lambda: [])

    def __clean(s):
        s = s.lstrip('*')
        s = s.lstrip('.')

        if s.find('[') != -1:
            exts = []
            start, stop = s.find('['), s.find(']')

            for suffix in s[start + 1:stop]:
                exts.append(s[:s.find('[')] + suffix)
            return [e.lower() for e in exts]
        else:
            return [s.lower()]

    for lx, t in sorted(pygments.lexers.LEXERS.items()):
        m = map(__clean, t[-2])
        if m:
            m = reduce(lambda x, y: x + y, m)
            for ext in m:
                desc = lx.replace('Lexer', '')
                d[ext].append(desc)

    return dict(d)


def str2bool(_str):
    """
    returs True/False value from given string, it tries to translate the
    string into boolean

    :param _str: string value to translate into boolean
    :rtype: boolean
    :returns: boolean from given string
    """
    if _str is None:
        return False
    if _str in (True, False):
        return _str
    _str = str(_str).strip().lower()
    return _str in ('t', 'true', 'y', 'yes', 'on', '1')


def aslist(obj, sep=None, strip=True):
    """
    Returns given string separated by sep as list

    :param obj:
    :param sep:
    :param strip:
    """
    if isinstance(obj, (basestring)):
        lst = obj.split(sep)
        if strip:
            lst = [v.strip() for v in lst]
        return lst
    elif isinstance(obj, (list, tuple)):
        return obj
    elif obj is None:
        return []
    else:
        return [obj]


def convert_line_endings(line, mode):
    """
    Converts a given line  "line end" accordingly to given mode

    Available modes are::
        0 - Unix
        1 - Mac
        2 - DOS

    :param line: given line to convert
    :param mode: mode to convert to
    :rtype: str
    :return: converted line according to mode
    """
    if mode == 0:
        line = line.replace('\r\n', '\n')
        line = line.replace('\r', '\n')
    elif mode == 1:
        line = line.replace('\r\n', '\r')
        line = line.replace('\n', '\r')
    elif mode == 2:
        line = re.sub('\r(?!\n)|(?<!\r)\n', '\r\n', line)
    return line


def detect_mode(line, default):
    """
    Detects line break for given line, if line break couldn't be found
    given default value is returned

    :param line: str line
    :param default: default
    :rtype: int
    :return: value of line end on of 0 - Unix, 1 - Mac, 2 - DOS
    """
    if line.endswith('\r\n'):
        return 2
    elif line.endswith('\n'):
        return 0
    elif line.endswith('\r'):
        return 1
    else:
        return default


def safe_int(val, default=None):
    """
    Returns int() of val if val is not convertable to int use default
    instead

    :param val:
    :param default:
    """

    try:
        val = int(val)
    except (ValueError, TypeError):
        val = default

    return val


def safe_unicode(str_, from_encoding=None):
    """
    safe unicode function. Does few trick to turn str_ into unicode

    In case of UnicodeDecode error, we try to return it with encoding detected
    by chardet library if it fails fallback to unicode with errors replaced

    :param str_: string to decode
    :rtype: unicode
    :returns: unicode object
    """
    if isinstance(str_, unicode):
        return str_

    if not from_encoding:
        DEFAULT_ENCODINGS = aslist(rhodecode.CONFIG.get('default_encoding',
                                                        'utf8'), sep=',')
        from_encoding = DEFAULT_ENCODINGS

    if not isinstance(from_encoding, (list, tuple)):
        from_encoding = [from_encoding]

    try:
        return unicode(str_)
    except UnicodeDecodeError:
        pass

    for enc in from_encoding:
        try:
            return unicode(str_, enc)
        except UnicodeDecodeError:
            pass

    try:
        import chardet
        encoding = chardet.detect(str_)['encoding']
        if encoding is None:
            raise Exception()
        return str_.decode(encoding)
    except (ImportError, UnicodeDecodeError, Exception):
        return unicode(str_, from_encoding[0], 'replace')


def safe_str(unicode_, to_encoding=None):
    """
    safe str function. Does few trick to turn unicode_ into string

    In case of UnicodeEncodeError, we try to return it with encoding detected
    by chardet library if it fails fallback to string with errors replaced

    :param unicode_: unicode to encode
    :rtype: str
    :returns: str object
    """

    # if it's not basestr cast to str
    if not isinstance(unicode_, basestring):
        return str(unicode_)

    if isinstance(unicode_, str):
        return unicode_

    if not to_encoding:
        DEFAULT_ENCODINGS = aslist(rhodecode.CONFIG.get('default_encoding',
                                                        'utf8'), sep=',')
        to_encoding = DEFAULT_ENCODINGS

    if not isinstance(to_encoding, (list, tuple)):
        to_encoding = [to_encoding]

    for enc in to_encoding:
        try:
            return unicode_.encode(enc)
        except UnicodeEncodeError:
            pass

    try:
        import chardet
        encoding = chardet.detect(unicode_)['encoding']
        if encoding is None:
            raise UnicodeEncodeError()

        return unicode_.encode(encoding)
    except (ImportError, UnicodeEncodeError):
        return unicode_.encode(to_encoding[0], 'replace')


def remove_suffix(s, suffix):
    if s.endswith(suffix):
        s = s[:-1 * len(suffix)]
    return s


def remove_prefix(s, prefix):
    if s.startswith(prefix):
        s = s[len(prefix):]
    return s


def find_calling_context(ignore_modules=None):
    """
    Look through the calling stack and return the frame which called
    this function and is part of core module ( ie. rhodecode.* )

    :param ignore_modules: list of modules to ignore eg. ['rhodecode.lib']
    """

    ignore_modules = ignore_modules or []

    f = sys._getframe(2)
    while f.f_back is not None:
        name = f.f_globals.get('__name__')
        if name and name.startswith(__name__.split('.')[0]):
            if name not in ignore_modules:
                return f
        f = f.f_back
    return None


def engine_from_config(configuration, prefix='sqlalchemy.', **kwargs):
    """Custom engine_from_config functions."""
    log = logging.getLogger('sqlalchemy.engine')
    engine = sqlalchemy.engine_from_config(configuration, prefix, **kwargs)

    def color_sql(sql):
        color_seq = '\033[1;33m'  # This is yellow: code 33
        normal = '\x1b[0m'
        return ''.join([color_seq, sql, normal])

    if configuration['debug']:
        # attach events only for debug configuration

        def before_cursor_execute(conn, cursor, statement,
                                  parameters, context, executemany):
            setattr(conn, 'query_start_time', time.time())
            log.info(color_sql(">>>>> STARTING QUERY >>>>>"))
            calling_context = find_calling_context(ignore_modules=[
                'rhodecode.lib.caching_query'
            ])
            if calling_context:
                log.info(color_sql('call context %s:%s' % (
                    calling_context.f_code.co_filename,
                    calling_context.f_lineno,
                )))

        def after_cursor_execute(conn, cursor, statement,
                                 parameters, context, executemany):
            delattr(conn, 'query_start_time')

        sqlalchemy.event.listen(engine, "before_cursor_execute",
                                before_cursor_execute)
        sqlalchemy.event.listen(engine, "after_cursor_execute",
                                after_cursor_execute)

    return engine


def age(prevdate, now=None, show_short_version=False, show_suffix=True,
        short_format=False):
    """
    Turns a datetime into an age string.
    If show_short_version is True, this generates a shorter string with
    an approximate age; ex. '1 day ago', rather than '1 day and 23 hours ago'.

    * IMPORTANT*
    Code of this function is written in special way so it's easier to
    backport it to javascript. If you mean to update it, please also update
    `jquery.timeago-extension.js` file

    :param prevdate: datetime object
    :param now: get current time, if not define we use
        `datetime.datetime.now()`
    :param show_short_version: if it should approximate the date and
        return a shorter string
    :param show_suffix:
    :param short_format: show short format, eg 2D instead of 2 days
    :rtype: unicode
    :returns: unicode words describing age
    """
    from pylons.i18n.translation import _, ungettext

    def _get_relative_delta(now, prevdate):
        base = dateutil.relativedelta.relativedelta(now, prevdate)
        return {
            'year': base.years,
            'month': base.months,
            'day': base.days,
            'hour': base.hours,
            'minute': base.minutes,
            'second': base.seconds,
        }

    def _is_leap_year(year):
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

    def get_month(prevdate):
        return prevdate.month

    def get_year(prevdate):
        return prevdate.year

    now = now or datetime.datetime.now()
    order = ['year', 'month', 'day', 'hour', 'minute', 'second']
    deltas = {}
    future = False

    if prevdate > now:
        now_old = now
        now = prevdate
        prevdate = now_old
        future = True
    if future:
        prevdate = prevdate.replace(microsecond=0)
    # Get date parts deltas
    for part in order:
        rel_delta = _get_relative_delta(now, prevdate)
        deltas[part] = rel_delta[part]

    # Fix negative offsets (there is 1 second between 10:59:59 and 11:00:00,
    # not 1 hour, -59 minutes and -59 seconds)
    offsets = [[5, 60], [4, 60], [3, 24]]
    for element in offsets:  # seconds, minutes, hours
        num = element[0]
        length = element[1]

        part = order[num]
        carry_part = order[num - 1]

        if deltas[part] < 0:
            deltas[part] += length
            deltas[carry_part] -= 1

    # Same thing for days except that the increment depends on the (variable)
    # number of days in the month
    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if deltas['day'] < 0:
        if get_month(prevdate) == 2 and _is_leap_year(get_year(prevdate)):
            deltas['day'] += 29
        else:
            deltas['day'] += month_lengths[get_month(prevdate) - 1]

        deltas['month'] -= 1

    if deltas['month'] < 0:
        deltas['month'] += 12
        deltas['year'] -= 1

    # Format the result
    if short_format:
        fmt_funcs = {
            'year': lambda d: u'%dy' % d,
            'month': lambda d: u'%dm' % d,
            'day': lambda d: u'%dd' % d,
            'hour': lambda d: u'%dh' % d,
            'minute': lambda d: u'%dmin' % d,
            'second': lambda d: u'%dsec' % d,
        }
    else:
        fmt_funcs = {
            'year': lambda d: ungettext(u'%d year', '%d years', d) % d,
            'month': lambda d: ungettext(u'%d month', '%d months', d) % d,
            'day': lambda d: ungettext(u'%d day', '%d days', d) % d,
            'hour': lambda d: ungettext(u'%d hour', '%d hours', d) % d,
            'minute': lambda d: ungettext(u'%d minute', '%d minutes', d) % d,
            'second': lambda d: ungettext(u'%d second', '%d seconds', d) % d,
        }

    i = 0
    for part in order:
        value = deltas[part]
        if value != 0:

            if i < 5:
                sub_part = order[i + 1]
                sub_value = deltas[sub_part]
            else:
                sub_value = 0

            if sub_value == 0 or show_short_version:
                _val = fmt_funcs[part](value)
                if future:
                    if show_suffix:
                        return _(u'in %s') % _val
                    else:
                        return _val

                else:
                    if show_suffix:
                        return _(u'%s ago') % _val
                    else:
                        return _val

            val = fmt_funcs[part](value)
            val_detail = fmt_funcs[sub_part](sub_value)

            if short_format:
                datetime_tmpl = u'%s, %s'
                if show_suffix:
                    datetime_tmpl = _(u'%s, %s ago')
                    if future:
                        datetime_tmpl = _(u'in %s, %s')
            else:
                datetime_tmpl = _(u'%s and %s')
                if show_suffix:
                    datetime_tmpl = _(u'%s and %s ago')
                    if future:
                        datetime_tmpl = _(u'in %s and %s')

            return datetime_tmpl % (val, val_detail)
        i += 1
    return _(u'just now')


def uri_filter(uri):
    """
    Removes user:password from given url string

    :param uri:
    :rtype: unicode
    :returns: filtered list of strings
    """
    if not uri:
        return ''

    proto = ''

    for pat in ('https://', 'http://'):
        if uri.startswith(pat):
            uri = uri[len(pat):]
            proto = pat
            break

    # remove passwords and username
    uri = uri[uri.find('@') + 1:]

    # get the port
    cred_pos = uri.find(':')
    if cred_pos == -1:
        host, port = uri, None
    else:
        host, port = uri[:cred_pos], uri[cred_pos + 1:]

    return filter(None, [proto, host, port])


def credentials_filter(uri):
    """
    Returns a url with removed credentials

    :param uri:
    """

    uri = uri_filter(uri)
    # check if we have port
    if len(uri) > 2 and uri[2]:
        uri[2] = ':' + uri[2]

    return ''.join(uri)


def get_clone_url(uri_tmpl, qualifed_home_url, repo_name, repo_id, **override):
    parsed_url = urlobject.URLObject(qualifed_home_url)
    decoded_path = safe_unicode(urllib.unquote(parsed_url.path.rstrip('/')))
    args = {
        'scheme': parsed_url.scheme,
        'user': '',
        # path if we use proxy-prefix
        'netloc': parsed_url.netloc+decoded_path,
        'prefix': decoded_path,
        'repo': repo_name,
        'repoid': str(repo_id)
    }
    args.update(override)
    args['user'] = urllib.quote(safe_str(args['user']))

    for k, v in args.items():
        uri_tmpl = uri_tmpl.replace('{%s}' % k, v)

    # remove leading @ sign if it's present. Case of empty user
    url_obj = urlobject.URLObject(uri_tmpl)
    url = url_obj.with_netloc(url_obj.netloc.lstrip('@'))

    return safe_unicode(url)


def get_commit_safe(repo, commit_id=None, commit_idx=None, pre_load=None):
    """
    Safe version of get_commit if this commit doesn't exists for a
    repository it returns a Dummy one instead

    :param repo: repository instance
    :param commit_id: commit id as str
    :param pre_load: optional list of commit attributes to load
    """
    # TODO(skreft): remove these circular imports
    from rhodecode.lib.vcs.backends.base import BaseRepository, EmptyCommit
    from rhodecode.lib.vcs.exceptions import RepositoryError
    if not isinstance(repo, BaseRepository):
        raise Exception('You must pass an Repository '
                        'object as first argument got %s', type(repo))

    try:
        commit = repo.get_commit(
            commit_id=commit_id, commit_idx=commit_idx, pre_load=pre_load)
    except (RepositoryError, LookupError):
        commit = EmptyCommit()
    return commit


def datetime_to_time(dt):
    if dt:
        return time.mktime(dt.timetuple())


def time_to_datetime(tm):
    if tm:
        if isinstance(tm, basestring):
            try:
                tm = float(tm)
            except ValueError:
                return
        return datetime.datetime.fromtimestamp(tm)


MENTIONS_REGEX = re.compile(
    # ^@ or @ without any special chars in front
    r'(?:^@|[^a-zA-Z0-9\-\_\.]@)'
    # main body starts with letter, then can be . - _
    r'([a-zA-Z0-9]{1}[a-zA-Z0-9\-\_\.]+)',
    re.VERBOSE | re.MULTILINE)


def extract_mentioned_users(s):
    """
    Returns unique usernames from given string s that have @mention

    :param s: string to get mentions
    """
    usrs = set()
    for username in MENTIONS_REGEX.findall(s):
        usrs.add(username)

    return sorted(list(usrs), key=lambda k: k.lower())


class AttributeDict(dict):
    def __getattr__(self, attr):
        return self.get(attr, None)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def fix_PATH(os_=None):
    """
    Get current active python path, and append it to PATH variable to fix
    issues of subprocess calls and different python versions
    """
    if os_ is None:
        import os
    else:
        os = os_

    cur_path = os.path.split(sys.executable)[0]
    if not os.environ['PATH'].startswith(cur_path):
        os.environ['PATH'] = '%s:%s' % (cur_path, os.environ['PATH'])


def obfuscate_url_pw(engine):
    _url = engine or ''
    try:
        _url = sqlalchemy.engine.url.make_url(engine)
        if _url.password:
            _url.password = 'XXXXX'
    except Exception:
        pass
    return unicode(_url)


def get_server_url(environ):
    req = webob.Request(environ)
    return req.host_url + req.script_name


def unique_id(hexlen=32):
    alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjklmnpqrstuvwxyz"
    return suuid(truncate_to=hexlen, alphabet=alphabet)


def suuid(url=None, truncate_to=22, alphabet=None):
    """
    Generate and return a short URL safe UUID.

    If the url parameter is provided, set the namespace to the provided
    URL and generate a UUID.

    :param url to get the uuid for
    :truncate_to: truncate the basic 22 UUID to shorter version

    The IDs won't be universally unique any longer, but the probability of
    a collision will still be very low.
    """
    # Define our alphabet.
    _ALPHABET = alphabet or "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"

    # If no URL is given, generate a random UUID.
    if url is None:
        unique_id = uuid.uuid4().int
    else:
        unique_id = uuid.uuid3(uuid.NAMESPACE_URL, url).int

    alphabet_length = len(_ALPHABET)
    output = []
    while unique_id > 0:
        digit = unique_id % alphabet_length
        output.append(_ALPHABET[digit])
        unique_id = int(unique_id / alphabet_length)
    return "".join(output)[:truncate_to]


def get_current_rhodecode_user():
    """
    Gets rhodecode user from threadlocal tmpl_context variable if it's
    defined, else returns None.
    """
    from pylons import tmpl_context as c
    if hasattr(c, 'rhodecode_user'):
        return c.rhodecode_user

    return None


def action_logger_generic(action, namespace=''):
    """
    A generic logger for actions useful to the system overview, tries to find
    an acting user for the context of the call otherwise reports unknown user

    :param action: logging message eg 'comment 5 deleted'
    :param type: string

    :param namespace: namespace of the logging message eg. 'repo.comments'
    :param type: string

    """

    logger_name = 'rhodecode.actions'

    if namespace:
        logger_name += '.' + namespace

    log = logging.getLogger(logger_name)

    # get a user if we can
    user = get_current_rhodecode_user()

    logfunc = log.info

    if not user:
        user = '<unknown user>'
        logfunc = log.warning

    logfunc('Logging action by {}: {}'.format(user, action))


def escape_split(text, sep=',', maxsplit=-1):
    r"""
    Allows for escaping of the separator: e.g. arg='foo\, bar'

    It should be noted that the way bash et. al. do command line parsing, those
    single quotes are required.
    """
    escaped_sep = r'\%s' % sep

    if escaped_sep not in text:
        return text.split(sep, maxsplit)

    before, _mid, after = text.partition(escaped_sep)
    startlist = before.split(sep, maxsplit)  # a regular split is fine here
    unfinished = startlist[-1]
    startlist = startlist[:-1]

    # recurse because there may be more escaped separators
    endlist = escape_split(after, sep, maxsplit)

    # finish building the escaped value. we use endlist[0] becaue the first
    # part of the string sent in recursion is the rest of the escaped value.
    unfinished += sep + endlist[0]

    return startlist + [unfinished] + endlist[1:]  # put together all the parts


class OptionalAttr(object):
    """
    Special Optional Option that defines other attribute. Example::

        def test(apiuser, userid=Optional(OAttr('apiuser')):
            user = Optional.extract(userid)
            # calls

    """

    def __init__(self, attr_name):
        self.attr_name = attr_name

    def __repr__(self):
        return '<OptionalAttr:%s>' % self.attr_name

    def __call__(self):
        return self


# alias
OAttr = OptionalAttr


class Optional(object):
    """
    Defines an optional parameter::

        param = param.getval() if isinstance(param, Optional) else param
        param = param() if isinstance(param, Optional) else param

    is equivalent of::

        param = Optional.extract(param)

    """

    def __init__(self, type_):
        self.type_ = type_

    def __repr__(self):
        return '<Optional:%s>' % self.type_.__repr__()

    def __call__(self):
        return self.getval()

    def getval(self):
        """
        returns value from this Optional instance
        """
        if isinstance(self.type_, OAttr):
            # use params name
            return self.type_.attr_name
        return self.type_

    @classmethod
    def extract(cls, val):
        """
        Extracts value from Optional() instance

        :param val:
        :return: original value if it's not Optional instance else
            value of instance
        """
        if isinstance(val, cls):
            return val.getval()
        return val
