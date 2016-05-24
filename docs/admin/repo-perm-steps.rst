.. _set-repo-perms:

Setting Repository Permissions
------------------------------

To set the permissions on an individual |repo|, use the following steps:

1. Open :menuselection:`Admin --> Repositories` and select
   :guilabel:`edit` beside the |repo| you wish to configure.
2. On the |repo| settings page you will see a number of tabs. Exploring these
   you will find the following main configuration options for a |repo|.
3. Once you make changes, select :guilabel:`Save`

* :guilabel:`Repository group`: Lets you to add a |repo| to a |repo| group.
* :guilabel:`Owner`: Lets you change the |repo| owner. Useful when users are
  moving roles within an organisation.
* :guilabel:`Enable automatic locking`: For more information,
  see :ref:`repo-locking`
* :guilabel:`User Access`: On the permissions tab you can add users,
  or user groups, and set the permissions each has for that |repo|.
* :guilabel:`Invalidate repository cache`: On the Caches tab you can delete
  the |repo| cache, sometimes needed when mirroring.

.. _set-repo-group-perms:

Setting Repository Group Permissions
------------------------------------

To set the permissions on a Repository Group, use the following steps:

1. Open :menuselection:`Admin --> Repository groups` and select
   :guilabel:`edit` beside the |repo| you wish to configure.
2. On the |repo| group settings page you will see a number of tabs. Exploring
   these you will find the following main configuration options:

* :guilabel:`Owner`: Lets you change the group owner. Useful when users are
  moving roles within an organisation.
* :guilabel:`Group parent`: Lets you add the |repo| group as a sub-group
  of a larger group, i.e. :guilabel:`QA-Repos >> QA-Repos-Berlin`
* :guilabel:`Enable automatic locking`: For more information,
  see :ref:`repo-locking`
* :guilabel:`User Access`: On the permissions tab you can add users,
  or user groups, and set the permissions each has for that |repo| group.
* :guilabel:`Add Child Group`: Allows you to add sub-repository-groups
  that will all share the same permissions.
