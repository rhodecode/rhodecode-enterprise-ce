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

from rhodecode.lib.vcs import exceptions


class TestMapVcsExceptions:

    def test_maps_exceptions_based_on_exception_map(self):
        with pytest.raises(exceptions.RepositoryError):
            self.func(kind='abort')

    def test_raises_key_error_if_kind_is_unknown(self):
        with pytest.raises(KeyError):
            self.func(kind='not_existing_kind')

    def test_raises_exception_unchanged_if_no_vcs_kind(self):
        with pytest.raises(Exception) as exc:
            self.func(exc=ValueError())
        assert exc.type == ValueError

    @exceptions.map_vcs_exceptions
    def func(self, kind=None, exc=None):
        exc = exc or Exception()
        if kind:
            exc._vcs_kind = kind
        raise exc
