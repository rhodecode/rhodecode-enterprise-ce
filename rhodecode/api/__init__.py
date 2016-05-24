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

import inspect
import itertools
import logging
import types

import decorator
import venusian
from pyramid.exceptions import ConfigurationError
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotFound

from rhodecode.api.exc import JSONRPCBaseError, JSONRPCError, JSONRPCForbidden
from rhodecode.lib.auth import AuthUser
from rhodecode.lib.base import get_ip_addr
from rhodecode.lib.ext_json import json
from rhodecode.lib.utils2 import safe_str
from rhodecode.lib.plugins.utils import get_plugin_settings
from rhodecode.model.db import User, UserApiKeys

log = logging.getLogger(__name__)

DEFAULT_RENDERER = 'jsonrpc_renderer'
DEFAULT_URL = '/_admin/apiv2'


class ExtJsonRenderer(object):
    """
    Custom renderer that mkaes use of our ext_json lib

    """

    def __init__(self, serializer=json.dumps, **kw):
        """ Any keyword arguments will be passed to the ``serializer``
        function."""
        self.serializer = serializer
        self.kw = kw

    def __call__(self, info):
        """ Returns a plain JSON-encoded string with content-type
        ``application/json``. The content-type may be overridden by
        setting ``request.response.content_type``."""

        def _render(value, system):
            request = system.get('request')
            if request is not None:
                response = request.response
                ct = response.content_type
                if ct == response.default_content_type:
                    response.content_type = 'application/json'

            return self.serializer(value, **self.kw)

        return _render


def jsonrpc_response(request, result):
    rpc_id = getattr(request, 'rpc_id', None)
    response = request.response

    # store content_type before render is called
    ct = response.content_type

    ret_value = ''
    if rpc_id:
        ret_value = {
            'id': rpc_id,
            'result': result,
            'error': None,
        }

        # fetch deprecation warnings, and store it inside results
        deprecation = getattr(request, 'rpc_deprecation', None)
        if deprecation:
            ret_value['DEPRECATION_WARNING'] = deprecation

    raw_body = render(DEFAULT_RENDERER, ret_value, request=request)
    response.body = safe_str(raw_body, response.charset)

    if ct == response.default_content_type:
        response.content_type = 'application/json'

    return response


def jsonrpc_error(request, message, retid=None, code=None):
    """
    Generate a Response object with a JSON-RPC error body

    :param code:
    :param retid:
    :param message:
    """
    err_dict = {'id': retid, 'result': None, 'error': message}
    body = render(DEFAULT_RENDERER, err_dict, request=request).encode('utf-8')
    return Response(
        body=body,
        status=code,
        content_type='application/json'
    )


def exception_view(exc, request):
    rpc_id = getattr(request, 'rpc_id', None)

    fault_message = 'undefined error'
    if isinstance(exc, JSONRPCError):
        fault_message = exc.message
        log.debug('json-rpc error rpc_id:%s "%s"', rpc_id, fault_message)
    elif isinstance(exc, JSONRPCForbidden):
        fault_message = 'Access was denied to this resource.'
        log.warning('json-rpc forbidden call rpc_id:%s "%s"', rpc_id, fault_message)
    elif isinstance(exc, HTTPNotFound):
        method = request.rpc_method
        log.debug('json-rpc method `%s` not found in list of '
                  'api calls: %s, rpc_id:%s',
                  method, request.registry.jsonrpc_methods.keys(), rpc_id)
        fault_message = "No such method: {}".format(method)

    return jsonrpc_error(request, fault_message, rpc_id)


