.. _permissions-info-anon-ref:

Anonymous Users
---------------

By default, |RCM| provides |repo| access for registered users only. It can be
configured to be **world-open** in terms of read and write permissions. This
configuration is called "Anonymous Access" and allows |RCM| to be used as a
public hub where unregistered users have access to your |repos|.

Anonymous access is useful for open source projects, universities,
or if running inside a restricted internal corporate network to serve
documents to all employees. Anonymous users get the default user permission
settings that are applied across the whole |RCM| system.

To enable anonymous access to your |repos|, use the following steps:

1. From the |RCM| interface, select :menuselection:`Admin --> Permissions`.
2. On the Application tab, check the :guilabel:`Allow anonymous access` box.
3. Select :guilabel:`Save`.
4. To set the anonymous user access permissions, which are based on the
   default user settings, see :ref:`permissions-default-ref`.
