.. _dev-setup:

===================
 Development setup
===================


RhodeCode Enterprise runs inside a Nix managed environment. This ensures build
environment dependencies are correctly declared and installed during setup.
It also enables atomic upgrades, rollbacks, and multiple instances of RhodeCode
Enterprise running with isolation.

To set up RhodeCode Enterprise inside the Nix environment, use the following steps:



Setup Nix Package Manager
-------------------------

To install the Nix Package Manager, please run::

   $ curl https://nixos.org/nix/install | sh

or go to https://nixos.org/nix/ and follow the installation instructions.
Once this is correctly set up on your system, you should be able to use the
following commands:

* `nix-env`

* `nix-shell`


.. tip::

   Update your channels frequently by running ``nix-channel --upgrade``.


Switch nix to the latest STABLE channel
---------------------------------------

run::

   nix-channel --add https://nixos.org/channels/nixos-16.03 nixpkgs

Followed by::

   nix-channel --update


Clone the required repositories
-------------------------------

After Nix is set up, clone the RhodeCode Enterprise Community Edition and
RhodeCode VCSServer repositories into the same directory.
To do this, use the following example::

    mkdir rhodecode-develop && cd rhodecode-develop
    hg clone https://code.rhodecode.com/rhodecode-enterprise-ce
    hg clone https://code.rhodecode.com/rhodecode-vcsserver

.. note::

   If you cannot clone the repository, please request read permissions
   via support@rhodecode.com



Enter the Development Shell
---------------------------

The final step is to start the development shell. To do this, run the
following command from inside the cloned repository::

   cd ~/rhodecode-enterprise-ce
   nix-shell

.. note::

   On the first run, this will take a while to download and optionally compile
   a few things. The following runs will be faster. The development shell works
   fine on both MacOS and Linux platforms.



Creating a Development Configuration
------------------------------------

To create a development environment for RhodeCode Enterprise,
use the following steps:

1. Create a copy of `~/rhodecode-enterprise-ce/configs/development.ini`
2. Adjust the configuration settings to your needs

   .. note::

      It is recommended to use the name `dev.ini`.


Setup the Development Database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create a development database, use the following example. This is a one
time operation::

    paster setup-rhodecode dev.ini \
        --user=admin --password=secret \
        --email=admin@example.com \
        --repos=~/my_dev_repos


Compile CSS and JavaScript
^^^^^^^^^^^^^^^^^^^^^^^^^^

To use the application's frontend, you will need to compile the CSS and
JavaScript with Grunt. This is easily done from within the nix-shell using the
following command::

    make web-build

You will need to recompile following any changes made to the CSS or JavaScript
files.


Start the Development Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, set the `start.vcs_server` flag in the ``dev.ini`` file to true.
For example:

   .. code-block:: python

      ### VCS CONFIG ###
      ##################
      vcs.start_server = true
      vcs.server = localhost:9900
      vcs.server.log_level = debug

From the rhodecode-vcsserver directory, start the development server in another
nix-shell, using the following command::

      pserve configs/development_pyramid.ini http_port=9900

In the adjacent nix-shell which you created for your development server, you may
now start CE with the following command::

      rcserver dev.ini

You may also wish to use the option `--reload` with this command so that any
changes which you make in the code trigger an automatic refresh.


Run the Environment Tests
^^^^^^^^^^^^^^^^^^^^^^^^^

Please make sure that the tests are passing to verify that your environment is
set up correctly. RhodeCode uses py.test to run tests.
While your instance is running, start a new nix-shell and simply run
``make test`` to run the basic test suite.


Need Help?
^^^^^^^^^^

Join us on Slack via https://rhodecode.com/join or post questions in our
Community Portal at https://community.rhodecode.com
