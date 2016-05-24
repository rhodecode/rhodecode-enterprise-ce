.. _repo-locking:

Repository Locking
------------------

Repository locking means that when a user pulls from a |repo|,
only a push by that user will unlock it. This allows an
Admin to pull from a |repo| and ensure that no changes can be introduced. You
need Admin access to the |repo| to enable
|repo| locking. To enable |repo| locking, use the following steps.

1. From the |RCE| interface, select :menuselection:`Admin --> Repositories`,
   then :guilabel:`Edit` beside the |repo| you wish to lock.
2. From the left-hand pane, select
   :menuselection:`Advanced --> Lock Repository`