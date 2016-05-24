.. _ssh-connection:

SSH Connection
--------------

If you wish to connect to your Git or Mercurial |repos| using SSH, use the
following instructions.

.. note::

   SSH access with full |RCE| permissions will require an Admin |authtoken|.

   You need to install the |RC| SSH tool on the server which is running
   the |RCE| instance.

1. Gather the following information about the instance you wish to connect to:

   * *Hostname*: Use the ``rccontrol status`` command to view instance details.
   * *API key*: From the |RCE|, go to
     :menuselection:`username --> My Account --> Auth Tokens`
   * *Configuration file*: Identify the configuration file for that instance,
     the default is :file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini`
   * Identify which |git| and |hg| packages your |RCM| instance is using.

       * For |git|, see
         :menuselection:`Admin --> Settings --> System Info`
       * For |hg|, use the ``which hg`` command.

2. Clone the |RC| SSH script,
   ``hg clone https://code.rhodecode.com/rhodecode-ssh``
3. Copy the ``sshwrapper.sample.ini``, and save it as ``sshwrapper.ini``
4. Configure the :file:`sshwrapper.ini` file using the following example:

.. code-block:: ini

    [api]
    host=http://localhost:10005
    key=24a67076d69c84670132f55166ac79d1faafd660

    [shell]
    shell=/bin/bash -l

    [vcs]
    root=/path/to/repos/

    [rhodecode]
    config=/home/user/.rccontrol/enterprise-3/rhodecode.ini

    [vcs:hg]
    path=/usr/bin/hg

    # should be a base dir for all git binaries, i.e. not ../bin/git
    [vcs:git]
    path=/usr/bin

    [keys]
    path=/home/user/.ssh/authorized_keys

5. Add the public key to your |RCE| instance server using the
   :file:`addkey.py` script. This script automatically creates
   the :file:`authorized_keys` file which was specified in your
   :file:`sshwrapper.ini` configuration. Use the following example:

.. code-block:: bash

   $ ./addkey.py --user username --shell --key /home/username/.ssh/id_rsa.pub

.. important::

   To give SSH access to all users, you will need to maintain
   each users |authtoken| in the :file:`authorized_keys` file.

6. Connect to your server using SSH from your local machine.

.. code-block:: bash

    $ ssh user@localhost
    Enter passphrase for key '/home/username/.ssh/id_rsa':

If you need to manually configure the ``authorized_keys`` file,
add a line for each key using the following example:

.. code-block:: vim

   command="/home/user/.rhodecode-ssh/sshwrapper.py --user username --shell",
   no-port-forwarding,no-X11-forwarding,no-agent-forwarding ssh-rsa yourpublickey

.. tip::

   Best practice would be to create a special SSH user account with each
   users |authtoken| attached.

   |RCE| will manage the user permissions based on the |authtoken| supplied.
   This would allow you to immediately revoke all SSH access by removing one
   user from your server if you needed to.

See the following command line example of setting this up. These steps
take place on the server.

.. code-block:: bash

    # On the RhodeCode Enterprise server
    # set up user and clone SSH tool
    $ sudo adduser testuser
    $ sudo su - testuser
    $ hg clone https://code.rhodecode.com/rhodecode-ssh
    $ cd rhodecode-ssh

    # Copy and modify the sshwrapper.ini as explained in step 4
    $ cp sshwrapper.sample.ini sshwrapper.ini

    $ cd ~
    $ mkdir .ssh
    $ touch .ssh/authorized_keys

    # copy your ssh public key, id_rsa.pub, from your local machine
    # to the server. We’ll use it in the next step

    $ python addkey.py --user testuser --shell --key /path/to/id_rsa.pub

    # Note: testssh - user on the rhodecode instance
    $ chmod 755 sshwrapper.py

Test the connection from your local machine using the following example:

.. code-block:: bash

    # Test connection using the ssh command from the local machine
    $ ssh testuser@my-server.example.com
