.. _multi-instance-setup:

Scaling |RCE| Using Multiple Instances
======================================

Running multiple instances of |RCE| from a single database can be used to
scale the application for the following deployment setups:

* Using dedicated Continuous Integrations instances.
* Locating instances closer to geographically dispersed development teams.
* Running production and testing instances, or failover instances on a
  different server.
* Running proxy read-only instances for pull operations.

If you wish to run multiple instances of |RCE| using a single database for
settings, use the following instructions to set this up. Before you get onto
multiple instances though, you should install |RCE|, and set
up your first instance as you see fit. You can see the full instructions here
:ref:`Installing RhodeCode Enterprise <control:rcc>`

Once you have configured your first instance, you can run additional instances
from the same database using the following steps:

1. Install a new instance of |RCE|, choosing SQLite as the database. It is
   important to choose SQLite, because this will not overwrite any other
   database settings you may have.

   Once the new instance is installed you need to update the licence token and
   database connection string in the
   :file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file.

.. code-block:: bash

   $ rccontrol install Enterprise

    Agree to the licence agreement? [y/N]: y
    Username [admin]: username
    Password (min 6 chars):
    Repeat for confirmation:
    Email: user@example.com
    Respositories location [/home/brian/repos]:
    IP to start the Enterprise server on [127.0.0.1]:
    Port for the Enterprise server to use [10000]:
    Database type - [s]qlite, [m]ysql, [p]ostresql: s

2. The licence token used on each new instance needs to be the token from your
   initial instance. This allows multiple instances to run the same licence key.

   To get the licence token, go to the |RCE| interface of your primary
   instance and select :menuselection:`admin --> setting --> license`. Then
   update the licence token setting in each new instance's
   :file:`rhodecode.ini` file.

.. code-block:: ini

    ## generated license token, goto license page in RhodeCode settings to get
    ## new token
    license_token = add-token-here

3. Update the database connection string in the
   :file:`rhodecode.ini` file to point to your database. For
   more information, see :ref:`config-database`.

.. code-block:: ini

    #########################################################
    ### DB CONFIGS - EACH DB WILL HAVE IT'S OWN CONFIG    ###
    #########################################################

    # Default SQLite config
    sqlalchemy.db1.url = sqlite:////home/user/.rccontrol/enterprise-1/rhodecode.db

    # Use this example for a PostgreSQL
    sqlalchemy.db1.url = postgresql://username:password@localhost/rhodecode

4. Restart your updated instance. Once restarted the new instance will read
   the licence key in the database and will function identically as the
   original instance.

.. code-block:: bash

   $ rccontrol restart enterprise-2

If you wish to add additional performance to your setup, see the
:ref:`rhodecode-tuning-ref` section.

Scaling Deployment Diagram
--------------------------

.. image:: ../images/scaling-diagrm.png
   :align: center
