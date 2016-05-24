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
This module provides some useful tools for ``vcs`` like annotate/diff html
output. It also includes some internal helpers.
"""


def author_email(author):
    """
    returns email address of given author.
    If any of <,> sign are found, it fallbacks to regex findall()
    and returns first found result or empty string

    Regex taken from http://www.regular-expressions.info/email.html
    """
    import re
    if not author:
        return ''

    r = author.find('>')
    l = author.find('<')

    if l == -1 or r == -1:
        # fallback to regex match of email out of a string
        email_re = re.compile(r"""[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!"""
                              r"""#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z"""
                              r"""0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]"""
                              r"""*[a-z0-9])?""", re.IGNORECASE)
        m = re.findall(email_re, author)
        return m[0] if m else ''

    return author[l + 1:r].strip()


def author_name(author):
    """
    get name of author, or else username.
    It'll try to find an email in the author string and just cut it off
    to get the username
    """

    if not author or not '@' in author:
        return author
    else:
        return author.replace(author_email(author), '').replace('<', '')\
            .replace('>', '').strip()
