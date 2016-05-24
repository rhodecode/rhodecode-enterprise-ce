.. _authentication-ref:

Authentication Options
======================

|RCE| provides a built in authentication plugin
``rhodecode.lib.auth_rhodecode``. This is enabled by default and accessed
through the administrative interface. Additionally,
|RCE| provides a Pluggable Authentication System (PAS). This gives the
administrator greater control over how users authenticate with the system.

.. important::

  You can disable the built in |RCM| authentication plugin
  ``rhodecode.lib.auth_rhodecode`` and force all authentication to go
  through your authentication plugin. However, if you do this,
  and your external authentication tools fails, you will be unable to
  access |RCM|.

|RCM| comes with the following user authentication management plugins:

.. only:: latex

    * :ref:`config-ldap-ref`
    * :ref:`config-pam-ref`
    * :ref:`config-crowd-ref`
    * :ref:`config-token-ref`

.. toctree::

    ldap-config-steps
    crowd-auth
    pam-auth
    token-auth
    ssh-connection


