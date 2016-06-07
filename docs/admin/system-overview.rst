.. _system-overview-ref:

System Overview
===============

Latest Version
--------------

* |release| on Unix and Windows systems.

System Architecture
-------------------

The following diagram shows a typical production architecture.

.. image:: ../images/architecture-diagram.png
  :align: center

Supported Operating Systems
---------------------------

Linux
^^^^^

* Ubuntu 14.04
* CentOS 6.2 and 7
* Debian 7.8
* RedHat Fedora
* Arch Linux
* SUSE Linux

Windows
^^^^^^^

* Windows Vista Ultimate 64bit
* Windows 7 Ultimate 64bit
* Windows 8 Professional 64bit
* Windows 8.1 Enterprise 64bit
* Windows Server 2008 64bit
* Windows Server 2008-R2 64bit
* Windows Server 2012 64bit

Supported Databases
-------------------

* SQLite
* MySQL
* MariaDB
* PostgreSQL

Supported Browsers
------------------

* Chrome
* Safari
* Firefox
* Internet Explorer 10 & 11

System Requirements
-------------------

|RCM| performs best on machines with ultra-fast hard disks. Generally disk
performance is more important than CPU performance. In a corporate production
environment handling 1000s of users and |repos| you should deploy on a 12+
core 64GB RAM server. In short, the more RAM the better.


For example:

 - for team of 1 - 5 active users you can run on 1GB RAM machine with 1CPU
 - above 250 active users, |RCM| needs at least 8GB of memory.
   Number of CPUs is less important, but recommended to have at least 2-3 CPUs


.. _config-rce-files:

Configuration Files
-------------------

* :file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini`
* :file:`/home/{user}/.rccontrol/{instance-id}/mapping.ini`
* :file:`/home/{user}/.rccontrol/{vcsserver-id}/vcsserver.ini`
* :file:`/home/{user}/.rccontrol/supervisor/supervisord.ini`
* :file:`/home/{user}/.rccontrol.ini`
* :file:`/home/{user}/.rhoderc`
* :file:`/home/{user}/.rccontrol/cache/MANIFEST`

For more information, see the :ref:`config-files` section.

Log Files
---------

* :file:`/home/{user}/.rccontrol/{instance-id}/enterprise.log`
* :file:`/home/{user}/.rccontrol/{vcsserver-id}/vcsserver.log`
* :file:`/home/{user}/.rccontrol/supervisor/supervisord.log`
* :file:`/tmp/rccontrol.log`
* :file:`/tmp/rhodecode_tools.log`

Storage Files
-------------

* :file:`/home/{user}/.rccontrol/{instance-id}/data/index/{index-file.toc}`
* :file:`/home/{user}/repos/.rc_gist_store`
* :file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.db`
* :file:`/opt/rhodecode/store/{unique-hash}`

Default Repositories Location
-----------------------------

* :file:`/home/{user}/repos`

Connection Methods
------------------

* HTTPS
* SSH
* |RCM| API

Internationalization Support
----------------------------

Currently available in the following languages, see `Transifex`_ for the
latest details. If you want a new language added, please contact us. To
configure your language settings, see the :ref:`set-lang` section.

.. hlist::

  * Belorussian
  * Chinese
  * French
  * German
  * Italian
  * Japanese
  * Portuguese
  * Polish
  * Russian
  * Spanish

Licencing Information
---------------------

* See licencing information `here`_

Peer-to-peer Failover Support
-----------------------------

* Yes

Additional Binaries
-------------------

* Yes, see :ref:`rhodecode-nix-ref` for full details.

Remote Connectivity
-------------------

* Available

Executable Files
----------------

Windows: :file:`RhodeCode-installer-{version}.exe`

Deprecated Support
------------------

- Internet Explorer 8 support deprecated since version 3.7.0.
- Internet Explorer 9 support deprecated since version 3.8.0.

.. _here: https://rhodecode.com/licenses/
.. _Transifex: https://www.transifex.com/projects/p/RhodeCode/
