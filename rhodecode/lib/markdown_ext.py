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

import re

import markdown


class FlavoredCheckboxExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('checklist',
                             FlavoredCheckboxPreprocessor(md), '<reference')
        md.postprocessors.add('checklist',
                              FlavoredCheckboxPostprocessor(md), '>unescape')


class FlavoredCheckboxPreprocessor(markdown.preprocessors.Preprocessor):
    """
    Replaces occurrences of [ ] or [x] to checkbox input
    """

    pattern = re.compile(r'^([*-]) \[([ x])\]')

    def run(self, lines):
        return [self._transform_line(line) for line in lines]

    def _transform_line(self, line):
        return self.pattern.sub(self._replacer, line)

    def _replacer(self, match):
        list_prefix, state = match.groups()
        checked = '' if state == ' ' else ' checked="checked"'
        return '%s <input type="checkbox" disabled="disabled"%s>' % (list_prefix,
                                                                   checked)


class FlavoredCheckboxPostprocessor(markdown.postprocessors.Postprocessor):
    """
    Adds `flavored_checkbox_list` class to list of checkboxes
    """

    pattern = re.compile(r'^([*-]) \[([ x])\]')

    def run(self, html):
        before = '<ul>\n<li><input type="checkbox"'
        after = '<ul class="flavored_checkbox_list">\n<li><input type="checkbox"'
        return html.replace(before, after)




# Global Vars
URLIZE_RE = '(%s)' % '|'.join([
    r'<(?:f|ht)tps?://[^>]*>',
    r'\b(?:f|ht)tps?://[^)<>\s]+[^.,)<>\s]',
    r'\bwww\.[^)<>\s]+[^.,)<>\s]',
    r'[^(<\s]+\.(?:com|net|org)\b',
])

class UrlizePattern(markdown.inlinepatterns.Pattern):
    """ Return a link Element given an autolink (`http://example/com`). """
    def handleMatch(self, m):
        url = m.group(2)

        if url.startswith('<'):
            url = url[1:-1]

        text = url

        if not url.split('://')[0] in ('http','https','ftp'):
            if '@' in url and not '/' in url:
                url = 'mailto:' + url
            else:
                url = 'http://' + url

        el = markdown.util.etree.Element("a")
        el.set('href', url)
        el.text = markdown.util.AtomicString(text)
        return el


class UrlizeExtension(markdown.Extension):
    """ Urlize Extension for Python-Markdown. """

    def extendMarkdown(self, md, md_globals):
        """ Replace autolink with UrlizePattern """
        md.inlinePatterns['autolink'] = UrlizePattern(URLIZE_RE, md)