def request_view(request):
    """
    Main request handling method. It handles all logic to call a specific
    exposed method
    """

    # check if we can find this session using api_key, get_by_auth_token
    # search not expired tokens only

    try:
        u = User.get_by_auth_token(request.rpc_api_key)

        if u is None:
            return jsonrpc_error(
                request, retid=request.rpc_id, message='Invalid API KEY')

        if not u.active:
            return jsonrpc_error(
                request, retid=request.rpc_id,
                message='Request from this user not allowed')

        # check if we are allowed to use this IP
        auth_u = AuthUser(
            u.user_id, request.rpc_api_key, ip_addr=request.rpc_ip_addr)
        if not auth_u.ip_allowed:
            return jsonrpc_error(
                request, retid=request.rpc_id,
                message='Request from IP:%s not allowed' % (
                request.rpc_ip_addr,))
        else:
            log.info('Access for IP:%s allowed' % (request.rpc_ip_addr,))

        # now check if token is valid for API
        role = UserApiKeys.ROLE_API
        extra_auth_tokens = [
            x.api_key for x in User.extra_valid_auth_tokens(u, role=role)]
        active_tokens = [u.api_key] + extra_auth_tokens

        log.debug('Checking if API key has proper role')
        if request.rpc_api_key not in active_tokens:
            return jsonrpc_error(
                request, retid=request.rpc_id,
                message='API KEY has bad role for an API call')

    except Exception as e:
        log.exception('Error on API AUTH')
        return jsonrpc_error(
            request, retid=request.rpc_id, message='Invalid API KEY')

    method = request.rpc_method
    func = request.registry.jsonrpc_methods[method]

    # now that we have a method, add request._req_params to
    # self.kargs and dispatch control to WGIController
    argspec = inspect.getargspec(func)
    arglist = argspec[0]
    defaults = map(type, argspec[3] or [])
    default_empty = types.NotImplementedType

    # kw arguments required by this method
    func_kwargs = dict(itertools.izip_longest(
        reversed(arglist), reversed(defaults), fillvalue=default_empty))

    # This attribute will need to be first param of a method that uses
    # api_key, which is translated to instance of user at that name
    user_var = 'apiuser'
    request_var = 'request'

    for arg in [user_var, request_var]:
        if arg not in arglist:
            return jsonrpc_error(
                request,
                retid=request.rpc_id,
                message='This method [%s] does not support '
                        'required parameter `%s`' % (func.__name__, arg))

    # get our arglist and check if we provided them as args
    for arg, default in func_kwargs.items():
        if arg in [user_var, request_var]:
            # user_var and request_var are pre-hardcoded parameters and we
            # don't need to do any translation
            continue

        # skip the required param check if it's default value is
        # NotImplementedType (default_empty)
        if default == default_empty and arg not in request.rpc_params:
            return jsonrpc_error(
                request,
                retid=request.rpc_id,
                message=('Missing non optional `%s` arg in JSON DATA' % arg)
            )

    # sanitze extra passed arguments
    for k in request.rpc_params.keys()[:]:
        if k not in func_kwargs:
            del request.rpc_params[k]

    call_params = request.rpc_params
    call_params.update({
        'request': request,
        'apiuser': auth_u
    })
    try:
        ret_value = func(**call_params)
        return jsonrpc_response(request, ret_value)
    except JSONRPCBaseError:
        raise
    except Exception:
        log.exception('Unhandled exception occured on api call: %s', func)
        return jsonrpc_error(request, retid=request.rpc_id,
                             message='Internal server error')


def setup_request(request):
    """
    Parse a JSON-RPC request body. It's used inside the predicates method
    to validate and bootstrap requests for usage in rpc calls.

    We need to raise JSONRPCError here if we want to return some errors back to
    user.
    """
    log.debug('Executing setup request: %r', request)
    request.rpc_ip_addr = get_ip_addr(request.environ)
    # TODO: marcink, deprecate GET at some point
    if request.method not in ['POST', 'GET']:
        log.debug('unsupported request method "%s"', request.method)
        raise JSONRPCError(
            'unsupported request method "%s". Please use POST' % request.method)

    if 'CONTENT_LENGTH' not in request.environ:
        log.debug("No Content-Length")
        raise JSONRPCError("Empty body, No Content-Length in request")

    else:
        length = request.environ['CONTENT_LENGTH']
        log.debug('Content-Length: %s', length)

        if length == 0:
            log.debug("Content-Length is 0")
            raise JSONRPCError("Content-Length is 0")

    raw_body = request.body
    try:
        json_body = json.loads(raw_body)
    except ValueError as e:
        # catch JSON errors Here
        raise JSONRPCError("JSON parse error ERR:%s RAW:%r" % (e, raw_body))

    request.rpc_id = json_body.get('id')
    request.rpc_method = json_body.get('method')

    # check required base parameters
    try:
        api_key = json_body.get('api_key')
        if not api_key:
            api_key = json_body.get('auth_token')

        if not api_key:
            raise KeyError('api_key or auth_token')

        request.rpc_api_key = api_key
        request.rpc_id = json_body['id']
        request.rpc_method = json_body['method']
        request.rpc_params = json_body['args'] \
            if isinstance(json_body['args'], dict) else {}

        log.debug(
            'method: %s, params: %s' % (request.rpc_method, request.rpc_params))
    except KeyError as e:
        raise JSONRPCError('Incorrect JSON data. Missing %s' % e)

    log.debug('setup complete, now handling method:%s rpcid:%s',
              request.rpc_method, request.rpc_id, )


class RoutePredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'jsonrpc route = %s' % self.val

    phash = text

    def __call__(self, info, request):
        if self.val:
            # potentially setup and bootstrap our call
            setup_request(request)

            # Always return True so that even if it isn't a valid RPC it
            # will fall through to the underlaying handlers like notfound_view
            return True


class NotFoundPredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'jsonrpc method not found = %s' % self.val

    phash = text

    def __call__(self, info, request):
        return hasattr(request, 'rpc_method')


class MethodPredicate(object):
    def __init__(self, val, config):
        self.method = val

    def text(self):
        return 'jsonrpc method = %s' % self.method

    phash = text

    def __call__(self, context, request):
        # we need to explicitly return False here, so pyramid doesn't try to
        # execute our view directly. We need our main handler to execute things
        return getattr(request, 'rpc_method') == self.method


def add_jsonrpc_method(config, view, **kwargs):
    # pop the method name
    method = kwargs.pop('method', None)

    if method is None:
        raise ConfigurationError(
            'Cannot register a JSON-RPC method without specifying the '
            '"method"')

    # we define custom predicate, to enable to detect conflicting methods,
    # those predicates are kind of "translation" from the decorator variables
    # to internal predicates names

    kwargs['jsonrpc_method'] = method

    # register our view into global view store for validation
    config.registry.jsonrpc_methods[method] = view

    # we're using our main request_view handler, here, so each method
    # has a unified handler for itself
    config.add_view(request_view, route_name='apiv2', **kwargs)


class jsonrpc_method(object):
    """
    decorator that works similar to @add_view_config decorator,
    but tailored for our JSON RPC
    """

    venusian = venusian  # for testing injection

    def __init__(self, method=None, **kwargs):
        self.method = method
        self.kwargs = kwargs

    def __call__(self, wrapped):
        kwargs = self.kwargs.copy()
        kwargs['method'] = self.method or wrapped.__name__
        depth = kwargs.pop('_depth', 0)

        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_jsonrpc_method(view=ob, **kwargs)

        info = venusian.attach(wrapped, callback, category='pyramid',
                               depth=depth + 1)
        if info.scope == 'class':
            # ensure that attr is set if decorating a class method
            kwargs.setdefault('attr', wrapped.__name__)

        kwargs['_info'] = info.codeinfo  # fbo action_method
        return wrapped


class jsonrpc_deprecated_method(object):
    """
    Marks method as deprecated, adds log.warning, and inject special key to
    the request variable to mark method as deprecated.
    Also injects special docstring that extract_docs will catch to mark
    method as deprecated.

    :param use_method: specify which method should be used instead of
        the decorated one

    Use like::

        @jsonrpc_method()
        @jsonrpc_deprecated_method(use_method='new_func', deprecated_at_version='3.0.0')
        def old_func(request, apiuser, arg1, arg2):
            ...
    """

    def __init__(self, use_method, deprecated_at_version):
        self.use_method = use_method
        self.deprecated_at_version = deprecated_at_version
        self.deprecated_msg = ''

    def __call__(self, func):
        self.deprecated_msg = 'Please use method `{method}` instead.'.format(
            method=self.use_method)

        docstring = """\n
        .. deprecated:: {version}

           {deprecation_message}

        {original_docstring}
        """
        func.__doc__ = docstring.format(
            version=self.deprecated_at_version,
            deprecation_message=self.deprecated_msg,
            original_docstring=func.__doc__)
        return decorator.decorator(self.__wrapper, func)

    def __wrapper(self, func, *fargs, **fkwargs):
        log.warning('DEPRECATED API CALL on function %s, please '
                    'use `%s` instead', func, self.use_method)
        # alter function docstring to mark as deprecated, this is picked up
        # via fabric file that generates API DOC.
        result = func(*fargs, **fkwargs)

        request = fargs[0]
        request.rpc_deprecation = 'DEPRECATED METHOD ' + self.deprecated_msg
        return result


def includeme(config):
    plugin_module = 'rhodecode.api'
    plugin_settings = get_plugin_settings(
        plugin_module, config.registry.settings)

    if not hasattr(config.registry, 'jsonrpc_methods'):
        config.registry.jsonrpc_methods = {}

    # match filter by given method only
    config.add_view_predicate(
        'jsonrpc_method', MethodPredicate)

    config.add_renderer(DEFAULT_RENDERER, ExtJsonRenderer(
        serializer=json.dumps, indent=4))
    config.add_directive('add_jsonrpc_method', add_jsonrpc_method)

    config.add_route_predicate(
        'jsonrpc_call', RoutePredicate)

    config.add_route(
        'apiv2', plugin_settings.get('url', DEFAULT_URL), jsonrpc_call=True)

    config.scan(plugin_module, ignore='rhodecode.api.tests')
    # register some exception handling view
    config.add_view(exception_view, context=JSONRPCBaseError)
    config.add_view_predicate('jsonrpc_method_not_found', NotFoundPredicate)
    config.add_notfound_view(exception_view, jsonrpc_method_not_found=True)
