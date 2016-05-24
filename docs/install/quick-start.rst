.. _quick-start:

Quick Start Guide
=================

.. important::

    These are quick start instructions. To optimize your |RCE|,
    |RCC|, and |RCT| usage, read the more detailed instructions in our guides.
    For detailed installation instructions, see
    :ref:`RhodeCode Control Documentation <control:rcc>`

.. tip::

   If using a non-SQLite database, install and configure the database, create
   a new user, and grant permissions. You will be prompted for this user's
   credentials during |RCE| installation. See the relevant database
   documentation for more details.

To get |RCM| up and running, run through the below steps:

1. Download the latest |RCC| installer from your `rhodecode.com`_ profile
   page. If you don't have an account, sign up at `rhodecode.com/register`_.
2. Run the |RCC| installer and accept the End User Licence using the
   following example:

.. code-block:: bash

    $ chmod 755 RhodeCode-installer-linux-*
    $ ./RhodeCode-installer-linux-*

3. Install a VCS Server, and configure it to start at boot.

.. code-block:: bash

    $ rccontrol install VCSServer

    Agree to the licence agreement? [y/N]: y
    IP to start the server on [127.0.0.1]:
    Port for the server to start [10005]:
    Creating new instance: vcsserver-1
    Installing RhodeCode VCSServer
    Configuring RhodeCode VCS Server ...
    Supervisord state is: RUNNING
    Added process group vcsserver-1


4. Install |RCE|. If using MySQL or PostgreSQL, during installation you'll be
   asked for your database credentials, so have them at hand. You don't need
   any for SQLite.

.. code-block:: bash
   :emphasize-lines: 11-16

    $ rccontrol install Enterprise

    Username [admin]: username
    Password (min 6 chars):
    Repeat for confirmation:
    Email: your@mail.com
    Respositories location [/home/brian/repos]:
    IP to start the Enterprise server on [127.0.0.1]:
    Port for the Enterprise server to use [10004]:
    Database type - [s]qlite, [m]ysql, [p]ostresql:
    PostgreSQL selected
    Database host [127.0.0.1]:
    Database port [5432]:
    Database username: db-user-name
    Database password: somepassword
    Database name: example-db-name

5. Check the status of your installation. You |RCE| instance runs on the URL
   displayed in the status message.

.. code-block:: bash

    $ rccontrol status

    - NAME: enterprise-1
    - STATUS: RUNNING
    - TYPE: Enterprise
    - VERSION: 3.3.0
    - URL: http://127.0.0.1:10003

    - NAME: vcsserver-1
    - STATUS: RUNNING
    - TYPE: VCSServer
    - VERSION: 3.3.0
    - URL: http://127.0.0.1:10001

.. note::

   Recommended post quick start install instructions:

   * Read the documentation
   * Carry out the :ref:`rhodecode-post-instal-ref`
   * Set up :ref:`indexing-ref`
   * Familiarise yourself with the :ref:`rhodecode-admin-ref` section.

.. _rhodecode.com/download/: https://rhodecode.com/download/
.. _rhodecode.com: https://rhodecode.com/
.. _rhodecode.com/register: https://rhodecode.com/register/
