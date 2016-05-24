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
Tests checking the crypto backends which can be used by lib/auth.
"""
import collections

import pytest

from rhodecode.lib import auth


# Utility functions to get or check passwords

def test_get_crypt_password_accepts_unicode(password):
    result = auth.get_crypt_password(password.value)
    assert result == password.hashed


def test_check_password_accepts_unicode(password):
    result = auth.check_password(password.value, password.hashed)
    assert result


# API contracts from _RhodeCodeCryptoBase

def test_constructor_takes_no_arguments(crypto_backend_class):
    instance = crypto_backend_class()
    assert instance


def test_hash_create_returns_bytes(crypto_backend, password):
    hashed = crypto_backend.hash_create(password.encoded)
    assert isinstance(hashed, str)


def test_hash_create_changes_the_value(crypto_backend, password):
    hashed = crypto_backend.hash_create(password.encoded)
    assert hashed != password.encoded


def test_hash_create_enforces_bytes(crypto_backend, password):
    with pytest.raises(TypeError):
        crypto_backend.hash_create(password.value)


def test_hash_check(crypto_backend, password):
    not_matching = 'stub-hash'
    with pytest.raises(TypeError):
        crypto_backend.hash_check(password.value, not_matching)


def test_hash_check_with_update_enforces_bytes(crypto_backend, password):
    not_matching = 'stub-hash'
    with pytest.raises(TypeError):
        crypto_backend.hash_check_with_upgrade(password.value, not_matching)


@pytest.fixture(params=[
    auth._RhodeCodeCryptoMd5,
    auth._RhodeCodeCryptoBCrypt,
    auth._RhodeCodeCryptoSha256,
])
def crypto_backend_class(request):
    """
    Parameterizes per crypto backend class.
    """
    return request.param


@pytest.fixture
def crypto_backend(crypto_backend_class):
    return crypto_backend_class()


@pytest.fixture
def password():
    encoding = 'utf-8'
    value = u'value'
    value_encoded = value.encode(encoding)
    value_hashed = auth.crypto_backend().hash_create(value_encoded)
    return collections.namedtuple('Password', 'value, encoded, hashed')(
        value, value_encoded, value_hashed)
