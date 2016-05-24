.. _install-mysql-database:

MySQL or MariaDB
----------------

To use a MySQL or MariaDB database you should install and configure the
database before installing |RCM|. This is because during |RCM| installation
you will setup a connection to your MySQL or MariaDB database. To work with
either, use the following steps:

1. Depending on your |os|, install a MySQL or MariaDB database following the
   appropriate instructions from the `MySQL website`_ or `MariaDB website`_.
2. Configure the database with a username and password which you will use
   with |RCM|.
3. Install |RCM|, and during installation select MySQL as your database.
4. Enter the following information during the database setup:

   * Your network IP Address
   * The port number for MySQL or MariaDB access.
     The default port for both is ``3306``
   * Your database username
   * Your database password
   * A new database name

.. _MySQL website: http://www.mysql.com/
.. _MariaDB website: https://mariadb.com/
