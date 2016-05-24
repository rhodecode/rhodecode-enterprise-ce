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
Anontation library for usage in rhodecode, previously part of vcs
"""

import StringIO

from pygments import highlight
from pygments.formatters import HtmlFormatter

from rhodecode.lib.vcs.exceptions import VCSError
from rhodecode.lib.vcs.nodes import FileNode


def annotate_highlight(
        filenode, annotate_from_commit_func=None,
        order=None, headers=None, **options):
    """
    Returns html portion containing annotated table with 3 columns: line
    numbers, commit information and pygmentized line of code.

    :param filenode: FileNode object
    :param annotate_from_commit_func: function taking commit and
      returning single annotate cell; needs break line at the end
    :param order: ordered sequence of ``ls`` (line numbers column),
      ``annotate`` (annotate column), ``code`` (code column); Default is
      ``['ls', 'annotate', 'code']``
    :param headers: dictionary with headers (keys are whats in ``order``
      parameter)
    """
    from rhodecode.lib.utils import get_custom_lexer
    options['linenos'] = True
    formatter = AnnotateHtmlFormatter(
        filenode=filenode, order=order, headers=headers,
        annotate_from_commit_func=annotate_from_commit_func, **options)
    lexer = get_custom_lexer(filenode.extension) or filenode.lexer
    highlighted = highlight(filenode.content, lexer, formatter)
    return highlighted


class AnnotateHtmlFormatter(HtmlFormatter):

    def __init__(
            self, filenode, annotate_from_commit_func=None,
            order=None, **options):
        """
        If ``annotate_from_commit_func`` is passed, it should be a function
        which returns string from the given commit. For example, we may pass
        following function as ``annotate_from_commit_func``::

            def commit_to_anchor(commit):
                return '<a href="/commits/%s/">%s</a>\n' %\
                       (commit.id, commit.id)

        :param annotate_from_commit_func: see above
        :param order: (default: ``['ls', 'annotate', 'code']``); order of
          columns;
        :param options: standard pygment's HtmlFormatter options, there is
          extra option tough, ``headers``. For instance we can pass::

             formatter = AnnotateHtmlFormatter(filenode, headers={
                'ls': '#',
                'annotate': 'Annotate',
                'code': 'Code',
             })

        """
        super(AnnotateHtmlFormatter, self).__init__(**options)
        self.annotate_from_commit_func = annotate_from_commit_func
        self.order = order or ('ls', 'annotate', 'code')
        headers = options.pop('headers', None)
        if headers and not (
                'ls' in headers and 'annotate' in headers and 'code' in headers):
            raise ValueError(
                "If headers option dict is specified it must "
                "all 'ls', 'annotate' and 'code' keys")
        self.headers = headers
        if isinstance(filenode, FileNode):
            self.filenode = filenode
        else:
            raise VCSError(
                "This formatter expect FileNode parameter, not %r" %
                type(filenode))

    def annotate_from_commit(self, commit):
        """
        Returns full html line for single commit per annotated line.
        """
        if self.annotate_from_commit_func:
            return self.annotate_from_commit_func(commit)
        else:
            return commit.id + '\n'

    def _wrap_tablelinenos(self, inner):
        dummyoutfile = StringIO.StringIO()
        lncount = 0
        for t, line in inner:
            if t:
                lncount += 1
            dummyoutfile.write(line)

        fl = self.linenostart
        mw = len(str(lncount + fl - 1))
        sp = self.linenospecial
        st = self.linenostep
        la = self.lineanchors
        aln = self.anchorlinenos
        if sp:
            lines = []

            for i in range(fl, fl + lncount):
                if i % st == 0:
                    if i % sp == 0:
                        if aln:
                            lines.append('<a href="#%s-%d" class="special">'
                                         '%*d</a>' %
                                         (la, i, mw, i))
                        else:
                            lines.append('<span class="special">'
                                         '%*d</span>' % (mw, i))
                    else:
                        if aln:
                            lines.append('<a href="#%s-%d">'
                                         '%*d</a>' % (la, i, mw, i))
                        else:
                            lines.append('%*d' % (mw, i))
                else:
                    lines.append('')
            ls = '\n'.join(lines)
        else:
            lines = []
            for i in range(fl, fl + lncount):
                if i % st == 0:
                    if aln:
                        lines.append('<a href="#%s-%d">%*d</a>' \
                                     % (la, i, mw, i))
                    else:
                        lines.append('%*d' % (mw, i))
                else:
                    lines.append('')
            ls = '\n'.join(lines)

        cached = {}
        annotate = []
        for el in self.filenode.annotate:
            commit_id = el[1]
            if commit_id in cached:
                result = cached[commit_id]
            else:
                commit = el[2]()
                result = self.annotate_from_commit(commit)
                cached[commit_id] = result
            annotate.append(result)

        annotate = ''.join(annotate)

        # in case you wonder about the seemingly redundant <div> here:
        # since the content in the other cell also is wrapped in a div,
        # some browsers in some configurations seem to mess up the formatting.
        '''
        yield 0, ('<table class="%stable">' % self.cssclass +
                  '<tr><td class="linenos"><div class="linenodiv"><pre>' +
                  ls + '</pre></div></td>' +
                  '<td class="code">')
        yield 0, dummyoutfile.getvalue()
        yield 0, '</td></tr></table>'

        '''
        headers_row = []
        if self.headers:
            headers_row = ['<tr class="annotate-header">']
            for key in self.order:
                td = ''.join(('<td>', self.headers[key], '</td>'))
                headers_row.append(td)
            headers_row.append('</tr>')

        body_row_start = ['<tr>']
        for key in self.order:
            if key == 'ls':
                body_row_start.append(
                    '<td class="linenos"><div class="linenodiv"><pre>' +
                    ls + '</pre></div></td>')
            elif key == 'annotate':
                body_row_start.append(
                    '<td class="annotate"><div class="annotatediv"><pre>' +
                    annotate + '</pre></div></td>')
            elif key == 'code':
                body_row_start.append('<td class="code">')
        yield 0, ('<table class="%stable">' % self.cssclass +
                  ''.join(headers_row) +
                  ''.join(body_row_start)
                  )
        yield 0, dummyoutfile.getvalue()
        yield 0, '</td></tr></table>'
