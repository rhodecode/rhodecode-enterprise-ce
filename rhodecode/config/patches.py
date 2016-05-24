# -*- coding: utf-8 -*-

# Copyright (C) 2016-2016  RhodeCode GmbH
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
Compatibility patches.

Please keep the following principles in mind:

* Keep imports local, so that importing this module does not cause too many
  side effects by itself.

* Try to make patches idempotent, calling them multiple times should not do
  harm. If that is not possible, ensure that the second call explodes.

"""


def kombu_1_5_1_python_2_7_11():
    """
    Kombu 1.5.1 relies on a private method which got removed in Python 2.7.11.

    This patch adds the symbol to the module :mod:`uuid` and assigns the value
    ``None`` to it. This causes kombu to fall back to the public API of
    :mod:`uuid`.

    This patch can most probably be removed once celery and kombu are updated
    to more recent versions.
    """
    import uuid

    if not hasattr(uuid, '_uuid_generate_random'):
        uuid._uuid_generate_random = None


def inspect_getargspec():
    """
    Pyramid and Pylons rely on inspect.getargspec to lookup the signature of
    view functions. This is not compatible with cython, therefore we replace
    getargspec with a custom version.
    Code is inspired by the inspect module from Python-3.4
    """
    import inspect

    def _isCython(func):
        """
        Private helper that checks if a function is a cython function.
        """
        return func.__class__.__name__ == 'cython_function_or_method'

    def unwrap(func):
        """
        Get the object wrapped by *func*.

        Follows the chain of :attr:`__wrapped__` attributes returning the last
        object in the chain.

        *stop* is an optional callback accepting an object in the wrapper chain
        as its sole argument that allows the unwrapping to be terminated early
        if the callback returns a true value. If the callback never returns a
        true value, the last object in the chain is returned as usual. For
        example, :func:`signature` uses this to stop unwrapping if any object
        in the chain has a ``__signature__`` attribute defined.

        :exc:`ValueError` is raised if a cycle is encountered.
        """
        f = func  # remember the original func for error reporting
        memo = {id(f)}  # Memoise by id to tolerate non-hashable objects
        while hasattr(func, '__wrapped__'):
            func = func.__wrapped__
            id_func = id(func)
            if id_func in memo:
                raise ValueError('wrapper loop when unwrapping {!r}'.format(f))
            memo.add(id_func)
        return func

    def custom_getargspec(func):
        """
        Get the names and default values of a function's arguments.

        A tuple of four things is returned: (args, varargs, varkw, defaults).
        'args' is a list of the argument names (it may contain nested lists).
        'varargs' and 'varkw' are the names of the * and ** arguments or None.
        'defaults' is an n-tuple of the default values of the last n arguments.
        """

        func = unwrap(func)

        if inspect.ismethod(func):
            func = func.im_func
        if not inspect.isfunction(func):
            if not _isCython(func):
                raise TypeError('{!r} is not a Python or Cython function'
                                .format(func))
        args, varargs, varkw = inspect.getargs(func.func_code)
        return inspect.ArgSpec(args, varargs, varkw, func.func_defaults)

    inspect.getargspec = custom_getargspec
