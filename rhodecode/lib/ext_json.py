import datetime
import decimal
import functools

import simplejson as json

from rhodecode.lib.datelib import is_aware

try:
    import pylons
except ImportError:
    pylons = None

__all__ = ['json']


def _obj_dump(obj):
    """
    Custom function for dumping objects to JSON, if obj has __json__ attribute
    or method defined it will be used for serialization

    :param obj:
    """

    # See "Date Time String Format" in the ECMA-262 specification.
    # some code borrowed from django 1.4
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, datetime.datetime):
        r = obj.isoformat()
        if isinstance(obj.microsecond, (int, long)):
            r = r[:23] + r[26:]
        if r.endswith('+00:00'):
            r = r[:-6] + 'Z'
        return r
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, datetime.time):
        if is_aware(obj):
            raise TypeError("Time-zone aware times are not JSON serializable")
        r = obj.isoformat()
        if isinstance(obj.microsecond, (int, long)):
            r = r[:12]
        return r
    elif hasattr(obj, '__json__'):
        if callable(obj.__json__):
            return obj.__json__()
        else:
            return obj.__json__
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
    elif isinstance(obj, complex):
        return [obj.real, obj.imag]
    elif pylons and isinstance(obj, pylons.i18n.translation.LazyString):
        return obj.eval()
    else:
        raise TypeError(repr(obj) + " is not JSON serializable")


json.dumps = functools.partial(json.dumps, default=_obj_dump, use_decimal=False)
json.dump = functools.partial(json.dump, default=_obj_dump, use_decimal=False)

# alias for formatted json
formatted_json = functools.partial(json.dumps, indent=4, sort_keys=True)
