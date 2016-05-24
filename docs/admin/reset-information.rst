.. _rhodecode-reset-ref:

Settings Management
-------------------

All |RCE| settings can be set from the user interface, but in the event that
it somehow becomes unavailable you can use ``ishell`` inside your |RCE|
``virtualenv`` to carry out emergency measures.

.. warning::

   Logging into the |RCE| database with ``iShell`` should only be done by an
   experienced and knowledgeable database administrator.

Reset Admin Account Privileges
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you accidentally remove your admin privileges from the admin account you
can restore them using ``ishell``. Use the following example to reset your
account permissions.

.. code-block:: bash

    # Open iShell from the terminal
    $ .rccontrol/enterprise-5/profile/bin/paster \
        ishell .rccontrol/enterprise-5/rhodecode.ini

.. code-block:: mysql

    # Use this example to change user permissions
    In [1]: adminuser = User.get_by_username('username')
    In [2]: adminuser.admin = True
    In [3]: Session.add(adminuser);Session().commit()
    In [4]: exit()

Set to read global ``.hgrc`` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, |RCE| does not read global ``hgrc`` files in
``/etc/mercurial/hgrc`` or ``/etc/mercurial/hgrc.d`` because it
can lead to issues. This is set in the ``rhodecode_ui`` table for which
there is no UI. If you need to edit this you can
manually change the settings using SQL statements with ``ishell``. Use the
following example to make changes to this table.

.. code-block:: bash

  # Open iShell from the terminal
  $ .rccontrol/enterprise-5/profile/bin/paster \
      ishell.rccontrol/enterprise-5/rhodecode.ini

.. code-block:: mysql

  # Use this example to enable global .hgrc access
  In [4]: new_option = RhodeCodeUi()
  In [5]: new_option.ui_section='web'
  In [6]: new_option.ui_key='allow_push'
  In [7]: new_option.ui_value='*'
  In [8]: Session().add(new_option);Session().commit()

Manually Reset Password
^^^^^^^^^^^^^^^^^^^^^^^

If you need to manually reset a user password, use the following steps.

1. Navigate to your |RCE| install location.
2. Run the interactive ``ishell`` prompt.
3. Set a new password.

Use the following code example to carry out these steps.

.. code-block:: bash

    # starts the ishell interactive prompt
    $ .rccontrol/enterprise-5/profile/bin/paster \
        ishell .rccontrol/enterprise-5/rhodecode.ini

.. code-block:: mysql

    from rhodecode.lib.auth import generate_auth_token
    from rhodecode.lib.auth import get_crypt_password

    # Enter the user name whose password you wish to change
    my_user = 'USERNAME'
    u = User.get_by_username(my_user)

    # If this fails then the user does not exist
    u.auth_token = generate_auth_token(my_user)

    # Set the new password
    u.password = get_crypt_password('PASSWORD')

    Session().add(u)
    Session().commit()
    exit
