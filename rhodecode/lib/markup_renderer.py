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
Renderer for markup languages with ability to parse using rst or markdown
"""


import re
import os
import logging
from mako.lookup import TemplateLookup

from docutils.core import publish_parts
from docutils.parsers.rst import directives
import markdown

from rhodecode.lib.markdown_ext import (
    UrlizeExtension, GithubFlavoredMarkdownExtension)
from rhodecode.lib.utils2 import safe_unicode, md5_safe, MENTIONS_REGEX

log = logging.getLogger(__name__)

# default renderer used to generate automated comments
DEFAULT_COMMENTS_RENDERER = 'rst'


class MarkupRenderer(object):
    RESTRUCTUREDTEXT_DISALLOWED_DIRECTIVES = ['include', 'meta', 'raw']

    MARKDOWN_PAT = re.compile(r'\.(md|mkdn?|mdown|markdown)$', re.IGNORECASE)
    RST_PAT = re.compile(r'\.re?st$', re.IGNORECASE)
    PLAIN_PAT = re.compile(r'^readme$', re.IGNORECASE)

    def _detect_renderer(self, source, filename=None):
        """
        runs detection of what renderer should be used for generating html
        from a markup language

        filename can be also explicitly a renderer name

        :param source:
        :param filename:
        """

        if MarkupRenderer.MARKDOWN_PAT.findall(filename):
            detected_renderer = 'markdown'
        elif MarkupRenderer.RST_PAT.findall(filename):
            detected_renderer = 'rst'
        elif MarkupRenderer.PLAIN_PAT.findall(filename):
            detected_renderer = 'rst'
        else:
            detected_renderer = 'plain'

        return getattr(MarkupRenderer, detected_renderer)

    def render(self, source, filename=None):
        """
        Renders a given filename using detected renderer
        it detects renderers based on file extension or mimetype.
        At last it will just do a simple html replacing new lines with <br/>

        :param file_name:
        :param source:
        """

        renderer = self._detect_renderer(source, filename)
        readme_data = renderer(source)
        return readme_data

    @classmethod
    def _flavored_markdown(cls, text):
        """
        Github style flavored markdown

        :param text:
        """

        # Extract pre blocks.
        extractions = {}

        def pre_extraction_callback(matchobj):
            digest = md5_safe(matchobj.group(0))
            extractions[digest] = matchobj.group(0)
            return "{gfm-extraction-%s}" % digest
        pattern = re.compile(r'<pre>.*?</pre>', re.MULTILINE | re.DOTALL)
        text = re.sub(pattern, pre_extraction_callback, text)

        # Prevent foo_bar_baz from ending up with an italic word in the middle.
        def italic_callback(matchobj):
            s = matchobj.group(0)
            if list(s).count('_') >= 2:
                return s.replace('_', r'\_')
            return s
        text = re.sub(r'^(?! {4}|\t)\w+_\w+_\w[\w_]*', italic_callback, text)

        # Insert pre block extractions.
        def pre_insert_callback(matchobj):
            return '\n\n' + extractions[matchobj.group(1)]
        text = re.sub(r'\{gfm-extraction-([0-9a-f]{32})\}',
                      pre_insert_callback, text)

        return text

    @classmethod
    def urlify_text(cls, text):
        url_pat = re.compile(r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]'
                             r'|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)')

        def url_func(match_obj):
            url_full = match_obj.groups()[0]
            return '<a href="%(url)s">%(url)s</a>' % ({'url': url_full})

        return url_pat.sub(url_func, text)

    @classmethod
    def plain(cls, source, universal_newline=True):
        source = safe_unicode(source)
        if universal_newline:
            newline = '\n'
            source = newline.join(source.splitlines())

        source = cls.urlify_text(source)
        return '<br />' + source.replace("\n", '<br />')

    @classmethod
    def markdown(cls, source, safe=True, flavored=True, mentions=False):
        # It does not allow to insert inline HTML. In presence of HTML tags, it
        # will replace them instead with [HTML_REMOVED]. This is controlled by
        # the safe_mode=True parameter of the markdown method.
        extensions = ['codehilite', 'extra', 'def_list', 'sane_lists']
        if flavored:
            extensions.append(GithubFlavoredMarkdownExtension())

        if mentions:
            mention_pat = re.compile(MENTIONS_REGEX)

            def wrapp(match_obj):
                uname = match_obj.groups()[0]
                return ' **@%(uname)s** ' % {'uname': uname}
            mention_hl = mention_pat.sub(wrapp, source).strip()
            # we extracted mentions render with this using Mentions false
            return cls.markdown(mention_hl, safe=safe, flavored=flavored,
                                mentions=False)

        source = safe_unicode(source)
        try:
            if flavored:
                source = cls._flavored_markdown(source)
            return markdown.markdown(
                source, extensions, safe_mode=True, enable_attributes=False)
        except Exception:
            log.exception('Error when rendering Markdown')
            if safe:
                log.debug('Fallback to render in plain mode')
                return cls.plain(source)
            else:
                raise

    @classmethod
    def rst(cls, source, safe=True, mentions=False):
        if mentions:
            mention_pat = re.compile(MENTIONS_REGEX)

            def wrapp(match_obj):
                uname = match_obj.groups()[0]
                return ' **@%(uname)s** ' % {'uname': uname}
            mention_hl = mention_pat.sub(wrapp, source).strip()
            # we extracted mentions render with this using Mentions false
            return cls.rst(mention_hl, safe=safe, mentions=False)

        source = safe_unicode(source)
        try:
            docutils_settings = dict(
                [(alias, None) for alias in
                 cls.RESTRUCTUREDTEXT_DISALLOWED_DIRECTIVES])

            docutils_settings.update({'input_encoding': 'unicode',
                                      'report_level': 4})

            for k, v in docutils_settings.iteritems():
                directives.register_directive(k, v)

            parts = publish_parts(source=source,
                                  writer_name="html4css1",
                                  settings_overrides=docutils_settings)

            return parts['html_title'] + parts["fragment"]
        except Exception:
            log.exception('Error when rendering RST')
            if safe:
                log.debug('Fallbacking to render in plain mode')
                return cls.plain(source)
            else:
                raise


class RstTemplateRenderer(object):

    def __init__(self):
        base = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        rst_template_dirs = [os.path.join(base, 'templates', 'rst_templates')]
        self.template_store = TemplateLookup(
            directories=rst_template_dirs,
            input_encoding='utf-8',
            imports=['from rhodecode.lib import helpers as h'])

    def _get_template(self, templatename):
        return self.template_store.get_template(templatename)

    def render(self, template_name, **kwargs):
        template = self._get_template(template_name)
        return template.render(**kwargs)
