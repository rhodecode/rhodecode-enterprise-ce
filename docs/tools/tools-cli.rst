.. _tools-cli:

|RCT| CLI
---------

The commands available with |RCT| can be split into three categories:

- Remotely executable commands that can be run from your local machine once you
  have your connection details to |RCE| configured.
- Locally executable commands the can be run on the server to carry out
  general maintenance.
- Local configuration commands used to help set up your |RCT| configuration.


rhodecode-tools
---------------

Use |RCT| to setup automation, run the indexer, and install extensions for
your |RCM| instances. Options:

.. rst-class:: dl-horizontal

    \ - -apihost <api_host>
        Set the API host value.

    \ - -apikey <apikey_value>
        Set the API key value.

    \-c, - -config <config_file>
        Create a configuration file. The default file is created
        in ``~/.rhoderc``

    \ - -save-config
        Save the configuration file.

    \ - -show-config
        Show the current configuration values.

    \ - -format {json,pretty}
        Set the formatted representation.

Example usage:

.. code-block:: bash

   $ rhodecode-tools --apikey=key --apihost=http://rhodecode.server \
       --save-config

rhodecode-api
-------------

The |RC| API lets you connect to |RCE| and carry out management tasks from a
remote machine, for more information about the API, see the :ref:`api`. To
pass arguments on the command-line use the ``method:option`` syntax.

Example usage:

.. code-block:: bash

    # Run the get_repos API call and sample output
    $ rhodecode-api --instance-name=enterprise-1 create_repo \
        repo_name:brand-new repo_type:hg description:repo-desc

    {
      "error": null,
      "id": 1110,
      "result": {
        "msg": "Created new repository `brand-new`",
        "success": true,
        "task": null
      }
    }

Options:

.. rst-class:: dl-horizontal

    \ - -api-cache-only
        Requires a cache to be present when running this call

    \ - -api-cache-rebuild
        Replaces existing cached values with new ones from server

    \ - -api-cache <PATH>
        Use a special cache dir to read responses from instead of the server

    \ - -api-cert-verify
         Verify the endpoint ssl certificate

    \ - -api-cert <PATH>
         Path to alternate CA bundle.

    \ - -apihost <api_host>
        Set the API host value.

    \ - -apikey <apikey_value>
        Set the API key value.

    \ - -instance-name <instance-id>
        Set the instance name

    \-I, - -install-dir <DIR>
        Location of application instances

    \-c, - -config <.rhoderc-file>
        Location of the :file:`.rhoderc`

    \-F, - -format {json,pretty}
        Set the formatted representation.

    \-h, - -help
        Show help messages.

    \-v, - -verbose
        Enable verbose messaging

rhodecode-cleanup-gists
-----------------------

Use this to delete gists within |RCM|. Options:

.. rst-class:: dl-horizontal

    \-c, - -config <config_file>
        Set the file path to the configuration file. The default file is
        :file:`/home/{user}/.rhoderc`

    \ - -corrupted
        Remove gists with corrupted metadata.

    \ - -dont-ask
        Remove gists without asking for confirmation.

    \-h, - -help
        Show help messages. current configuration values.

    \ - -instance-name <instance-id>
        Set the instance name.

    \-R, - -repo-dir
        Set the repository file path.

    \ - -version
        Display your |RCT| version.

Example usage:

.. code-block:: bash

    # Clean up gists related to an instance
    $ rhodecode-cleanup-gists --instance-name=enterprise-1
    Scanning for gists in /home/brian/repos/.rc_gist_store...
    preparing to remove [3] found gists

    # Clean up corrupted gists in an instance
    $ rhodecode-cleanup-gists --instance-name=enterprise-1 --corrupted
    Scanning for gists in /home/brian/repos/.rc_gist_store...
    preparing to remove [2] found gists
    the following gists will be archived:
      * EXPIRED: BAD METADATA        | /home/brian/repos/.rc_gist_store/5
      * EXPIRED: BAD METADATA        | /home/brian/repos/.rc_gist_store/8FtC
    are you sure you want to archive them? [y/N]: y
    removing gist /home/brian/repos/.rc_gist_store/5
    removing gist /home/brian/repos/.rc_gist_store/8FtCKdcbRKmEvRzTVsEt

rhodecode-cleanup-repos
-----------------------

Use this to manage |repos| and |repo| groups within |RCM|. Options:

