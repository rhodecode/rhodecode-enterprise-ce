.. _rhodecode-database-ref:

Supported Databases
===================

.. important::

   We do not recommend using SQLite in a production environment. It is
   supported by |RCE| for evaluation purposes.

Database Overview
-----------------

Prior to installing |RCE| you should install and set up your database.
This means carrying out the following tasks:

1. Install the database software of your choice.
2. Using the relevant instructions, create a user on that database to use
   with |RCE|.
3. Create a database, granting that user read/write access.
4. During |RCE| installation you will be prompted for these user credentials,
   enter them where appropriate. These credentials will be what |RCE| uses
   to read/write from the database tables.

Version Differences
-------------------

|RCE| releases 2(Major).x(Minor).x(Bug Fix) and 3.x.x use different database
schemas. Therefore, if you wish to run multiple instances using one database,
you can only do so using the same Minor Release numbered versions.
Though Bug Fix updates rarely have a database change, it is recommended to use
identical |RCE| version numbers for multi-instance setups.

You can use the same database server to run multiple databases for differing
version numbers, but you will need separate databases for each |RCE| version on
that server. You can specify the database during installation, use the
following example to configure the correct one.

.. code-block:: bash

     Database type - [s]qlite, [m]ysql, [p]ostresql:
     PostgreSQL selected
     Database host [127.0.0.1]:
     Database port [5432]:
     Database username: rhodecode
     Database password: somepassword
     # Specify the database you with to use on that server
     # for the RCE instance you are installing
     Database name: example-db-name-for-2xx # The 2xx version database
     Database name: example-db-name-for-3xx # The 3xx version database

Supported Databases
-------------------

|RCM| supports the following databases. The recommended encoding is Unicode
UTF-8.

.. only:: latex

   * :ref:`install-sqlite-database`
   * :ref:`install-mysql-database`
   * :ref:`install-postgresql-database`

.. toctree::

   using-mysql
   using-postgresql
   using-sqllite
