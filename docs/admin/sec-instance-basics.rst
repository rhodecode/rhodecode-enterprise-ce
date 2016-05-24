.. _instance-basics:

3 Basic User Security Steps
===========================

By implementing the following user configuration tasks, you will help to
secure your |RCE| instances.


Define the Instance Wide Default User
-------------------------------------

The default user settings are applied across the whole instance. You should
define the default user so that newly created users immediately have
permission settings attached to their profile. For more information about
defining the default user settings, see the :ref:`default-perms` section.

Configure Specific User Groups
------------------------------

By defining user groups, it allows you to put users into them and
have the group permissions applied to their profile. For more information about
defining the default user settings, see the :ref:`user-admin-set` section.

Define the Default User in Each Group
-------------------------------------

Apart from the system wide user permissions, each user group can apply its
settings to the default user permissions within the scope of the group. To
set the default user's permissions inside a user group, see the
:ref:`permissions-info-repo-group-access` section.
