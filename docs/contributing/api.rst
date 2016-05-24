
=====
 API
=====



Naming conventions
==================

We keep the calls in the form ``{verb}_{noun}``.



Change and Deprecation
======================

API deprecation is documented in the section :ref:`deprecated` together with
other notes about deprecated parts of the application.


Deprecated API calls
--------------------

- Make sure to add them into the section :ref:`deprecated`.

- Use `deprecated` inside of the call docstring to make our users aware of the
  deprecation::

    .. deprecated:: 1.2.3

       Use `new_call_name` instead to fetch this information.

- Make sure to log on level `logging.WARNING` a message that the API call or
  specific parameters are deprecated.

- If possible return deprecation information inside of the result from the API
  call. Use the attribute `_warning_` to contain a message.


Changed API calls
-----------------

- If the change is significant, consider to use `versionchanged` in the
  docstring::

    .. versionchanged:: 1.2.3

       Optional explanation if reasonable.


Added API calls
---------------

- Use `versionadded` to document since which version this API call is
  available::

    .. versionadded:: 1.2.3

       Optional explanation if reasonable.
