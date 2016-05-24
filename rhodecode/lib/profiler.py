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


import gc
import objgraph
import cProfile
import pstats
import cgi
import pprint
import threading

from StringIO import StringIO


class ProfilingMiddleware(object):
    def __init__(self, app):
        self.lock = threading.Lock()
        self.app = app

    def __call__(self, environ, start_response):
        with self.lock:
            profiler = cProfile.Profile()

            def run_app(*a, **kw):
                self.response = self.app(environ, start_response)

            profiler.runcall(run_app, environ, start_response)

            profiler.snapshot_stats()

            stats = pstats.Stats(profiler)
            stats.sort_stats('calls') #cummulative

            # Redirect output
            out = StringIO()
            stats.stream = out

            stats.print_stats()

            resp = ''.join(self.response)

            # Lets at least only put this on html-like responses.
            if resp.strip().startswith('<'):
                ## The profiling info is just appended to the response.
                ##  Browsers don't mind this.
                resp += ('<pre style="text-align:left; '
                         'border-top: 4px dashed red; padding: 1em;">')
                resp += cgi.escape(out.getvalue(), True)

                ct = objgraph.show_most_common_types()
                print ct

                resp += ct if ct else '---'

                output = StringIO()
                pprint.pprint(environ, output, depth=3)

                resp += cgi.escape(output.getvalue(), True)
                resp += '</pre>'

            return resp
