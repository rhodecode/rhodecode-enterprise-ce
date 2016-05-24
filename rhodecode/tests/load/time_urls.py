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

import timeit

server = "localhost:5000"

pages = [
    "cpython",
    "cpython/annotate/74236c8bf064188516b32bf95016971227ec72a9/Makefile.pre.in",
    "cpython/changelog",
    "cpython/changeset/e0f681f4ade3af52915d5f32daac97ada580d71a",
    "cpython/compare/tag@v3.4.1rc1...tag@v3.4.1?target_repo=cpython",
    "cpython/files/tip/",
    "cpython/files/74236c8bf064188516b32bf95016971227ec72a9/Grammar",
    "",
    "git",
    "git/annotate/6c4ab27f2378ce67940b4496365043119d7ffff2/gitk-git/.gitignore",
    "git/changelog",
    "git/changeset/d299e9e550c1bf8640907fdba1f03cc585ee71df",
    "git/compare/rev@1200...rev@1300?target_repo=git",
    "git/files/tip/",
    "git/files/6c4ab27f2378ce67940b4496365043119d7ffff2/.gitignore"
]

svn_pages = [
    "svn-apache",
    "svn-apache/annotate/672129/cocoon/trunk/README.txt",
    "svn-apache/changelog",
    "svn-apache/changeset/1164362",
    "svn-apache/compare/rev@1164350...rev@1164360?target_repo=svn-apache",
    "svn-apache/compare/rev@1164300...rev@1164360?target_repo=svn-apache",
    "svn-apache/files/tip/",
    "svn-apache/files/1164363/cocoon/trunk/README.txt",
]

# Uncomment to check also svn performance
# pages = pages + svn_pages

repeat = 10

print "Repeating each URL x%d\n" % repeat
for page in pages:
    url = "http://%s/%s" % (server, page)
    print url

    stmt = "urllib2.urlopen('%s', timeout=120)" % url
    t = timeit.Timer(stmt=stmt, setup="import urllib2")

    result = t.repeat(repeat=repeat, number=1)
    print "\t%.3f (min) - %.3f (max) - %.3f (avg)\n" % \
          (min(result), max(result), sum(result)/len(result))
