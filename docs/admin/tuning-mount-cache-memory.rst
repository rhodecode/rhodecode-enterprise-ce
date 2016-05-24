.. _data-mem:

Mount Cache Folders To Memory
-----------------------------

To increase the performance of folders containing cache data, you can mount
them to memory. The following folders specified in the :file:`rhodecode.ini`
file would benefit from this.

.. code-block:: ini

    cache_dir = %(here)s/data
    search.location = %(here)s/data/index

Use the following Ubuntu example to mount these to memory, or see your
particular |os| instructions. The expected performance benefit is
approximately 5%. You should ensure you allocate an adequate amount of memory
depending on your available resources.

.. code-block:: bash

    # mount to memory with 2GB limit and 755 write permissions
    mount -t tmpfs -o size=2G,mode=0755 tmpfs /home/user/.rccontrol/enterprise-1/data
    mount -t tmpfs -o size=2G,mode=0755 tmpfs /home/user/.rccontrol/enterprise-1/data/index

.. _move-tmp:

Move ``tmp`` to TMPFS
---------------------

|RCE| components heavily use the :file:`/tmp` folder, so moving your
:file:`/tmp` folder into to a RAM-based TMPS can lead to a noticeable
performance boost.

.. code-block:: bash

    # mount tmp to memory with 2GB limit and 755 write permissions
    mount -t tmpfs -o size=2G,mode=0755 tmpfs /tmp

For more information about TMPFS, see the documentation `here`_.

.. _here: https://wiki.archlinux.org/index.php/Tmpfs
