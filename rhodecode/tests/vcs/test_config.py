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

import pytest


def test_get_existing_value(config):
    value = config.get('section-a', 'a-1')
    assert value == 'value-a-1'


@pytest.mark.parametrize('section, option', [
    ('section-a', 'does-not-exist'),
    ('does-not-exist', 'does-not-exist'),
])
def test_get_unset_value_returns_none(config, section, option):
    value = config.get(section, option)
    assert value is None


def test_allows_to_create_a_copy(config):
    clone = config.copy()
    assert set(config.serialize()) == set(clone.serialize())


def test_changes_in_the_copy_dont_affect_the_original(config):
    clone = config.copy()
    clone.set('section-a', 'a-2', 'value-a-2')
    assert set(config.serialize()) == {('section-a', 'a-1', 'value-a-1')}


def test_changes_in_the_original_dont_affect_the_copy(config):
    clone = config.copy()
    config.set('section-a', 'a-2', 'value-a-2')
    assert set(clone.serialize()) == {('section-a', 'a-1', 'value-a-1')}
