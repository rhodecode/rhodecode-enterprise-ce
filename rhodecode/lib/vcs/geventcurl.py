# -*- coding: utf-8 -*-

# Copyright (C) 2016-2016  RhodeCode GmbH
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
This serves as a drop in replacement for pycurl. It implements the pycurl Curl
class in a way that is compatible with gevent.
"""


import logging
import gevent
import pycurl

# Import everything from pycurl.
# This allows us to use this module as a drop in replacement of pycurl.
from pycurl import *  # noqa

from gevent import core
from gevent.hub import Waiter


log = logging.getLogger(__name__)


class GeventCurlMulti(object):
    """
    Wrapper around pycurl.CurlMulti that integrates it into gevent's event
    loop.
    """

    def __init__(self, loop=None):
        self._watchers = {}
        self._timeout = None
        self.loop = loop or gevent.get_hub().loop

        # Setup curl's multi instance.
        self._curl_multi = pycurl.CurlMulti()
        self.setopt(pycurl.M_TIMERFUNCTION, self._set_timeout)
        self.setopt(pycurl.M_SOCKETFUNCTION, self._handle_socket)

    def __getattr__(self, item):
        """
        The pycurl.CurlMulti class is final and we cannot subclass it.
        Therefore we are wrapping it and forward everything to it here.
        """
        return getattr(self._curl_multi, item)

    def add_handle(self, curl):
        """
        Add handle variant that also takes care about the initial invocation of
        socket action method. This is done by setting an immediate timeout.
        """
        result = self._curl_multi.add_handle(curl)
        self._set_timeout(0)
        return result

    def _handle_socket(self, event, fd, multi, data):
        """
        Called by libcurl when it wants to change the file descriptors it cares
        about.
        """
        event_map = {
            pycurl.POLL_NONE: core.NONE,
            pycurl.POLL_IN: core.READ,
            pycurl.POLL_OUT: core.WRITE,
            pycurl.POLL_INOUT: core.READ | core.WRITE
        }

        if event == pycurl.POLL_REMOVE:
            watcher = self._watchers.pop(fd, None)
            if watcher is not None:
                watcher.stop()
        else:
            gloop_event = event_map[event]
            watcher = self._watchers.get(fd)
            if watcher is None:
                watcher = self.loop.io(fd, gloop_event)
                watcher.start(self._handle_events, fd, pass_events=True)
                self._watchers[fd] = watcher
            else:
                if watcher.events != gloop_event:
                    watcher.stop()
                    watcher.events = gloop_event
                    watcher.start(self._handle_events, fd, pass_events=True)

    def _set_timeout(self, msecs):
        """
        Called by libcurl to schedule a timeout.
        """
        if self._timeout is not None:
            self._timeout.stop()
        self._timeout = self.loop.timer(msecs/1000.0)
        self._timeout.start(self._handle_timeout)

    def _handle_events(self, events, fd):
        action = 0
        if events & core.READ:
            action |= pycurl.CSELECT_IN
        if events & core.WRITE:
            action |= pycurl.CSELECT_OUT
        while True:
            try:
                ret, num_handles = self._curl_multi.socket_action(fd, action)
            except pycurl.error, e:
                ret = e.args[0]
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
        self._finish_pending_requests()

    def _handle_timeout(self):
        """
        Called by IOLoop when the requested timeout has passed.
        """
        if self._timeout is not None:
            self._timeout.stop()
            self._timeout = None
        while True:
            try:
                ret, num_handles = self._curl_multi.socket_action(
                    pycurl.SOCKET_TIMEOUT, 0)
            except pycurl.error, e:
                ret = e.args[0]
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
        self._finish_pending_requests()

        # In theory, we shouldn't have to do this because curl will call
        # _set_timeout whenever the timeout changes. However, sometimes after
        # _handle_timeout we will need to reschedule immediately even though
        # nothing has changed from curl's perspective. This is because when
        # socket_action is called with SOCKET_TIMEOUT, libcurl decides
        # internally which timeouts need to be processed by using a monotonic
        # clock (where available) while tornado uses python's time.time() to
        # decide when timeouts have occurred. When those clocks disagree on
        # elapsed time (as they will whenever there is an NTP adjustment),
        # tornado might call _handle_timeout before libcurl is ready. After
        # each timeout, resync the scheduled timeout with libcurl's current
        # state.
        new_timeout = self._curl_multi.timeout()
        if new_timeout >= 0:
            self._set_timeout(new_timeout)

    def _finish_pending_requests(self):
        """
        Process any requests that were completed by the last call to
        multi.socket_action.
        """
        while True:
            num_q, ok_list, err_list = self._curl_multi.info_read()
            for curl in ok_list:
                curl.waiter.switch()
            for curl, errnum, errmsg in err_list:
                curl.waiter.throw(Exception('%s %s' % (errnum, errmsg)))
            if num_q == 0:
                break


class GeventCurl(object):
    """
    Gevent compatible implementation of the pycurl.Curl class. Essentially a
    wrapper around pycurl.Curl with a customized perform method. It uses the
    GeventCurlMulti class to implement a blocking API to libcurl's "easy"
    interface.
    """

    # Reference to the GeventCurlMulti instance.
    _multi_instance = None

    def __init__(self):
        self._curl = pycurl.Curl()

    def __getattr__(self, item):
        """
        The pycurl.Curl class is final and we cannot subclass it. Therefore we
        are wrapping it and forward everything to it here.
        """
        return getattr(self._curl, item)

    @property
    def _multi(self):
        """
        Lazy property that returns the GeventCurlMulti instance. The value is
        cached as a class attribute. Therefore only one instance per process
        exists.
        """
        if GeventCurl._multi_instance is None:
            GeventCurl._multi_instance = GeventCurlMulti()
        return GeventCurl._multi_instance

    def perform(self):
        """
        This perform method is compatible with gevent because it uses gevent
        synchronization mechanisms to wait for the request to finish.
        """
        waiter = self._curl.waiter = Waiter()
        try:
            self._multi.add_handle(self._curl)
            response = waiter.get()
        finally:
            self._multi.remove_handle(self._curl)
            del self._curl.waiter

        return response

# Curl is originally imported from pycurl. At this point we override it with
# our custom implementation.
Curl = GeventCurl
