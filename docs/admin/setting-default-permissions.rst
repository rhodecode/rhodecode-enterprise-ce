.. _permissions-default-ref:

Setting Default Permissions
---------------------------

Default permissions allow you to configure |RCM| so that when a new |repo|, user group,
or user is created their permissions are already defined. To set default permissions you need administrator
privileges. See the following sections for setting up your permissions system:

* :ref:`user-default-ref`
* :ref:`user-group-default-ref`
* :ref:`repo-default-ref`
* :ref:`repo-group-default-ref`

.. _user-default-ref:

Setting User defaults
^^^^^^^^^^^^^^^^^^^^^

To set default user permissions, use the following steps.

1. From the |RCM| interface, select :menuselection:`Admin --> Permissions`
2. Select the :guilabel:`Global` tab from the left-hand menu. The permissions
   set on this screen apply to users and user-groups across the whole instance.
3. Save your changes

.. _user-group-default-ref:

Setting User Group defaults
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To set default user group permissions, use the following steps.

1. From the |RCM| interface, select :menuselection:`Admin --> User groups`
2. Select :guilabel:`Permissions`, and configure the default user
   permissions. All users will get these permissions unless
   individually set.
3. Select :guilabel:`Global permissions`, and if you wish to configure
   non-standard behaviour, uncheck the
   :guilabel:`inherit from default settings` box and configure the desired
   permissions
4. Save your changes

.. _repo-default-ref:

Setting Repository defaults
^^^^^^^^^^^^^^^^^^^^^^^^^^^

To set default |repo| permissions, use the following steps.

1. From the |RCM| interface, select :menuselection:`Admin --> Permissions`
2. Select the :guilabel:`Object` tab from the left-hand menu and set the
   |perm| permissions
3. Save your changes

.. _repo-group-default-ref:

Setting Repository Group defaults
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To set default Repository Group permissions, use the following steps.

1. From the |RCM| interface, select :menuselection:`Admin --> Repository Groups`
2. Select :guilabel:`Edit` beside the |repo| group you wish to configure
3. On the left-hand pane select :guilabel:`Permissions`
4. Set the default permissions for all |repos| created in this group
5. Save your changes

.. |perm| replace:: :guilabel:`None, Read, Write, or Admin`
