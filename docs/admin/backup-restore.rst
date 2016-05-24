.. _backup-ref:

Backup and Restore
==================

*“The condition of any backup is unknown until a restore is attempted.”*
`Schrödinger's Backup`_

To snapshot an instance of |RCE|, and save its settings, you need to backup the
following parts of the system at the same time.

* The |repos| managed by the instance.
* The |RCE| database.
* Any configuration files or extensions that you've configured.

.. important::

   Ideally you should script all of these functions so that it creates a
   backup snapshot of your system at a particular timestamp and then run that
   script regularly.

Backup Details
--------------

To backup the relevant parts of |RCE| required to restore your system, use
the information in this section to identify what is important to you.

Repository Backup
^^^^^^^^^^^^^^^^^

To back up your |repos|, use the API to get a list of all |repos| managed,
and then clone them to your backup location.

Use the ``get_repos`` method to list all your managed |repos|,
and use the ``clone_uri`` information that is returned. See the :ref:`api`
for more information.

.. important::

   This will not work for |svn| |repos|. Currently the only way to back up
   your |svn| |repos| is to make a copy of them.

   It is also important to note, that you can only restore the |svn| |repos|
   using the same version as they were saved with.

Database Backup
^^^^^^^^^^^^^^^

The instance database contains all the |RCE| permissions settings,
and user management information. To backup your database,
export it using the following appropriate example, and then move it to your
backup location:

.. code-block:: bash

   # For MySQL DBs
   $ mysqldump -u <uname> -p <pass> db_name > mysql-db-backup

   # For PostgreSQL DBs
   $ pg_dump dbname > postgresql-db-backup

   # For SQLlite
   $ sqlite3 rhodecode.db ‘.dump’ > sqlite-db-backup


The default |RCE| SQLite database location is
:file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.db`

If running MySQL or PostgreSQL databases, you will have configured these
separately, for more information see :ref:`rhodecode-database-ref`

Configuration File Backup
^^^^^^^^^^^^^^^^^^^^^^^^^

Depending on your setup, you could have a number of configuration files that
should be backed up. You may have some, or all of the configuration files
listed in the :ref:`config-rce-files` section. Ideally you should back these
up at the same time as the database and |repos|.

Gist Backup
^^^^^^^^^^^

To backup the gists on your |RCE| instance you can use the ``get_users`` and
``get_gists`` API methods to fetch the gists for each user on the instance.

Extension Backups
^^^^^^^^^^^^^^^^^

You should also backup any extensions added in the
:file:`home/{user}/.rccontrol/{instance-id}/rcextensions` directory.

Full-text Search Backup
^^^^^^^^^^^^^^^^^^^^^^^

You may also have full text search set up, but the index can be rebuild from
re-imported |repos| if necessary. You will most likely want to backup your
:file:`mapping.ini` file if you've configured that. For more information, see
the :ref:`indexing-ref` section.

Restoration Steps
-----------------

To restore an instance of |RCE| from its backed up components, use the
following steps.

1. Install a new instance of |RCE|.
2. Once installed, configure the instance to use the backed up
   :file:`rhodecode.ini` file. Ensure this file points to the backed up
   database, see the :ref:`config-database` section.
3. Restart |RCE| and remap and rescan your |repos|, see the
   :ref:`remap-rescan` section.

Post Restoration Steps
^^^^^^^^^^^^^^^^^^^^^^

Once you have restored your |RCE| instance to basic functionality, you can
then work on restoring any specific setup changes you had made.

* To recreate the |RCE| index, use the backed up :file:`mapping.ini` file if
  you had made changes and rerun the indexer. See the
  :ref:`indexing-ref` section for details.
* To reconfigure any extensions, copy the backed up extensions into the
  :file:`/home/{user}/.rccontrol/{instance-id}/rcextensions` and also specify
  any custom hooks if necessary. See the :ref:`integrations-ref` section for
  details.

.. _Schrödinger's Backup: http://novabackup.novastor.com/blog/schrodingers-backup-good-bad-backup/
