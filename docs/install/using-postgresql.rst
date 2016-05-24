.. _install-postgresql-database:

PostgreSQL
----------

To use a PostgreSQL database you should install and configurevthe database
before installing |RCV|. This is becausevduring |RCV| installation you will
setup a connection to your PostgreSQL database. To work with PostgreSQL,
use the following steps:

1. Depending on your |os|, install avPostgreSQL database following the
   appropriate instructions from the `PostgreSQL website`_.
2. Configure the database with a username and password which you will use
   with |RCV|.
3. Install |RCV|, and during installation select PostgreSQL as your database.
4. Enter the following information to during the database setup:

   * Your network IP Address
   * The port number for MySQL access. The default MySQL port is ``5434``
   * Your database username
   * Your database password
   * A new database name

.. _PostgreSQL website: http://www.postgresql.org/