.. rst-class:: dl-horizontal

    \-c, - -config <config_file>
        Set the file path to the configuration file. The default file is
        :file:`/home/{user}/.rhoderc`.

    \-h, - -help
        Show help messages. current configuration values.

    \ - -interactive
        Enable an interactive prompt for each repository when deleting.

    \ - -include-groups
        Remove repository groups.

    \ - -instance-name <instance-id>
        Set the instance name.

    \ - -list-only
        Display repositories selected for deletion.

    \ - -older-than <str>
        Delete repositories older that a specified time.
        You can use the following suffixes; d for days, h for hours,
        m for minutes, s for seconds.

    \-R, - -repo-dir
        Set the repository file path

Example usage:

.. code-block:: bash

    # Cleaning up repos using tools installed with RCE 350 and above
    $ ~/.rccontrol/enterprise-4/profile/bin/rhodecode-cleanup-repos \
        --instance-name=enterprise-4 --older-than=1d
    Scanning for repositories in /home/brian/repos...
    preparing to remove [2] found repositories older than 1 day, 0:00:00 (1d)

    the following repositories will be deleted completely:
    * REMOVED: 2015-08-05 00:23:18 | /home/brian/repos/rm__20150805_002318_831
    * REMOVED: 2015-08-04 01:22:10 | /home/brian/repos/rm__20150804_012210_336
    are you sure you want to remove them? [y/N]:

    # Clean up repos older than 1 year
    # If using virtualenv and pre RCE 350 tools installation
    (venv)$ rhodecode-cleanup-repos --instance-name=enterprise-1 \
        --older-than=365d

    Scanning for repositories in /home/brian/repos...
    preparing to remove [343] found repositories older than 365 days

    # clean up repos older than 3 days
    # If using virtualenv and pre RCE 350 tools installation
    (venv)$ rhodecode-cleanup-repos --instance-name=enterprise-1 \
        --older-than=3d
    Scanning for repositories in /home/brian/repos...
    preparing to remove [3] found repositories older than 3 days

.. _tools-config:

rhodecode-config
----------------

Use this to create or update a |RCE| configuration file on the local machine.

.. rst-class:: dl-horizontal

    \- -filename </path/to/config_file>
        Set the file path to the |RCE| configuration file.

    \- -show-defaults
        Display the defaults set in the |RCE| configuration file.

    \- -update
        Update the configuration with the new settings passed on the command
        line.

.. code-block:: bash

    # Create a new config file
    $ rhodecode-config --filename=dev.ini
    Wrote new config file in /Users/user/dev.ini

    # Update config value for given section:
    $ rhodecode-config --update --filename=prod.ini [handler_console]level=INFO

    $ rhodecode-config --filename=dev.ini --show-defaults
    lang=en
    cpu_number=4
    uuid=<function <lambda> at 0x10d86ac08>
    license_token=ff1e-aa9c-bb66-11e5
    host=127.0.0.1
    here=/Users/brian
    error_aggregation_service=None
    database_url=sqlite:///%(here)s/rhodecode.db?timeout=30
    git_path=git
    http_server=waitress
    port=5000

.. _tools-rhodecode-extensions:

rhodecode-extensions
--------------------

|RCT| adds additional mapping for :ref:`indexing-ref`, statistics, and adds
additional code for push/pull/create/delete |repo| hooks. These hooks can be
used to send signals to build-bots such as jenkins. Options:

.. rst-class:: dl-horizontal

    \-c, - -config <config_file>
        Create a configuration file. The default file is created
        in ``~/.rhoderc``

    \-h, - -help
         Show help messages.

    \-F, - -format {json,pretty}
        Set the formatted representation.

    \-I, - -install-dir <str>
        Set the location of the |RCE| installation. The default location is
        :file:`/home/{user}/.rccontrol/`.

    \ - -ini-file <str>
        Path to the :file:`rhodecode.ini` file for that instance.

    \ - -instance-name <instance-id>
        Set the instance name.

    \ - -plugins
         Add plugins to your |RCE| installation. See the
         :ref:`integrations-ref` section for more details.

    \ - -version
         Display your |RCT| version.


Once installed, you will see a :file:`rcextensions` folder in the instance
directory, for example :file:`home/{user}/.rccontrol/{instance-id}/rcextensions`

To install ``rcextensions``, use the following example:

.. code-block:: bash

    # install extensions on the given instance
    # If using virtualenv prior to RCE 350
    (venv)$ rhodecode-extensions --instance-name=enterprise-1 \
        --ini-file=rhodecode.ini
    Writen new extensions file to rcextensions

    # install extensions with additional plugins on the given instance
    (venv)$ rhodecode-extensions --instance-name=enterprise-1 \
        --ini-file=rhodecode.ini --plugins
    Writen new extensions file to rcextensions

    # installing extensions from 350 onwards
    # as they are packaged with RCE
    $ .rccontrol/enterprise-4/profile/bin/rhodecode-extensions --plugins \
      --instance-name=enterprise-4 --ini-file=rhodecode.ini

    Writen new extensions file to rcextensions

