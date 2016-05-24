=======================
DB Schema and Migration
=======================

To create or alter tables in the database it's necessary to change a couple of
files, apart from configuring the settings pointing to the latest database
schema.


Database Model and ORM
----------------------

On ``rhodecode.model.db`` you will find the database definition of all tables and 
fields. Any fresh install database will be correctly created by the definitions 
here. So, any change to this files will affect the tests without having to change
any other file.

A second layer are the businness classes that are inside ``rhodecode.model``. 


Database Migration
------------------

Three files play a role when creating database migrations:

    * Database schema inside ``rhodecode.lib.dbmigrate``
    * Database version inside ``rhodecode.lib.dbmigrate`` 
    * Configuration ``__dbversion__`` at ``rhodecode.__init__``


Schema is a snapshot of the database version BEFORE the migration. So, it's
the initial state before any changes were added. The name convention is
the latest release version where the snapshot were created, and not the 
target version of this code.

Version is the method that will define how to UPGRADE/DOWNGRADE the database.

``rhodecode.__init__`` contains only a variable that defines up to which version of 
the database will be used to upgrade. Eg.: ``__dbversion__ = 45``


For examples on how to create those files, please see the existing code.


Migration Command
^^^^^^^^^^^^^^^^^

After you changed the database ORM and migration files, you can run::

   paster upgrade-db <ini-file> 

And the database will be upgraded up to the version defined in the ``__init__`` file.