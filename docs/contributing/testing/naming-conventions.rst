
====================
 Naming conventions
====================


Fixtures
========

We found so far a few patterns emerging in our py.test fixtures. The naming
conventions for those are documented on this page.


Utilities - ``_util``
---------------------

Used for fixtures which are used to ensure that the pre-conditions of the test
are met. Usually it does not matter so much for the test how they achieve
this. Most utilities will clean up automatically after themselves.

Use the suffix ``_util``.


Page objects - ``{route_name}_page``
------------------------------------

Used as abstractions of pages.

Use the suffix ``_page`` and if possible use the route name as the prefix.
