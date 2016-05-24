.. _config-ldap-ref:

LDAP
----

|RCM| supports LDAP (Lightweight Directory Access Protocol) authentication.
All LDAP versions are supported, with the following |RCM| plugins managing each:

* For LDAPv3 use ``rhodecode.lib.auth_modules.auth_ldap_group``
* For older LDAP versions use ``rhodecode.lib.auth_modules.auth_ldap``

.. important::

   The email used with your |RCE| super-admin account needs to match the email
   address attached to your admin profile in LDAP. This is because
   within |RCE| the user email needs to be unique, and multiple users
   cannot share an email account.

   Likewise, if as an admin you also have a user account, the email address
   attached to the user account needs to be different.

LDAP Configuration Steps
^^^^^^^^^^^^^^^^^^^^^^^^

To configure |LDAP|, use the following steps:

1. From the |RCM| interface, select
   :menuselection:`Admin --> Authentication`
2. Enable the required plugin and select :guilabel:`Save`
3. Select the :guilabel:`Enabled` check box in the plugin configuration section
4. Add the required LDAP information and :guilabel:`Save`, for more details,
   see :ref:`config-ldap-examples`

For a more detailed description of LDAP objects, see :ref:`ldap-gloss-ref`:

.. _config-ldap-examples:

Example LDAP configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: bash

        # Auth Cache TTL
        3600
        # Host
        https://ldap1.server.com/ldap-admin/,https://ldap2.server.com/ldap-admin/
        # Port
        389
        # Account
        cn=admin,dc=rhodecode,dc=com
        # Password
        ldap-user-password
        # LDAP connection security
        LDAPS
        # Certificate checks level
        DEMAND
        # Base DN
        cn=Rufus Magillacuddy,ou=users,dc=rhodecode,dc=com
        # User Search Base
        ou=groups,ou=users
        # LDAP search filter
        (objectClass=person)
        # LDAP search scope
        SUBTREE
        # Login attribute
        rmagillacuddy
        # First Name Attribute
        Rufus
        # Last Name Attribute
        Magillacuddy
        # Email Attribute
        LDAP-Registered@email.ac
        # User Member of Attribute
        Organizational Role
        # Group search base
        cn=users,ou=groups,dc=rhodecode,dc=com
        # LDAP Group Search Filter
        (objectclass=posixGroup)
        # Group Name Attribute
        users
        # Group Member Of Attribute
        cn
        # Admin Groups
        admin,devops,qa

.. toctree::

   ldap-active-directory
   ldap-authentication
