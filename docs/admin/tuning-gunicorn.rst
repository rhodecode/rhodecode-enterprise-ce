.. _increase-gunicorn:

Increase Gunicorn Workers
-------------------------

.. important::

   If you increase the number of :term:`Gunicorn` workers, you also need to
   increase the threadpool size of the VCS Server. The recommended size is
   6 times the number of Gunicorn workers. To set this, see
   :ref:`vcs-server-config-file`.

|RCE| comes with `Gunicorn`_ packaged in its Nix environment. To improve
performance you can increase the number of workers. To do this, use the
following steps:

1. Open the :file:`home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file.
2. In the ``[server:main]`` section, increase the number of Gunicorn
   ``workers`` using the following formula :math:`(2 * Cores) + 1`.

.. code-block:: ini

    [server:main]
    host = 127.0.0.1
    port = 10002
    use = egg:gunicorn#main
    workers = 1
    threads = 1
    proc_name = RhodeCodeEnterprise
    worker_class = sync
    max_requests = 1000
    timeout = 3600

3. In the ``[app:main]`` section, set the ``instance_id`` property to ``*``.

.. code-block:: ini

    # In the [app:main] section
    [app:main]
    # You must set `instance_id = *`
    instance_id = *

4. Save your changes.
5. Restart your |RCE| instance, using the following command:

.. code-block:: bash

    $ rccontrol restart enterprise-1

If you scale across different machines, each |RCM| instance
needs to store its data on a shared disk, preferably together with your
|repos|. This data directory contains template caches, a whoosh index,
and is used for task locking to ensure safety across multiple instances.
To do this, set the following properties in the :file:`rhodecode.ini` file to
set the shared location across all |RCM| instances.

.. code-block:: ini

    cache_dir = /file/path           # set to shared location
    search.location = /file/path           # set to shared location

    ####################################
    ###         BEAKER CACHE        ####
    ####################################
    beaker.cache.data_dir = /file/path       # set to shared location
    beaker.cache.lock_dir = /file/path       # set to shared location



Gunicorn SSL support
--------------------


:term:`Gunicorn` wsgi server allows users to use HTTPS connection directly
without a need to use HTTP server like Nginx or Apache. To Configure
SSL support directly with :term:`Gunicorn` you need to simply add the key
and certificate paths to your configuration file.

1. Open the :file:`home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file.
2. In the ``[server:main]`` section, add two new variables
   called `certfile` and `keyfile`.

.. code-block:: ini

    [server:main]
    host = 127.0.0.1
    port = 10002
    use = egg:gunicorn#main
    workers = 1
    threads = 1
    proc_name = RhodeCodeEnterprise
    worker_class = sync
    max_requests = 1000
    timeout = 3600
    # adding ssl support
    certfile = /home/ssl/my_server_com.pem
    keyfile = /home/ssl/my_server_com.key

4. Save your changes.
5. Restart your |RCE| instance, using the following command:

.. code-block:: bash

    $ rccontrol restart enterprise-1

After this is enabled you can *only* access your instances via https://
protocol. Check out more docs here `Gunicorn SSL Docs`_


.. _Gunicorn: http://gunicorn.org/
.. _Gunicorn SSL Docs: http://docs.gunicorn.org/en/stable/settings.html#ssl