See the new extensions inside this directory for more details about the
additional hooks available, for example see the ``push_post.py`` file.

.. code-block:: python

    import urllib
    import urllib2

    def run(*args, **kwargs):
        """
        Extra params

        :param URL: url to send the data to
        """

        url = kwargs.pop('URL', None)
        if url:
            from rhodecode.lib.compat import json
            from rhodecode.model.db import Repository

            repo = Repository.get_by_repo_name(kwargs['repository'])
            changesets = []
            vcs_repo = repo.scm_instance_no_cache()
            for r in kwargs['pushed_revs']:
                cs = vcs_repo.get_changeset(r)
                changesets.append(json.dumps(cs))

            kwargs['pushed_revs'] = changesets
            headers = {
                'User-Agent': 'RhodeCode-SCM web hook',
                'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept': 'text/javascript, text/html, application/xml, '
                          'text/xml, */*',
                'Accept-Encoding': 'gzip,deflate,sdch',
            }

            data = kwargs
            data = urllib.urlencode(data)
            req = urllib2.Request(url, data, headers)
            response = urllib2.urlopen(req)
            response.read()
            return 0


rhodecode-gist
--------------

Use this to create, list, show, or delete gists within |RCM|. Options:

.. rst-class:: dl-horizontal

    \ - -api-cache-only
        Requires a cache to be present when running this call

    \ - -api-cache-rebuild
        Replaces existing cached values with new ones from server

    \ - -api-cache PATH
        Use a special cache dir to read responses from instead of the server

    \ - -api-cert-verify
         Verify the endpoint ssl certificate

    \ - -api-cert PATH
         Path to alternate CA bundle.

    \ - -apihost <api_host>
        Set the API host value.

    \ - -apikey <apikey_value>
        Set the API key value.

    \-c, - -config <config_file>
        Create a configuration file.
        The default file is created in :file:`~/.rhoderc`

    \ - -create <gistname>
        create the gist

    \-d, - -description <str>
        Set gist description

    \ - -delete <gistid>
        Delete the gist

    \-f, - -file
        Specify the filename The file extension will enable syntax highlighting.

    \-F, - -format {json,pretty}
        Set the formatted representation.

    \ - -help
        Show help messages.

    \-I, - -install-dir <DIR>
        Location of application instances

    \ - -instance-name <instance-id>
        Set the instance name.

    \ - -list
        Display instance gists.

    \-l, --lifetime <minutes>
        Set the gist lifetime. The default value is (-1) forever

    \ - -show <gistname>
        Show the content of the gist

    \-o, - -open
        After creating Gist open it in browser

    \-p, - -private
        Create a private gist

    \ - -version
         Display your |RCT| version.

Example usage:

.. code-block:: bash

    # List the gists in an instance
    (venv)brian@ubuntu:~$ rhodecode-gist --instance-name=enterprise-1 list
    {
      "error": null,
      "id": 7102,
      "result": [
        {
          "access_id": "2",
          "content": null,
          "created_on": "2015-01-19T12:52:26.494",
          "description": "A public gust",
          "expires": -1.0,
          "gist_id": 2,
          "type": "public",
          "url": "http://127.0.0.1:10003/_admin/gists/2"
        },
        {
          "access_id": "7gs6BsSEC4pKUEPLz5AB",
          "content": null,
          "created_on": "2015-01-19T11:27:40.812",
          "description": "Gist testing API",
          "expires": -1.0,
          "gist_id": 1,
          "type": "private",
          "url": "http://127.0.0.1:10003/_admin/gists/7gs6BsSEC4pKUEPLz5AB"
        }
      ]
    }

    # delete a particular gist
    # You use the access_id to specify the gist to delete
    (venv)brian@ubuntu:~$ rhodecode-gist delete 2  --instance-name=enterprise-1
    {
      "error": null,
      "id": 6284,
      "result": {
        "gist": null,
        "msg": "deleted gist ID:2"
      }
    }

    # cat a file and pipe to new gist
    # This is if you are using virtualenv
    (venv)$ cat ~/.rhoderc | rhodecode-gist --instance-name=enterprise-1 \
        -d '.rhoderc copy' create

    {
      "error": null,
      "id": 5374,
      "result": {
        "gist": {
          "access_id": "7",
          "content": null,
          "created_on": "2015-01-26T11:31:58.774",
          "description": ".rhoderc copy",
          "expires": -1.0,
          "gist_id": 7,
          "type": "public",
          "url": "http://127.0.0.1:10003/_admin/gists/7"
        },
        "msg": "created new gist"
      }
    }

    # Cat a file and pipe to gist
    # in RCE 3.5.0 tools and above
    $ cat ~/.rhoderc | ~/.rccontrol/{instance-id}/profile/bin/rhodecode-gist \
       --instance-name=enterprise-4 -d '.rhoderc copy' create
    {
      "error": null,
      "id": 9253,
      "result": {
        "gist": {
          "access_id": "4",
          "acl_level": "acl_public",
          "content": null,
          "created_on": "2015-08-20T05:54:11.250",
          "description": ".rhoderc copy",
          "expires": -1.0,
          "gist_id": 4,
          "modified_at": "2015-08-20T05:54:11.250",
          "type": "public",
          "url": "http://127.0.0.1:10000/_admin/gists/4"
        },
        "msg": "created new gist"
      }
    }


