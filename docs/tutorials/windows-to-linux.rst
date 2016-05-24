Moving From Windows to Linux
============================

If you are moving from a Windows server to a Linux server, especially from
running an older version of |RCE| pre 2.x, use the following information to
successfully migrate your instances and database.

Overview
--------

* Install |RCC| on your Linux server, use the
  :ref:`RhodeCode Control Docs <control:rcc>` to guide you through this.
* Copy your |repos| directory to the Linux server.
* Copy your original :file:`rhodecode.ini` file to the Linux server, named
  :file:`production.ini` in older versions, and make a minor edit to
  point to the copied database.
* Copy your original instance database and update Windows paths to Linux
  paths pointing to your |repos| directory.
* Use |RCC| to import and upgrade your |RCE| instance, using the copied and
  edited file and database.

Pre-requisites
--------------

* For MySQL, do not use `localhost` in the database connection string of the
  :file:`rhodecode.ini` file.
* InnoDB must be the database tables engine.
* Contact |RC| for a new licence Key/Token pair. If you don't, a trial licence
  will be applied so you are not locked out of the upgraded instance.

You can find the specific instructions to carry out these pre-requisite steps
in the :ref:`RhodeCode Control upgrade <control:rce-upgrade-2x>` docs.

Configuration File Update
-------------------------

Configure the copied :file:`rhodecode.ini` file to connect to your copied
database. Use the following steps:

1. Open the copied :file:`rhodecode.ini` file.
2. When you open the file, find the database configuration section,
   and use the below example to change the connection details:

.. code-block:: ini

    #########################################################
    ### DB CONFIGS - EACH DB WILL HAVE IT'S OWN CONFIG    ###
    #########################################################

    # Point to copied DB
    sqlalchemy.db1.url = postgresql://postgres:qwe@localhost/rhodecode.db.copy
    sqlalchemy.db1.url = mysql://root:qweqwe@127.0.0.1/rhodecode.db.copy

Database Update
---------------

Update the Windows paths in the ``rhodecode.rhodecode_ui`` database tables.
To do this log into the database and reset the file paths to
Unix format. One login option is to use iShell, see usage examples in the
:ref:`rhodecode-reset-ref` section.

.. code-block:: python

    In [28]: from rhodecode.model.settings import SettingsModel
    In [29]: paths = SettingsModel().get_ui_by_section('paths')
    In [30]: paths[0].value = '/home/user/repos'
    In [32]: Session().add(paths[0])
    In [33]: Session().commit()

Import and Upgrade
------------------

Once you have made your changes, use |RCC| to import and upgrade your |RCE|
instance to the latest version.

.. code-block:: bash

    # Import original instance as explained above
    $ rccontrol import Enterprise path/to/rhodecode.ini

    # Install a VCS Server as explained above
    $ rccontrol install VCSServer

    # Check the status of them
    $ rccontrol status

     - NAME: enterprise-1
     - STATUS: RUNNING
     - TYPE: Enterprise
     - VERSION: 1.5.0
     - URL: http://127.0.0.1:10000

     - NAME: vcsserver-1
     - STATUS: RUNNING
     - TYPE: VCSServer
     - VERSION: 3.5.0
     - URL: http://127.0.0.1:10001

    # Upgrade from version 1.5.0 to 3.5.0
    $ rccontrol upgrade enterprise-1 --version 3.5.0

    Checking for available update for enterprise-1 @ 1.5.0
    Stopped enterprise-1
    Initiating upgrade to version 3.5.0
    ...
    ****************************************
    *** UPGRADE TO VERSION 45 SUCCESSFUL ***
    ****************************************

    Note that RCE 3.x requires a new license please contact support@rhodecode.com

    Upgrade of RhodeCode Enterprise successful.
    Auto starting enterprise-1

Post Migration Tasks
--------------------

* From the |RCE| :menuselection:`Admin --> Settings --> VCS` page, check that
  the :guilabel:`Repositories Location` is correctly pointing to your |repos|.
* Remap and rescan |repos| so that the new instance picks them up, see
  :ref:`remap-rescan`.
