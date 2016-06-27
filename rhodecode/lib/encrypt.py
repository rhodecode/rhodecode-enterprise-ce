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

import base64

from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Hash import HMAC, SHA256

from rhodecode.lib.utils2 import safe_str


class SignatureVerificationError(Exception):
    pass


class InvalidDecryptedValue(str):

    def __new__(cls, content):
        """
        This will generate something like this::
            <InvalidDecryptedValue(QkWusFgLJXR6m42v...)>
        And represent a safe indicator that encryption key is broken
        """
        content = '<{}({}...)>'.format(cls.__name__, content[:16])
        return str.__new__(cls, content)


class AESCipher(object):
    def __init__(self, key, hmac=False, strict_verification=True):
        if not key:
            raise ValueError('passed key variable is empty')
        self.strict_verification = strict_verification
        self.block_size = 32
        self.hmac_size = 32
        self.hmac = hmac

        self.key = SHA256.new(safe_str(key)).digest()
        self.hmac_key = SHA256.new(self.key).digest()

    def verify_hmac_signature(self, raw_data):
        org_hmac_signature = raw_data[-self.hmac_size:]
        data_without_sig = raw_data[:-self.hmac_size]
        recomputed_hmac = HMAC.new(
            self.hmac_key, data_without_sig, digestmod=SHA256).digest()
        return org_hmac_signature == recomputed_hmac

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        enc_value = cipher.encrypt(raw)

        hmac_signature = ''
        if self.hmac:
            # compute hmac+sha256 on iv + enc text, we use
            # encrypt then mac method to create the signature
            hmac_signature = HMAC.new(
                self.hmac_key, iv + enc_value, digestmod=SHA256).digest()

        return base64.b64encode(iv + enc_value + hmac_signature)

    def decrypt(self, enc):
        enc_org = enc
        enc = base64.b64decode(enc)

        if self.hmac and len(enc) > self.hmac_size:
            if self.verify_hmac_signature(enc):
                # cut off the HMAC verification digest
                enc = enc[:-self.hmac_size]
            else:
                if self.strict_verification:
                    raise SignatureVerificationError(
                        "Encryption signature verification failed. "
                        "Please check your secret key, and/or encrypted value. "
                        "Secret key is stored as "
                        "`rhodecode.encrypted_values.secret` or "
                        "`beaker.session.secret` inside .ini file")

                return InvalidDecryptedValue(enc_org)

        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return (s + (self.block_size - len(s) % self.block_size)
                * chr(self.block_size - len(s) % self.block_size))

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]