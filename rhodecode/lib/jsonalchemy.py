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

import collections

import sqlalchemy
from sqlalchemy import UnicodeText
from sqlalchemy.ext.mutable import Mutable

from rhodecode.lib.ext_json import json


class JsonRaw(unicode):
    """
    Allows interacting with a JSON types field using a raw string.

    For example::
        db_instance = JsonTable()
        db_instance.enabled = True
        db_instance.json_data = JsonRaw('{"a": 4}')

    This will bypass serialization/checks, and allow storing
    raw values
    """
    pass


# Set this to the standard dict if Order is not required
DictClass = collections.OrderedDict


class JSONEncodedObj(sqlalchemy.types.TypeDecorator):
    """
    Represents an immutable structure as a json-encoded string.

    If default is, for example, a dict, then a NULL value in the
    database will be exposed as an empty dict.
    """

    impl = UnicodeText
    safe = True

    def __init__(self, *args, **kwargs):
        self.default = kwargs.pop('default', None)
        self.safe = kwargs.pop('safe_json', self.safe)
        self.dialect_map = kwargs.pop('dialect_map', {})
        super(JSONEncodedObj, self).__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect):
        if dialect.name in self.dialect_map:
            return dialect.type_descriptor(self.dialect_map[dialect.name])
        return dialect.type_descriptor(self.impl)

    def process_bind_param(self, value, dialect):
        if isinstance(value, JsonRaw):
            value = value
        elif value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if self.default is not None and (not value or value == '""'):
            return self.default()

        if value is not None:
            try:
                value = json.loads(value, object_pairs_hook=DictClass)
            except Exception as e:
                if self.safe:
                    return self.default()
                else:
                    raise
        return value


class MutationObj(Mutable):
    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, dict) and not isinstance(value, MutationDict):
            return MutationDict.coerce(key, value)
        if isinstance(value, list) and not isinstance(value, MutationList):
            return MutationList.coerce(key, value)
        return value

    @classmethod
    def _listen_on_attribute(cls, attribute, coerce, parent_cls):
        key = attribute.key
        if parent_cls is not attribute.class_:
            return

        # rely on "propagate" here
        parent_cls = attribute.class_

        def load(state, *args):
            val = state.dict.get(key, None)
            if coerce:
                val = cls.coerce(key, val)
                state.dict[key] = val
            if isinstance(val, cls):
                val._parents[state.obj()] = key

        def set(target, value, oldvalue, initiator):
            if not isinstance(value, cls):
                value = cls.coerce(key, value)
            if isinstance(value, cls):
                value._parents[target.obj()] = key
            if isinstance(oldvalue, cls):
                oldvalue._parents.pop(target.obj(), None)
            return value

        def pickle(state, state_dict):
            val = state.dict.get(key, None)
            if isinstance(val, cls):
                if 'ext.mutable.values' not in state_dict:
                    state_dict['ext.mutable.values'] = []
                state_dict['ext.mutable.values'].append(val)

        def unpickle(state, state_dict):
            if 'ext.mutable.values' in state_dict:
                for val in state_dict['ext.mutable.values']:
                    val._parents[state.obj()] = key

        sqlalchemy.event.listen(parent_cls, 'load', load, raw=True,
                                propagate=True)
        sqlalchemy.event.listen(parent_cls, 'refresh', load, raw=True,
                                propagate=True)
        sqlalchemy.event.listen(parent_cls, 'pickle', pickle, raw=True,
                                propagate=True)
        sqlalchemy.event.listen(attribute, 'set', set, raw=True, retval=True,
                                propagate=True)
        sqlalchemy.event.listen(parent_cls, 'unpickle', unpickle, raw=True,
                                propagate=True)


class MutationDict(MutationObj, DictClass):
    @classmethod
    def coerce(cls, key, value):
        """Convert plain dictionary to MutationDict"""
        self = MutationDict(
            (k, MutationObj.coerce(key, v)) for (k, v) in value.items())
        self._key = key
        return self

    def __setitem__(self, key, value):
        # Due to the way OrderedDict works, this is called during __init__.
        # At this time we don't have a key set, but what is more, the value
        # being set has already been coerced. So special case this and skip.
        if hasattr(self, '_key'):
            value = MutationObj.coerce(self._key, value)
        DictClass.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        DictClass.__delitem__(self, key)
        self.changed()


class MutationList(MutationObj, list):
    @classmethod
    def coerce(cls, key, value):
        """Convert plain list to MutationList"""
        self = MutationList((MutationObj.coerce(key, v) for v in value))
        self._key = key
        return self

    def __setitem__(self, idx, value):
        list.__setitem__(self, idx, MutationObj.coerce(self._key, value))
        self.changed()

    def __setslice__(self, start, stop, values):
        list.__setslice__(self, start, stop,
                          (MutationObj.coerce(self._key, v) for v in values))
        self.changed()

    def __delitem__(self, idx):
        list.__delitem__(self, idx)
        self.changed()

    def __delslice__(self, start, stop):
        list.__delslice__(self, start, stop)
        self.changed()

    def append(self, value):
        list.append(self, MutationObj.coerce(self._key, value))
        self.changed()

    def insert(self, idx, value):
        list.insert(self, idx, MutationObj.coerce(self._key, value))
        self.changed()

    def extend(self, values):
        list.extend(self, (MutationObj.coerce(self._key, v) for v in values))
        self.changed()

    def pop(self, *args, **kw):
        value = list.pop(self, *args, **kw)
        self.changed()
        return value

    def remove(self, value):
        list.remove(self, value)
        self.changed()


def JsonType(impl=None, **kwargs):
    """
    Helper for using a mutation obj, it allows to use .with_variant easily.
    example::

        settings = Column('settings_json',
            MutationObj.as_mutable(
            JsonType(dialect_map=dict(mysql=UnicodeText(16384))))
    """

    if impl == 'list':
        return JSONEncodedObj(default=list, **kwargs)
    elif impl == 'dict':
        return JSONEncodedObj(default=DictClass, **kwargs)
    else:
        return JSONEncodedObj(**kwargs)


JSON = MutationObj.as_mutable(JsonType())
"""
A type to encode/decode JSON on the fly

sqltype is the string type for the underlying DB column::

    Column(JSON) (defaults to UnicodeText)
"""

JSONDict = MutationObj.as_mutable(JsonType('dict'))
"""
A type to encode/decode JSON dictionaries on the fly
"""

JSONList = MutationObj.as_mutable(JsonType('list'))
"""
A type to encode/decode JSON lists` on the fly
"""
