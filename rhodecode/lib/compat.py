# -*- coding: utf-8 -*-

# Copyright (C) 2011-2016  RhodeCode GmbH
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
Python backward compatibility functions and common libs
"""


import os
import sys

import rhodecode


# ==============================================================================
# kill FUNCTIONS
# ==============================================================================
if rhodecode.is_windows:
    import ctypes

    def kill(pid, sig):
        """Kill function for Win32."""
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(1, 0, pid)
        return kernel32.TerminateProcess(handle, 0) != 0
else:
    kill = os.kill


# ==============================================================================
# OrderedDict
# ==============================================================================
from collections import OrderedDict
