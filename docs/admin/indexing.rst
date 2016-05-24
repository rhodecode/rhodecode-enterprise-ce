.. _indexing-ref:

Full-text Search
----------------

By default |RCM| uses `Whoosh`_ to index |repos| and provide full-text search.
To run the indexer you need to use an |authtoken| with admin rights to all
|repos|.

To index new content added, you have the option to set the indexer up in a
number of ways, for example:

* Call the indexer via a cron job. We recommend running this nightly,
  unless you need everything indexed immediately.
* Set the indexer to infinitely loop and reindex as soon as it has run its
  cycle.
* Hook the indexer up with your CI server to reindex after each push.

The indexer works by indexing new commits added since the last run. If you
wish to build a brand new index from scratch each time,
use the ``force`` option in the configuration file.

.. important::

   You need to have |RCT| installed, see :ref:`install-tools`. Since |RCE|
   3.5.0 they are installed by default.

To set up indexing, use the following steps:

1. :ref:`config-rhoderc`, if running tools remotely.
2. :ref:`run-index`
3. :ref:`set-index`
4. :ref:`advanced-indexing`

.. _config-rhoderc:

Configure the ``.rhoderc`` File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

|RCT| uses the :file:`/home/{user}/.rhoderc` file for connection details
to |RCM| instances. If this file is not automatically created,
you can configure it using the following example. You need to configure the
details for each instance you want to index.

.. code-block:: bash

    # Check the instance details
    # of the instance you want to index
    $ rccontrol status

     - NAME: enterprise-1
     - STATUS: RUNNING
     - TYPE: Momentum
     - VERSION: 1.5.0
     - URL: http://127.0.0.1:10000

To get your API Token, on the |RCM| interface go to
:menuselection:`username --> My Account --> Auth tokens`

.. code-block:: ini

    # Configure .rhoderc with matching details
    # This allows the indexer to connect to the instance
    [instance:enterprise-1]
    api_host = http://127.0.0.1:10000
    api_key = <auth token goes here>
    repo_dir = /home/<username>/repos

.. _run-index:

Run the Indexer
^^^^^^^^^^^^^^^

Run the indexer using the following command, and specify the instance you
want to index:

.. code-block:: bash

   # From inside a virtualevv
   (venv)$ rhodecode-index --instance-name=enterprise-1

   # Using default installation
   $ /home/user/.rccontrol/enterprise-4/profile/bin/rhodecode-index \
       --instance-name=enterprise-4

   # Using a custom mapping file
   $ /home/user/.rccontrol/enterprise-4/profile/bin/rhodecode-index \
       --instance-name=enterprise-4 \
       --mapping=/home/user/.rccontrol/enterprise-4/mapping.ini

.. note::

   |RCT| require |PY| 2.7 to run.

.. _set-index:

Schedule the Indexer
^^^^^^^^^^^^^^^^^^^^

To schedule the indexer, configure the crontab file to run the indexer inside
your |RCT| virtualenv using the following steps.

1. Open the crontab file, using ``crontab -e``.
2. Add the indexer to the crontab, and schedule it to run as regularly as you
   wish.
3. Save the file.

.. code-block:: bash

    $ crontab -e

    # The virtualenv can be called using its full path, so for example you can
    # put this example into the crontab

    # Run the indexer daily at 4am using the default mapping settings
    * 4 * * * /home/ubuntu/.virtualenv/rhodecode-venv/bin/rhodecode-index \
    --instance-name=enterprise-1

    # Run the indexer every Sunday at 3am using default mapping
    * 3 * * 0 /home/ubuntu/.virtualenv/rhodecode-venv/bin/rhodecode-index \
    --instance-name=enterprise-1

    # Run the indexer every 15 minutes
    # using a specially configured mapping file
    */15 * * * * ~/.rccontrol/enterprise-4/profile/bin/rhodecode-index \
       --instance-name=enterprise-4 \
       --mapping=/home/user/.rccontrol/enterprise-4/mapping.ini

.. _advanced-indexing:

Advanced Indexing
^^^^^^^^^^^^^^^^^

|RCT| indexes based on the :file:`mapping.ini` file. To configure your index,
you can specify different options in this file. The default location is:

* :file:`/home/{user}/.rccontrol/{instance-id}/mapping.ini`, using default
  |RCT|.
* :file:`~/venv/lib/python2.7/site-packages/rhodecode_tools/templates/mapping.ini`,
  when using ``virtualenv``.

.. note::

    If you need to create the :file:`mapping.ini` file, use the |RCT|
    ``rhodecode-index --create-mapping path/to/file`` API call. For details,
    see the :ref:`tools-cli` section.

The indexer runs in a random order to prevent a failing |repo| from stopping
a build. To configure different indexing scenarios, set the following options
inside the :file:`mapping.ini` and specify the altered file using the
``--mapping`` option.

* ``index_files`` : Index the specified file types.
* ``skip_files`` : Do not index the specified file types.
* ``index_files_content`` : Index the content of the specified file types.
* ``skip_files_content`` : Do not index the content of the specified files.
* ``force`` : Create a fresh index on each run.
* ``max_filesize`` : Files larger than the set size will not be indexed.
* ``commit_parse_limit`` : Set the batch size when indexing commit messages.
  Set to a lower number to lessen memory load.
* ``repo_limit`` : Set the maximum number or |repos| indexed per run.
* ``[INCLUDE]`` : Set |repos| you want indexed. This takes precedent over
  ``[EXCLUDE]``.
* ``[EXCLUDE]`` : Set |repos| you do not want indexed. Exclude can be used to
  not index branches, forks, or log |repos|.

At the end of the file you can specify conditions for specific |repos| that
will override the default values. To configure your indexer,
use the following example :file:`mapping.ini` file.

.. code-block:: ini

    [__DEFAULT__]
    # default patterns for indexing files and content of files.
    # Binary files are skipped by default.

    # Index python and markdown files
    index_files = *.py, *.md

    # Do not index these file types
    skip_files = *.svg, *.log, *.dump, *.txt

    # Index both file types and their content
    index_files_content = *.cpp, *.ini, *.py

    # Index file names, but not file content
    skip_files_content = *.svg,

    # Force rebuilding an index from scratch. Each repository will be rebuild
    # from scratch with a global flag. Use local flag to rebuild single repos
    force = false

    # Do not index files larger than 385KB
    max_filesize = 385KB

    # Limit commit indexing to 500 per batch
    commit_parse_limit = 500

    # Limit each index run to 25 repos
    repo_limit = 25

    # __INCLUDE__ is more important that __EXCLUDE__.

    [__INCLUDE__]
    # Include all repos with these names

    docs/* = 1
    lib/* = 1

    [__EXCLUDE__]
    # Do not include the following repo in index

    dev-docs/* = 1
    legacy-repos/* = 1
    *-dev/* = 1

    # Each repo that needs special indexing is a separate section below.
    # In each section set the options to override the global configuration
    # parameters above.
    # If special settings are not configured, the global configuration values
    # above are inherited. If no special repositories are
    # defined here RhodeCode will use the API to ask for all repositories

    # For this repo use different settings
    [special-repo]
    commit_parse_limit = 20,
    skip_files = *.idea, *.xml,

    # For another repo use different settings
    [another-special-repo]
    index_files = *,
    max_filesize = 800MB
    commit_parse_limit = 20000

.. _Whoosh: https://pypi.python.org/pypi/Whoosh/
