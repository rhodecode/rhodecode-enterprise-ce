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

import copy
import mock
import pytest

from pylons.util import ContextObj

from rhodecode.lib import helpers
from rhodecode.lib.utils2 import AttributeDict
from rhodecode.model.settings import IssueTrackerSettingsModel


@pytest.mark.parametrize('url, expected_url', [
    ('http://rc.rc/test', '<a href="http://rc.rc/test">http://rc.rc/test</a>'),
    ('http://rc.rc/@foo', '<a href="http://rc.rc/@foo">http://rc.rc/@foo</a>'),
    ('http://rc.rc/!foo', '<a href="http://rc.rc/!foo">http://rc.rc/!foo</a>'),
    ('http://rc.rc/&foo', '<a href="http://rc.rc/&foo">http://rc.rc/&foo</a>'),
    ('http://rc.rc/#foo', '<a href="http://rc.rc/#foo">http://rc.rc/#foo</a>'),
])
def test_urlify_text(url, expected_url):
    assert helpers.urlify_text(url) == expected_url


@pytest.mark.parametrize('repo_name, commit_id, path, expected_result', [
    ('rX<X', 'cX<X', 'pX<X/aX<X/bX<X',
     '<a class="pjax-link" href="/rX%3CX/files/cX%3CX/">rX&lt;X</a>/'
     '<a class="pjax-link" href="/rX%3CX/files/cX%3CX/pX%3CX">pX&lt;X</a>/'
     '<a class="pjax-link" href="/rX%3CX/files/cX%3CX/pX%3CX/aX%3CX">aX&lt;X'
     '</a>/bX&lt;X'),
    # Path with only one segment
    ('rX<X', 'cX<X', 'pX<X',
     '<a class="pjax-link" href="/rX%3CX/files/cX%3CX/">rX&lt;X</a>/pX&lt;X'),
    # Empty path
    ('rX<X', 'cX<X', '', 'rX&lt;X'),
    ('rX"X', 'cX"X', 'pX"X/aX"X/bX"X',
     '<a class="pjax-link" href="/rX%22X/files/cX%22X/">rX&#34;X</a>/'
     '<a class="pjax-link" href="/rX%22X/files/cX%22X/pX%22X">pX&#34;X</a>/'
     '<a class="pjax-link" href="/rX%22X/files/cX%22X/pX%22X/aX%22X">aX&#34;X'
     '</a>/bX&#34;X'),
], ids=['simple', 'one_segment', 'empty_path', 'simple_quote'])
def test_files_breadcrumbs_xss(
        repo_name, commit_id, path, pylonsapp, expected_result):
    result = helpers.files_breadcrumbs(repo_name, commit_id, path)
    # Expect it to encode all path fragments properly. This is important
    # because it returns an instance of `literal`.
    assert result == expected_result


def test_format_binary():
    assert helpers.format_byte_size_binary(298489462784) == '278.0 GiB'


@pytest.mark.parametrize('text_string, pattern, expected_text', [
    ('Fix #42', '(?:#)(?P<issue_id>\d+)',
     'Fix <a class="issue-tracker-link" href="http://r.io/{repo}/i/42">#42</a>'
     ),
    ('Fix #42', '(?:#)?<issue_id>\d+)', 'Fix #42'),  # Broken regex
])
def test_process_patterns_repo(backend, text_string, pattern, expected_text):
    repo = backend.create_repo()
    config = {'123': {
        'uid': '123',
        'pat': pattern,
        'url': 'http://r.io/${repo}/i/${issue_id}',
        'pref': '#',
        }
    }
    with mock.patch.object(IssueTrackerSettingsModel,
                           'get_settings', lambda s: config):
        processed_text = helpers.process_patterns(
            text_string, repo.repo_name, config)

    assert processed_text == expected_text.format(repo=repo.repo_name)


@pytest.mark.parametrize('text_string, pattern, expected_text', [
    ('Fix #42', '(?:#)(?P<issue_id>\d+)',
     'Fix <a class="issue-tracker-link" href="http://r.io/i/42">#42</a>'
     ),
    ('Fix #42', '(?:#)?<issue_id>\d+)', 'Fix #42'),  # Broken regex
])
def test_process_patterns_no_repo(text_string, pattern, expected_text):
    config = {'123': {
        'uid': '123',
        'pat': pattern,
        'url': 'http://r.io/i/${issue_id}',
        'pref': '#',
        }
    }
    with mock.patch.object(IssueTrackerSettingsModel,
                           'get_global_settings', lambda s, cache: config):
        processed_text = helpers.process_patterns(
            text_string, '', config)

    assert processed_text == expected_text


def test_process_patterns_non_existent_repo_name(backend):
    text_string = 'Fix #42'
    pattern = '(?:#)(?P<issue_id>\d+)'
    expected_text = ('Fix <a class="issue-tracker-link" '
                     'href="http://r.io/do-not-exist/i/42">#42</a>')
    config = {'123': {
        'uid': '123',
        'pat': pattern,
        'url': 'http://r.io/${repo}/i/${issue_id}',
        'pref': '#',
        }
    }
    with mock.patch.object(IssueTrackerSettingsModel,
                           'get_global_settings', lambda s, cache: config):
        processed_text = helpers.process_patterns(
            text_string, 'do-not-exist', config)

    assert processed_text == expected_text


def test_get_visual_attr(pylonsapp):
    c = ContextObj()
    assert None is helpers.get_visual_attr(c, 'fakse')

    # emulate the c.visual behaviour
    c.visual = AttributeDict({})
    assert None is helpers.get_visual_attr(c, 'some_var')

    c.visual.some_var = 'foobar'
    assert 'foobar' == helpers.get_visual_attr(c, 'some_var')


@pytest.mark.parametrize('test_text, inclusive, expected_text', [
    ('just a string', False, 'just a string'),
    ('just a string\n', False, 'just a string'),
    ('just a string\n next line', False, 'just a string...'),
    ('just a string\n next line', True, 'just a string\n...'),
])
def test_chop_at(test_text, inclusive, expected_text):
    assert helpers.chop_at_smart(
        test_text, '\n', inclusive, '...') == expected_text


@pytest.mark.parametrize('test_text, expected_output', [
    ('some text', ['some', 'text']),
    ('some    text', ['some', 'text']),
    ('some text "with  a phrase"', ['some', 'text', 'with  a phrase']),
    ('"a phrase" "another phrase"', ['a phrase', 'another phrase']),
    ('"justphrase"', ['justphrase']),
    ('""', []),
    ('', []),
    ('  ', []),
    ('"   "', []),
])
def test_extract_phrases(test_text, expected_output):
    assert helpers.extract_phrases(test_text) == expected_output


@pytest.mark.parametrize('test_text, text_phrases, expected_output', [
    ('some text here', ['some', 'here'], [(0, 4), (10, 14)]),
    ('here here there', ['here'], [(0, 4), (5, 9), (11, 15)]),
    ('irrelevant', ['not found'], []),
    ('irrelevant', ['not found'], []),
])
def test_get_matching_offsets(test_text, text_phrases, expected_output):
    assert helpers.get_matching_offsets(
        test_text, text_phrases) == expected_output

def test_normalize_text_for_matching():
    assert helpers.normalize_text_for_matching(
        'OJjfe)*#$*@)$JF*)3r2f80h') == 'ojjfe        jf  3r2f80h'

def test_get_matching_line_offsets():
    assert helpers.get_matching_line_offsets([
        'words words words',
        'words words words',
        'some text some',
        'words words words',
        'words words words',
        'text here what'], 'text') == {3: [(5, 9)], 6: [(0, 4)]}