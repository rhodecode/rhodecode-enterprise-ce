.. _mig-repos:

Migrating |repos|
-----------------

If you have installed |RCM| and have |repos| that you wish to migrate into
the system, use the following instructions.

1. On the |RCM| interface, check your |repo| storage location under
   :menuselection:`Admin --> Settings --> System Info`. For example,
   Storage location: /home/{username}/repos.

2. Copy the |repos| that you want |RCM| to manage to this location.
3. Remap and rescan the |repos|, see :ref:`remap-rescan`

.. important::

   Directories create |repo| groups inside |RCM|.

   Importing adds |RCM| git hooks to your |repos|.

   You should verify if custom ``.hg`` or ``.hgrc`` files inside
   repositories should be adjusted since |RCM| reads the content of them.
