.. _scale-horizontal:

Scale Horizontally
------------------

Horizontal scaling means adding more machines or workers into your pool of
resources. Horizontally scaling |RCE| gives a huge performance increase,
especially under large traffic scenarios with a high number of requests. This
is very beneficial when |RCE| is serving many users simultaneously,
or if continuous integration servers are automatically pulling and pushing code.

To horizontally scale |RCE| you should use the following steps:

1. In the :file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file,
   set ``instance_id = *``. This enables |RCE| to use multiple nodes.
2. Define the number of worker threads using the formula
   :math:`(2 * Cores) + 1`. For example 4 CPU cores would lead to
   :math:`(2 * 4) + 1 = 9` workers. In some cases it's ok to increase number of
   workers even beyond this formula. Generally the more workers, the more
   simultaneous connections the system can handle.

It is recommended to create another dedicated |RCE| instance to handle
traffic from build farms or continuous integration servers.

.. note::

   You should configure your load balancing accordingly. We recommend writing
   load balancing rules that will separate regular user traffic from
   automated process traffic like continuous servers or build bots.

If you scale across different machines, each |RCE| instance needs to store
its data on a shared disk, preferably together with your repositories. This
data directory contains template caches, a whoosh index,
and is used for task locking to ensure safety across multiple instances. To
do this, set the following properties in the
:file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file to set
the shared location across all |RCE| instances.

.. code-block:: ini

         cache_dir = /file/path               # set to shared directory location
         search.location = /file/path               # set to shared directory location
         beaker.cache.data_dir = /file/path   # set to shared directory location
         beaker.cache.lock_dir = /file/path   # set to shared directory location

.. note::

     If Celery is used on each instance then you should run separate Celery
     instances, but the message broker should be the same for all of them.
     This excludes one RabbitMQ shared server.

