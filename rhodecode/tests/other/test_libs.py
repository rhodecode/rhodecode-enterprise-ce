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
Package for testing various lib/helper functions in rhodecode
"""

import datetime
import string
import mock
import pytest
from rhodecode.tests.utils import run_test_concurrently
from rhodecode.lib.helpers import InitialsGravatar

from rhodecode.lib.utils2 import AttributeDict
from rhodecode.model.db import Repository


def _urls_for_proto(proto):
    return [
        ('%s://127.0.0.1' % proto, ['%s://' % proto, '127.0.0.1'],
         '%s://127.0.0.1' % proto),
        ('%s://marcink@127.0.0.1' % proto, ['%s://' % proto, '127.0.0.1'],
         '%s://127.0.0.1' % proto),
        ('%s://marcink:pass@127.0.0.1' % proto, ['%s://' % proto, '127.0.0.1'],
         '%s://127.0.0.1' % proto),
        ('%s://127.0.0.1:8080' % proto, ['%s://' % proto, '127.0.0.1', '8080'],
         '%s://127.0.0.1:8080' % proto),
        ('%s://domain.org' % proto, ['%s://' % proto, 'domain.org'],
         '%s://domain.org' % proto),
        ('%s://user:pass@domain.org:8080' % proto,
         ['%s://' % proto, 'domain.org', '8080'],
         '%s://domain.org:8080' % proto),
    ]

TEST_URLS = _urls_for_proto('http') + _urls_for_proto('https')


@pytest.mark.parametrize("test_url, expected, expected_creds", TEST_URLS)
def test_uri_filter(test_url, expected, expected_creds):
    from rhodecode.lib.utils2 import uri_filter
    assert uri_filter(test_url) == expected


@pytest.mark.parametrize("test_url, expected, expected_creds", TEST_URLS)
def test_credentials_filter(test_url, expected, expected_creds):
    from rhodecode.lib.utils2 import credentials_filter
    assert credentials_filter(test_url) == expected_creds


@pytest.mark.parametrize("str_bool, expected", [
    ('t', True),
    ('true', True),
    ('y', True),
    ('yes', True),
    ('on', True),
    ('1', True),
    ('Y', True),
    ('yeS', True),
    ('Y', True),
    ('TRUE', True),
    ('T', True),
    ('False', False),
    ('F', False),
    ('FALSE', False),
    ('0', False),
    ('-1', False),
    ('', False)
])
def test_str2bool(str_bool, expected):
    from rhodecode.lib.utils2 import str2bool
    assert str2bool(str_bool) == expected


@pytest.mark.parametrize("text, expected", reduce(lambda a1,a2:a1+a2, [
[
(pref+"", []),
(pref+"Hi there @marcink", ['marcink']),
(pref+"Hi there @marcink and @bob", ['bob', 'marcink']),
(pref+"Hi there @marcink\n", ['marcink']),
(pref+"Hi there @marcink and @bob\n", ['bob', 'marcink']),
(pref+"Hi there marcin@rhodecode.com", []),
(pref+"Hi there @john.malcovic and @bob\n", ['bob', 'john.malcovic']),
(pref+"This needs to be reviewed: (@marcink,@john)", ["john", "marcink"]),
(pref+"This needs to be reviewed: (@marcink, @john)", ["john", "marcink"]),
(pref+"This needs to be reviewed: [@marcink,@john]", ["john", "marcink"]),
(pref+"This needs to be reviewed: (@marcink @john)", ["john", "marcink"]),
(pref+"@john @mary, please review", ["john", "mary"]),
(pref+"@john,@mary, please review", ["john", "mary"]),
(pref+"Hej @123, @22john,@mary, please review", ['123', '22john', 'mary']),
(pref+"@first hi there @marcink here's my email marcin@email.com "
 "@lukaszb check @one_more22 it pls @ ttwelve @D[] @one@two@three ", ['first', 'lukaszb', 'marcink', 'one', 'one_more22']),
(pref+"@MARCIN    @maRCiN @2one_more22 @john please see this http://org.pl", ['2one_more22', 'john', 'MARCIN', 'maRCiN']),
(pref+"@marian.user just do it @marco-polo and next extract @marco_polo", ['marco-polo', 'marco_polo', 'marian.user']),
(pref+"user.dot  hej ! not-needed maril@domain.org", []),
(pref+"\n@marcin", ['marcin']),
]
for pref in ['', '\n', 'hi !', '\t', '\n\n']]))
def test_mention_extractor(text, expected):
    from rhodecode.lib.utils2 import extract_mentioned_users
    got = extract_mentioned_users(text)
    assert sorted(got, key=lambda x: x.lower()) == got
    assert set(expected) == set(got)

@pytest.mark.parametrize("age_args, expected, kw", [
    ({}, u'just now', {}),
    ({'seconds': -1}, u'1 second ago', {}),
    ({'seconds': -60 * 2}, u'2 minutes ago', {}),
    ({'hours': -1}, u'1 hour ago', {}),
    ({'hours': -24}, u'1 day ago', {}),
    ({'hours': -24 * 5}, u'5 days ago', {}),
    ({'months': -1}, u'1 month ago', {}),
    ({'months': -1, 'days': -2}, u'1 month and 2 days ago', {}),
    ({'years': -1, 'months': -1}, u'1 year and 1 month ago', {}),
    ({}, u'just now', {'short_format': True}),
    ({'seconds': -1}, u'1sec ago', {'short_format': True}),
    ({'seconds': -60 * 2}, u'2min ago', {'short_format': True}),
    ({'hours': -1}, u'1h ago', {'short_format': True}),
    ({'hours': -24}, u'1d ago', {'short_format': True}),
    ({'hours': -24 * 5}, u'5d ago', {'short_format': True}),
    ({'months': -1}, u'1m ago', {'short_format': True}),
    ({'months': -1, 'days': -2}, u'1m, 2d ago', {'short_format': True}),
    ({'years': -1, 'months': -1}, u'1y, 1m ago', {'short_format': True}),
])
def test_age(age_args, expected, kw, pylonsapp):
    from rhodecode.lib.utils2 import age
    from dateutil import relativedelta
    n = datetime.datetime(year=2012, month=5, day=17)
    delt = lambda *args, **kwargs: relativedelta.relativedelta(*args, **kwargs)
    assert age(n + delt(**age_args), now=n, **kw) == expected

@pytest.mark.parametrize("age_args, expected, kw", [
    ({}, u'just now', {}),
    ({'seconds': 1}, u'in 1 second', {}),
    ({'seconds': 60 * 2}, u'in 2 minutes', {}),
    ({'hours': 1}, u'in 1 hour', {}),
    ({'hours': 24}, u'in 1 day', {}),
    ({'hours': 24 * 5}, u'in 5 days', {}),
    ({'months': 1}, u'in 1 month', {}),
    ({'months': 1, 'days': 1}, u'in 1 month and 1 day', {}),
    ({'years': 1, 'months': 1}, u'in 1 year and 1 month', {}),
    ({}, u'just now', {'short_format': True}),
    ({'seconds': 1}, u'in 1sec', {'short_format': True}),
    ({'seconds': 60 * 2}, u'in 2min', {'short_format': True}),
    ({'hours': 1}, u'in 1h', {'short_format': True}),
    ({'hours': 24}, u'in 1d', {'short_format': True}),
    ({'hours': 24 * 5}, u'in 5d', {'short_format': True}),
    ({'months': 1}, u'in 1m', {'short_format': True}),
    ({'months': 1, 'days': 1}, u'in 1m, 1d', {'short_format': True}),
    ({'years': 1, 'months': 1}, u'in 1y, 1m', {'short_format': True}),
])
def test_age_in_future(age_args, expected, kw, pylonsapp):
    from rhodecode.lib.utils2 import age
    from dateutil import relativedelta
    n = datetime.datetime(year=2012, month=5, day=17)
    delt = lambda *args, **kwargs: relativedelta.relativedelta(*args, **kwargs)
    assert age(n + delt(**age_args), now=n, **kw) == expected


def test_tag_exctrator():
    sample = (
        "hello pta[tag] gog [[]] [[] sda ero[or]d [me =>>< sa]"
        "[requires] [stale] [see<>=>] [see => http://url.com]"
        "[requires => url] [lang => python] [just a tag] <html_tag first='abc' attr=\"my.url?attr=&another=\"></html_tag>"
        "[,d] [ => ULR ] [obsolete] [desc]]"
    )
    from rhodecode.lib.helpers import desc_stylize, escaped_stylize
    res = desc_stylize(sample)
    assert '<div class="metatag" tag="tag">tag</div>' in res
    assert '<div class="metatag" tag="obsolete">obsolete</div>' in res
    assert '<div class="metatag" tag="stale">stale</div>' in res
    assert '<div class="metatag" tag="lang">python</div>' in res
    assert '<div class="metatag" tag="requires">requires =&gt; <a href="/url">url</a></div>' in res
    assert '<div class="metatag" tag="tag">tag</div>' in res
    assert '<html_tag first=\'abc\' attr=\"my.url?attr=&another=\"></html_tag>' in res

    res_encoded = escaped_stylize(sample)
    assert '<div class="metatag" tag="tag">tag</div>' in res_encoded
    assert '<div class="metatag" tag="obsolete">obsolete</div>' in res_encoded
    assert '<div class="metatag" tag="stale">stale</div>' in res_encoded
    assert '<div class="metatag" tag="lang">python</div>' in res_encoded
    assert '<div class="metatag" tag="requires">requires =&gt; <a href="/url">url</a></div>' in res_encoded
    assert '<div class="metatag" tag="tag">tag</div>' in res_encoded
    assert '&lt;html_tag first=&#39;abc&#39; attr=&#34;my.url?attr=&amp;another=&#34;&gt;&lt;/html_tag&gt;' in res_encoded


@pytest.mark.parametrize("tmpl_url, email, expected", [
    ('http://test.com/{email}', 'test@foo.com', 'http://test.com/test@foo.com'),

    ('http://test.com/{md5email}', 'test@foo.com', 'http://test.com/3cb7232fcc48743000cb86d0d5022bd9'),
    ('http://test.com/{md5email}', 'testąć@foo.com', 'http://test.com/978debb907a3c55cd741872ab293ef30'),

    ('http://testX.com/{md5email}?s={size}', 'test@foo.com', 'http://testX.com/3cb7232fcc48743000cb86d0d5022bd9?s=24'),
    ('http://testX.com/{md5email}?s={size}', 'testąć@foo.com', 'http://testX.com/978debb907a3c55cd741872ab293ef30?s=24'),

    ('{scheme}://{netloc}/{md5email}/{size}', 'test@foo.com', 'https://server.com/3cb7232fcc48743000cb86d0d5022bd9/24'),
    ('{scheme}://{netloc}/{md5email}/{size}', 'testąć@foo.com', 'https://server.com/978debb907a3c55cd741872ab293ef30/24'),

    ('http://test.com/{email}', 'testąć@foo.com', 'http://test.com/testąć@foo.com'),
    ('http://test.com/{email}?size={size}', 'test@foo.com', 'http://test.com/test@foo.com?size=24'),
    ('http://test.com/{email}?size={size}', 'testąć@foo.com', 'http://test.com/testąć@foo.com?size=24'),
])
def test_gravatar_url_builder(tmpl_url, email, expected, request_stub):
    from rhodecode.lib.helpers import gravatar_url

    # mock pyramid.threadlocals
    def fake_get_current_request():
        request_stub.scheme = 'https'
        request_stub.host = 'server.com'
        return request_stub

    # mock pylons.tmpl_context
    def fake_tmpl_context(_url):
        _c = AttributeDict()
        _c.visual = AttributeDict()
        _c.visual.use_gravatar = True
        _c.visual.gravatar_url = _url

        return _c

    with mock.patch('rhodecode.lib.helpers.get_current_request',
                    fake_get_current_request):
        fake = fake_tmpl_context(_url=tmpl_url)
        with mock.patch('pylons.tmpl_context', fake):
            grav = gravatar_url(email_address=email, size=24)
            assert grav == expected


@pytest.mark.parametrize(
    "email, first_name, last_name, expected_initials, expected_color", [

        ('test@rhodecode.com', '', '', 'TR', '#8a994d'),
        ('marcin.kuzminski@rhodecode.com', '', '', 'MK', '#6559b3'),
        # special cases of email
        ('john.van.dam@rhodecode.com', '', '', 'JD', '#526600'),
        ('Guido.van.Rossum@rhodecode.com', '', '', 'GR', '#990052'),
        ('Guido.van.Rossum@rhodecode.com', 'Guido', 'Van Rossum', 'GR', '#990052'),

        ('rhodecode+Guido.van.Rossum@rhodecode.com', '', '', 'RR', '#46598c'),
        ('pclouds@rhodecode.com', 'Nguyễn Thái', 'Tgọc Duy', 'ND', '#665200'),

        ('john-brown@foo.com', '', '', 'JF', '#73006b'),
        ('admin@rhodecode.com', 'Marcin', 'Kuzminski', 'MK', '#104036'),
        # partials
        ('admin@rhodecode.com', 'Marcin', '', 'MR', '#104036'),  # fn+email
        ('admin@rhodecode.com', '', 'Kuzminski', 'AK', '#104036'),  # em+ln
        # non-ascii
        ('admin@rhodecode.com', 'Marcin', 'Śuzminski', 'MS', '#104036'),
        ('marcin.śuzminski@rhodecode.com', '', '', 'MS', '#73000f'),

        # special cases, LDAP can provide those...
        ('admin@', 'Marcin', 'Śuzminski', 'MS', '#aa00ff'),
        ('marcin.śuzminski', '', '', 'MS', '#402020'),
        ('null', '', '', 'NL', '#8c4646'),
])
def test_initials_gravatar_pick_of_initials_and_color_algo(
        email, first_name, last_name, expected_initials, expected_color):
    instance = InitialsGravatar(email, first_name, last_name)
    assert instance.get_initials() == expected_initials
    assert instance.str2color(email) == expected_color


def test_initials_gravatar_mapping_algo():
    pos = set()
    instance = InitialsGravatar('', '', '')
    iterations = 0

    variations = []
    for letter1 in string.ascii_letters:
        for letter2 in string.ascii_letters[::-1][:10]:
            for letter3 in string.ascii_letters[:10]:
                variations.append(
                    '%s@rhodecode.com' % (letter1+letter2+letter3))

    max_variations = 4096
    for email in variations[:max_variations]:
        iterations += 1
        pos.add(
            instance.pick_color_bank_index(email,
                                           instance.get_color_bank()))

    # we assume that we have match all 256 possible positions,
    # in reasonable amount of different email addresses
    assert len(pos) == 256
    assert iterations == max_variations


@pytest.mark.parametrize("tmpl, repo_name, overrides, prefix, expected", [
    (Repository.DEFAULT_CLONE_URI, 'group/repo1', {}, '', 'http://vps1:8000/group/repo1'),
    (Repository.DEFAULT_CLONE_URI, 'group/repo1', {'user': 'marcink'}, '', 'http://marcink@vps1:8000/group/repo1'),
    (Repository.DEFAULT_CLONE_URI, 'group/repo1', {}, '/rc', 'http://vps1:8000/rc/group/repo1'),
    (Repository.DEFAULT_CLONE_URI, 'group/repo1', {'user': 'user'}, '/rc', 'http://user@vps1:8000/rc/group/repo1'),
    (Repository.DEFAULT_CLONE_URI, 'group/repo1', {'user': 'marcink'}, '/rc', 'http://marcink@vps1:8000/rc/group/repo1'),
    (Repository.DEFAULT_CLONE_URI, 'group/repo1', {'user': 'user'}, '/rc/', 'http://user@vps1:8000/rc/group/repo1'),
    (Repository.DEFAULT_CLONE_URI, 'group/repo1', {'user': 'marcink'}, '/rc/', 'http://marcink@vps1:8000/rc/group/repo1'),
    ('{scheme}://{user}@{netloc}/_{repoid}', 'group/repo1', {}, '', 'http://vps1:8000/_23'),
    ('{scheme}://{user}@{netloc}/_{repoid}', 'group/repo1', {'user': 'marcink'}, '', 'http://marcink@vps1:8000/_23'),
    ('http://{user}@{netloc}/_{repoid}', 'group/repo1', {'user': 'marcink'}, '', 'http://marcink@vps1:8000/_23'),
    ('http://{netloc}/_{repoid}', 'group/repo1', {'user': 'marcink'}, '', 'http://vps1:8000/_23'),
    ('https://{user}@proxy1.server.com/{repo}', 'group/repo1', {'user': 'marcink'}, '', 'https://marcink@proxy1.server.com/group/repo1'),
    ('https://{user}@proxy1.server.com/{repo}', 'group/repo1', {}, '', 'https://proxy1.server.com/group/repo1'),
    ('https://proxy1.server.com/{user}/{repo}', 'group/repo1', {'user': 'marcink'}, '', 'https://proxy1.server.com/marcink/group/repo1'),
])
def test_clone_url_generator(tmpl, repo_name, overrides, prefix, expected):
    from rhodecode.lib.utils2 import get_clone_url
    clone_url = get_clone_url(uri_tmpl=tmpl, qualifed_home_url='http://vps1:8000'+prefix,
                              repo_name=repo_name, repo_id=23, **overrides)
    assert clone_url == expected


def _quick_url(text, tmpl="""<a class="revision-link" href="%s">%s</a>""", url_=None):
    """
    Changes `some text url[foo]` => `some text <a href="/">foo</a>

    :param text:
    """
    import re
    # quickly change expected url[] into a link
    URL_PAT = re.compile(r'(?:url\[)(.+?)(?:\])')

    def url_func(match_obj):
        _url = match_obj.groups()[0]
        return tmpl % (url_ or '/some-url', _url)
    return URL_PAT.sub(url_func, text)


@pytest.mark.parametrize("sample, expected", [
  ("",
   ""),
  ("git-svn-id: https://svn.apache.org/repos/asf/libcloud/trunk@1441655 13f79535-47bb-0310-9956-ffa450edef68",
   "git-svn-id: https://svn.apache.org/repos/asf/libcloud/trunk@1441655 13f79535-47bb-0310-9956-ffa450edef68"),
  ("from rev 000000000000",
   "from rev url[000000000000]"),
  ("from rev 000000000000123123 also rev 000000000000",
   "from rev url[000000000000123123] also rev url[000000000000]"),
  ("this should-000 00",
   "this should-000 00"),
  ("longtextffffffffff rev 123123123123",
   "longtextffffffffff rev url[123123123123]"),
  ("rev ffffffffffffffffffffffffffffffffffffffffffffffffff",
   "rev ffffffffffffffffffffffffffffffffffffffffffffffffff"),
  ("ffffffffffff some text traalaa",
   "url[ffffffffffff] some text traalaa"),
   ("""Multi line
   123123123123
   some text 123123123123
   sometimes !
   """,
   """Multi line
   url[123123123123]
   some text url[123123123123]
   sometimes !
   """)
])
def test_urlify_commits(sample, expected):
    def fake_url(self, *args, **kwargs):
        return '/some-url'

    expected = _quick_url(expected)

    with mock.patch('pylons.url', fake_url):
        from rhodecode.lib.helpers import urlify_commits
        assert urlify_commits(sample, 'repo_name') == expected


@pytest.mark.parametrize("sample, expected, url_", [
    ("",
     "",
     ""),
    ("https://svn.apache.org/repos",
     "url[https://svn.apache.org/repos]",
     "https://svn.apache.org/repos"),
    ("http://svn.apache.org/repos",
     "url[http://svn.apache.org/repos]",
     "http://svn.apache.org/repos"),
    ("from rev a also rev http://google.com",
     "from rev a also rev url[http://google.com]",
     "http://google.com"),
    ("""Multi line
     https://foo.bar.com
     some text lalala""",
     """Multi line
     url[https://foo.bar.com]
     some text lalala""",
     "https://foo.bar.com")
])
def test_urlify_test(sample, expected, url_):
    from rhodecode.lib.helpers import urlify_text
    expected = _quick_url(expected, tmpl="""<a href="%s">%s</a>""", url_=url_)
    assert urlify_text(sample) == expected


@pytest.mark.parametrize("test, expected", [
  ("", None),
  ("/_2", '2'),
  ("_2", '2'),
  ("/_2/", '2'),
  ("_2/", '2'),

  ("/_21", '21'),
  ("_21", '21'),
  ("/_21/", '21'),
  ("_21/", '21'),

  ("/_21/foobar", '21'),
  ("_21/121", '21'),
  ("/_21/_12", '21'),
  ("_21/rc/foo", '21'),

])
def test_get_repo_by_id(test, expected):
    from rhodecode.model.repo import RepoModel
    _test = RepoModel()._extract_id_from_repo_name(test)
    assert _test == expected


@pytest.mark.parametrize("test_repo_name, repo_type", [
  ("test_repo_1", None),
  ("repo_group/foobar", None),
  ("test_non_asci_ąćę", None),
  (u"test_non_asci_unicode_ąćę", None),
])
def test_invalidation_context(pylonsapp, test_repo_name, repo_type):
    from beaker.cache import cache_region
    from rhodecode.lib import caches
    from rhodecode.model.db import CacheKey

    @cache_region('long_term')
    def _dummy_func(cache_key):
        return 'result'

    invalidator_context = CacheKey.repo_context_cache(
        _dummy_func, test_repo_name, 'repo')

    with invalidator_context as context:
        invalidated = context.invalidate()
        result = context.compute()

    assert invalidated == True
    assert 'result' == result
    assert isinstance(context, caches.FreshRegionCache)

    assert 'InvalidationContext' in repr(invalidator_context)

    with invalidator_context as context:
        context.invalidate()
        result = context.compute()

    assert 'result' == result
    assert isinstance(context, caches.ActiveRegionCache)


def test_invalidation_context_exception_in_compute(pylonsapp):
    from rhodecode.model.db import CacheKey
    from beaker.cache import cache_region

    @cache_region('long_term')
    def _dummy_func(cache_key):
        # this causes error since it doesn't get any params
        raise Exception('ups')

    invalidator_context = CacheKey.repo_context_cache(
        _dummy_func, 'test_repo_2', 'repo')

    with pytest.raises(Exception):
        with invalidator_context as context:
            context.invalidate()
            context.compute()


@pytest.mark.parametrize('execution_number', range(5))
def test_cache_invalidation_race_condition(execution_number, pylonsapp):
    import time
    from beaker.cache import cache_region
    from rhodecode.model.db import CacheKey

    if CacheKey.metadata.bind.url.get_backend_name() == "mysql":
        reason = (
            'Fails on MariaDB due to some locking issues. Investigation'
            ' needed')
        pytest.xfail(reason=reason)

    @run_test_concurrently(25)
    def test_create_and_delete_cache_keys():
        time.sleep(0.2)

        @cache_region('long_term')
        def _dummy_func(cache_key):
            return 'result'

        invalidator_context = CacheKey.repo_context_cache(
            _dummy_func, 'test_repo_1', 'repo')

        with invalidator_context as context:
            context.invalidate()
            context.compute()

        CacheKey.set_invalidate('test_repo_1', delete=True)

    test_create_and_delete_cache_keys()
