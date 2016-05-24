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
Utility to gather certain statistics about a process.

Used to generate data about the memory consumption of the vcsserver. It is
quite generic and should work for every process. Use the parameter `--help`
to see all options.

Example call::

  python profile-mem.py --pid=89816 --ae --ae-key=YOUR_API_KEY

"""


import argparse
import json
import sys
import time

import datetime
import requests
import psutil

import logging
import socket
logging.basicConfig(level=logging.DEBUG)


def profile():
    config = parse_options()
    try:
        process = psutil.Process(config.pid)
    except psutil.NoSuchProcess:
        print "Process {pid} does not exist!".format(pid=config.pid)
        sys.exit(1)

    while True:
        stats = process_stats(process)
        dump_stats(stats)
        if config.appenlight:
            client = AppenlightClient(
                url=config.appenlight_url,
                api_key=config.appenlight_api_key)
            client.dump_stats(stats)
        time.sleep(config.interval)


def parse_options():
    parser = argparse.ArgumentParser(
        description=__doc__)
    parser.add_argument(
        '--pid', required=True, type=int,
        help="Process ID to monitor.")
    parser.add_argument(
        '--interval', '-i', type=float, default=5,
        help="Interval in secods.")
    parser.add_argument(
        '--appenlight', '--ae', action='store_true')
    parser.add_argument(
        '--appenlight-url', '--ae-url',
        default='https://ae.rhodecode.com/api/logs',
        help='URL of the Appenlight API endpoint, defaults to "%(default)s".')
    parser.add_argument(
        '--appenlight-api-key', '--ae-key',
        help='API key to use when sending data to appenlight. This has to be '
             'set if Appenlight is enabled.')
    return parser.parse_args()


def process_stats(process):
    mem = process.memory_info()
    iso_now = datetime.datetime.utcnow().isoformat()
    stats = [
        {'message': 'Memory stats of process {pid}'.format(pid=process.pid),
         'namespace': 'process.{pid}'.format(pid=process.pid),
         'server': socket.getfqdn(socket.gethostname()),
         'tags': [
            ['rss', mem.rss],
            ['vms', mem.vms]],
         'date': iso_now,
         },
    ]
    return stats


def dump_stats(stats):
    for sample in stats:
        print json.dumps(sample)


class AppenlightClient():

    url_template = '{url}?protocol_version=0.5'

    def __init__(self, url, api_key):
        self.url = self.url_template.format(url=url)
        self.api_key = api_key

    def dump_stats(self, stats):
        response = requests.post(
            self.url,
            headers={
                'X-appenlight-api-key': self.api_key},
            data=json.dumps(stats))
        if not response.status_code == 200:
            logging.error(
                'Sending to appenlight failed\n%s\n%s',
                response.headers, response.text)


if __name__ == '__main__':
    try:
        profile()
    except KeyboardInterrupt:
        pass
