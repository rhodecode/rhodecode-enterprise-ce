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

import argparse

from rhodecode_api import RhodeCodeAPI


def add_api_pr_args(parser):
    parser.add_argument("--token", help="Rhodecode user token", required=True)
    parser.add_argument("--url", help="Rhodecode host url", required=True)
    parser.add_argument("--repoid", help="Repo id", required=True)
    parser.add_argument("--prid", help="Pull request id", required=True)
    parser.add_argument("--message", help="Comment to add", required=True)

    parser.add_argument("--status", help="Status to set (approved|rejected)")
    parser.add_argument(
        "--commit-id",
        help="Expected commit ID for source repo")


def get_pr_head(args):
    rc = RhodeCodeAPI(args.url, args.token)
    pr_info = rc.get_pull_request(
        repoid=args.repoid,
        pullrequestid=args.prid
    )
    if pr_info['error']:
        return None

    return pr_info['result']['source']['reference']['commit_id']


def pr_has_same_head(args):
    head_id = get_pr_head(args)
    return head_id == args.commit_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_api_pr_args(parser)
    args = parser.parse_args()
    status = args.status

    if args.commit_id and status:
        if not pr_has_same_head(args):
            # PR updated, don't set status
            status = None

    rc = RhodeCodeAPI(args.url, args.token)
    resp = rc.comment_pull_request(
        repoid=args.repoid,
        pullrequestid=int(args.prid),
        message=args.message,
        status=status
    )

    if resp['error']:
        raise Exception(resp['error'])
    else:
        print resp
