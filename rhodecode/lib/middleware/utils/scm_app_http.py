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
Implementation of the scm_app interface using raw HTTP communication.
"""

import base64
import logging
import urlparse
import wsgiref.util

import msgpack
import requests
import webob.request

import rhodecode


log = logging.getLogger(__name__)


def create_git_wsgi_app(repo_path, repo_name, config):
    url = _vcs_streaming_url() + 'git/'
    return VcsHttpProxy(url, repo_path, repo_name, config)


def create_hg_wsgi_app(repo_path, repo_name, config):
    url = _vcs_streaming_url() + 'hg/'
    return VcsHttpProxy(url, repo_path, repo_name, config)


def _vcs_streaming_url():
    template = 'http://{}/stream/'
    return template.format(rhodecode.CONFIG['vcs.server'])


# TODO: johbo: Avoid the global.
session = requests.Session()
# Requests speedup, avoid reading .netrc and similar
session.trust_env = False


class VcsHttpProxy(object):
    """
    A WSGI application which proxies vcs requests.

    The goal is to shuffle the data around without touching it. The only
    exception is the extra data from the config object which we send to the
    server as well.
    """

    def __init__(self, url, repo_path, repo_name, config):
        """
        :param str url: The URL of the VCSServer to call.
        """
        self._url = url
        self._repo_name = repo_name
        self._repo_path = repo_path
        self._config = config
        log.debug(
            "Creating VcsHttpProxy for repo %s, url %s",
            repo_name, url)

    def __call__(self, environ, start_response):
        status = '200 OK'

        config = msgpack.packb(self._config)
        request = webob.request.Request(environ)
        request_headers = request.headers
        request_headers.update({
            # TODO: johbo: Remove this, rely on URL path only
            'X-RC-Repo-Name': self._repo_name,
            'X-RC-Repo-Path': self._repo_path,
            'X-RC-Path-Info': environ['PATH_INFO'],
            # TODO: johbo: Avoid encoding and put this into payload?
            'X-RC-Repo-Config': base64.b64encode(config),
        })

        data = environ['wsgi.input'].read()
        method = environ['REQUEST_METHOD']

        # Preserve the query string
        url = self._url
        url = urlparse.urljoin(url, self._repo_name)
        if environ.get('QUERY_STRING'):
            url += '?' + environ['QUERY_STRING']

        response = session.request(
            method, url,
            data=data,
            headers=request_headers,
            stream=True)

        # Preserve the headers of the response, except hop_by_hop ones
        response_headers = [
            (h, v) for h, v in response.headers.items()
            if not wsgiref.util.is_hop_by_hop(h)
        ]

        # TODO: johbo: Better way to get the status including text?
        status = str(response.status_code)
        start_response(status, response_headers)
        return _maybe_stream(response)


def _maybe_stream(response):
    """
    Try to generate chunks from the response if it is chunked.
    """
    if _is_chunked(response):
        return response.raw.read_chunked()
    else:
        return [response.content]


def _is_chunked(response):
    return response.headers.get('Transfer-Encoding', '') == 'chunked'
