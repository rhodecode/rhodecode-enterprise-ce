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


import datetime
import decimal
import logging
import time

from rhodecode.api import jsonrpc_method, jsonrpc_deprecated_method, JSONRPCError, JSONRPCForbidden

from rhodecode.api.utils import Optional, OAttr

log = logging.getLogger(__name__)


@jsonrpc_method()
def test(request, apiuser, args):
    return args


@jsonrpc_method()
def test_ok(request, apiuser):
    return {
        'who': u'hello {} '.format(apiuser),
        'obj': {
            'time': time.time(),
            'dt': datetime.datetime.now(),
            'decimal': decimal.Decimal('0.123')
        }
    }


@jsonrpc_method()
def test_error(request, apiuser):
    raise JSONRPCError('error happened')


@jsonrpc_method()
def test_exception(request, apiuser):
    raise Exception('something unhanddled')


@jsonrpc_method()
def test_params(request, apiuser, params):
    return u'hello apiuser:{} params:{}'.format(apiuser, params)


@jsonrpc_method()
def test_params_opt(
        request, apiuser, params, opt1=False, opt2=Optional(True),
        opt3=Optional(OAttr('apiuser'))):
    opt2 = Optional.extract(opt2)
    opt3 = Optional.extract(opt3, evaluate_locals=locals())

    return u'hello apiuser:{} params:{}, opt:[{},{},{}]'.format(
        apiuser, params, opt1, opt2, opt3)


@jsonrpc_method()
@jsonrpc_deprecated_method(
    use_method='test_ok', deprecated_at_version='4.0.0')
def test_deprecated_method(request, apiuser):
    return u'value'


@jsonrpc_method()
def test_forbidden_method(request, apiuser):
    raise JSONRPCForbidden()
