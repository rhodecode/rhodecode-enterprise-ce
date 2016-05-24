.. _install-sqlite-database:

SQLite
------

.. important::

    We do not recommend using SQLite in a large development environment
    as it has an internal locking mechanism which can become a performance
    bottleneck when there are more than 5 concurrent users.

|RCM| installs SQLite as the default database if you do not specify another
during installation. SQLite is suitable for small teams,
projects with a low load, and evaluation purposes since it is built into
|RCM| and does not require any additional database server.

Using MySQL or PostgreSQL in an large setup gives you much greater
performance, and while migration tools exist to move from one database type
to another, it is better to get it right first time and to immediately use
MySQL or PostgreSQL when you deploy |RCM| in a production environment.

Migrating From SQLite to PostgreSQL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you started working with SQLite and now need to migrate your database
to PostgreSQL, you can contact support@rhodecode.com for some help. We have a
set of scripts that enable SQLite to PostgreSQL migration. These scripts have
been tested, and work with PostgreSQL 9.1+.

.. note::

    There are no SQLite to MySQL or MariaDB scripts available.
