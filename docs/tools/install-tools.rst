.. _install-tools:

|RCT| Installation
------------------

As of |RCE| 3.4.1 |RCT| is installed automatically on the server with |RCE|. You
do not need to install |RCT| on the server, but you will need to install them
on machines that need remote access. The tools are linked to the instance
folder, for example :file:`~/.rccontrol/{instance-id}/profile/bin`

You can list the available tools using the following example, and the valid
tools options are those which correspond with those in the :ref:`rc-tools`
section.

.. code-block:: bash

    $ ls ~/.rccontrol/enterprise-4/profile/bin/

    gen_js_i18n    rhodecode-cleanup-gists   rhodecode-tools  svnrdump
    gen_js_routes  rhodecode-cleanup-repos   supervisorctl    svnserve
    git            rhodecode-config          supervisord      svnsync
    gunicorn       rhodecode-extensions      svn              svnversion
    hg             rhodecode-gist            svnadmin         vcsserver
    paster         rhodecode-index           svndumpfilter
    rcserver       rhodecode-list-instances  svnlook
    rhodecode-api  rhodecode-setup-config    svnmucc

You can then use the tools as described in the :ref:`rc-tools` section using the
following example:

.. code-block:: bash

    # Running the indexer
    $ ~/.rccontrol/enterprise-1/profile/bin/rhodecode-index \
        --instance-name=enterprise-1

    # Cleaning up gists
    $ ~/.rccontrol/enterprise-4/profile/bin/rhodecode-cleanup-gists \
        --instance-name=enterprise-4

    Scanning for gists in /home/brian/repos/.rc_gist_store...
    preparing to remove [1] found gists

Installing |RCT|
^^^^^^^^^^^^^^^^

|RCT| enable you to automate many of the most common |RCM| functions through
the API. Installing them on a local machine lets you carry out maintenance on
the server remotely. Once installed you can use them to index your |repos|
to setup full-text search, strip commits, or install |RC| Extensions for
additional functionality.

For more detailed instructions about using |RCT| for indexing and full-text
search, see :ref:`indexing-ref`

To install |RCT|, use the following steps:

1. Set up a ``virtualenv`` on your local machine, see virtualenv_ instructions
   here.
2. Install |RCT| using pip. Full url with token is available at https://rhodecode.com/u/#rhodecode-tools
   ``pip install -I https://dls.rhodecode.com/dls/<token>/rhodecode-tools/latest``


Once |RCT| is installed using these steps there are a few extra
configuration changes you can make. These are explained in more detail in the
:ref:`indexing-ref` section, and the :ref:`rc-tools` section.

.. code-block:: bash

    # Create a virtualenv
    brian@ubuntu:~$ virtualenv venv
    New python executable in venv/bin/python
    Installing setuptools, pip...done.

    # Activate the virtualenv
    brian@ubuntu:~$ . venv/bin/activate

    # Install RhodeCode Tools inside the virtualenv, full url with token is available at https://rhodecode.com/u/#rhodecode-tools
    $ pip install -I https://dls.rhodecode.com/dls/<token>/rhodecode-tools/latest

    # Check the installation
    $ rhodecode-tools --help

.. _virtualenv: https://virtualenv.pypa.io/en/latest/index.html

