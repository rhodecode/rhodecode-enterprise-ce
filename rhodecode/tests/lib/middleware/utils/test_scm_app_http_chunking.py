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
Checking the chunked data transfer via HTTP
"""

import os
import time
import subprocess

import pytest
import requests

from rhodecode.lib.middleware.utils import scm_app_http
from rhodecode.tests.utils import wait_for_url


def test_does_chunked_end_to_end_transfer(scm_app):
    response = requests.post(scm_app, data='', stream=True)
    assert response.headers['Transfer-Encoding'] == 'chunked'
    times = [time.time() for chunk in response.raw.read_chunked()]
    assert times[1] - times[0] > 0.1, "Chunks arrived at the same time"


@pytest.fixture
def echo_app_chunking(request, available_port_factory):
    """
    Run the EchoApp via Waitress in a subprocess.

    Return the URL endpoint to reach the app.
    """
    port = available_port_factory()
    command = (
        'waitress-serve --send-bytes 1 --port {port} --call '
        'rhodecode.tests.lib.middleware.utils.test_scm_app_http_chunking'
        ':create_echo_app')
    command = command.format(port=port)
    proc = subprocess.Popen(command.split(' '), bufsize=0)
    echo_app_url = 'http://localhost:' + str(port)

    @request.addfinalizer
    def stop_echo_app():
        proc.kill()

    return echo_app_url


@pytest.fixture
def scm_app(request, available_port_factory, echo_app_chunking):
    """
    Run the scm_app in Waitress.

    Returns the URL endpoint where this app can be reached.
    """
    port = available_port_factory()
    command = (
        'waitress-serve --send-bytes 1 --port {port} --call '
        'rhodecode.tests.lib.middleware.utils.test_scm_app_http_chunking'
        ':create_scm_app')
    command = command.format(port=port)
    env = os.environ.copy()
    env["RC_ECHO_URL"] = echo_app_chunking
    proc = subprocess.Popen(command.split(' '), bufsize=0, env=env)
    scm_app_url = 'http://localhost:' + str(port)
    wait_for_url(scm_app_url)

    @request.addfinalizer
    def stop_echo_app():
        proc.kill()

    return scm_app_url


class EchoApp(object):
    """
    Stub WSGI application which returns a chunked response to every request.
    """

    def __init__(self, repo_path, repo_name, config):
        self._repo_path = repo_path

    def __call__(self, environ, start_response):
        environ['wsgi.input'].read()
        status = '200 OK'
        headers = []
        start_response(status, headers)
        return result_generator()


def result_generator():
    """
    Simulate chunked results.

    The intended usage is to simulate a chunked response as we would get it
    out of a vcs operation during a call to "hg clone".
    """
    yield 'waiting 2 seconds'
    # Wait long enough so that the first chunk can go out
    time.sleep(2)
    yield 'final chunk'
    # Another small wait, otherwise they go together
    time.sleep(0.1)


def create_echo_app():
    """
    Create EchoApp filled with stub data.
    """
    return EchoApp('stub_path', 'repo_name', {})


def create_scm_app():
    """
    Create a scm_app hooked up to speak to EchoApp.
    """
    echo_app_url = os.environ["RC_ECHO_URL"]
    return scm_app_http.VcsHttpProxy(
        echo_app_url, 'stub_path', 'stub_name', None)
