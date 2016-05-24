.. _cache-size:

Increase Cache Size
-------------------

When managing hundreds of |repos| from the main |RCE| interface the system
can become slow when the cache expires. Increasing the cache expiration
option improves the response times of the main user interface.
To increase your cache size, change the following default value in the
:file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file. The value
is specified in seconds.

.. code-block:: ini

      beaker.cache.long_term.expire=3600  # day (86400) week (604800)

.. note:: The |RCE| cache automatically expires for changed |repos|.
