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
Generic encryption library for RhodeCode
"""

import hashlib
import base64

from Crypto.Cipher import AES
from Crypto import Random

from rhodecode.lib.utils2 import safe_str


class AESCipher(object):
    def __init__(self, key):
        # create padding, trim to long enc key
        if not key:
            raise ValueError('passed key variable is empty')
        self.block_size = 32
        self.key = hashlib.sha256(safe_str(key)).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return (s + (self.block_size - len(s) % self.block_size)
                * chr(self.block_size - len(s) % self.block_size))

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]