rhodecode-index
---------------

More detailed information regarding setting up the indexer is available in
the :ref:`indexing-ref` section. Options:

.. rst-class:: dl-horizontal

    \ - -api-cache-only
        Requires a cache to be present when running this call

    \ - -api-cache-rebuild
        Replaces existing cached values with new ones from server

    \ - -api-cache PATH
        Use a special cache dir to read responses from instead of the server

    \ - -api-cert-verify
         Verify the endpoint ssl certificate

    \ - -api-cert PATH
         Path to alternate CA bundle.

    \ - -apihost <api_host>
        Set the API host value.

    \ - -apikey <apikey_value>
        Set the API key value.

    \-c, --config <config_file>
        Create a configuration file.
        The default file is created in :file:`~/.rhoderc`

    \ - -create-mapping <PATH>
         Creates an example mapping configuration for indexer.

    \-F, - -format {json,pretty}
         Set the formatted representation.

    \-h, - -help
         Show help messages.

    \ - -instance-name <instance-id>
        Set the instance name

    \-I, - -install-dir <DIR>
        Location of application instances

    \-m, - -mapping <file_name>
         Parse the output to the .ini mapping file.

    \ - -optimize
         Optimize index for performance by amalgamating multiple index files
         into one. Greatly increases incremental indexing speed.

    \-R, - -repo-dir <DIRECTORY>
         Location of repositories

    \ - -source <PATH>
         Use a special source JSON file to feed the indexer

    \ - -version
         Display your |RCT| version.

Example usage:

.. code-block:: bash

    # Run the indexer
    $ ~/.rccontrol/enterprise-4/profile/bin/rhodecode-index \
        --instance-name=enterprise-4

    # Run indexer based on mapping.ini file
    # This is using pre-350 virtualenv
    (venv)$ rhodecode-index --instance-name=enterprise-1

    # Index from the command line without creating
    # the .rhoderc file
    $ rhodecode-index --apikey=key --apihost=http://rhodecode.server \
        --instance-name=enterprise-2 --save-config

    # Create the indexing mapping file
    $ ~/.rccontrol/enterprise-4/profile/bin/rhodecode-index \
        --create-mapping mapping.ini --instance-name=enterprise-4

.. _tools-rhodecode-list-instance:

rhodecode-list-instances
------------------------

Use this command to list the instance details configured in the
:file:`~/.rhoderc` file.

.. code-block:: bash

   $ .rccontrol/enterprise-1/profile/bin/rhodecode-list-instances
   [instance:production] - Config only
   API-HOST: https://some.url.com
   API-KEY:  some.auth.token

   [instance:development] - Config only
   API-HOST: http://some.ip.address
   API-KEY:  some.auth.token


.. _tools-setup-config:

rhodecode-setup-config
----------------------

Use this command to create the ``~.rhoderc`` file required by |RCT| to access
remote instances.

.. rst-class:: dl-horizontal

    \- -instance-name <name>
        Specify the instance name in the :file:`~/.rhoderc`

    \api_host <hostname>
        Create a configuration file. The default file is created
        in ``~/.rhoderc``

    \api_key <auth-token>
        Create a configuration file. The default file is created
        in ``~/.rhoderc``


.. code-block:: bash

    (venv)$ rhodecode-setup-config --instance-name=tea api_host=URL api_key=xyz
    Config not found under /Users/username/.rhoderc, creating a new one
    Wrote new configuration into /Users/username/.rhoderc
