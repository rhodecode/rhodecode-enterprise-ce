.. _vcs-server:

VCS Server Management
---------------------

The VCS Server handles |RCM| backend functionality. You need to configure
a VCS Server to run with a |RCM| instance. If you do not, you will be missing
the connection between |RCM| and its |repos|. This will cause error messages
on the web interface. You can run your setup in the following configurations,
currently the best performance is one VCS Server per |RCM| instance:

* One VCS Server per |RCM| instance.
* One VCS Server handling multiple instances.

.. important::

   If your server locale settings are not correctly configured,
   |RCE| and the VCS Server can run into issues. See this `Ask Ubuntu`_ post
   which explains the problem and gives a solution.

For more information, see the following sections:

* :ref:`install-vcs`
* :ref:`config-vcs`
* :ref:`vcs-server-options`
* :ref:`vcs-server-versions`
* :ref:`vcs-server-maintain`
* :ref:`vcs-server-config-file`

.. _install-vcs:

VCS Server Installation
^^^^^^^^^^^^^^^^^^^^^^^

To install a VCS Server, see
:ref:`Installing a VCS server <control:install-vcsserver>`.

.. _config-vcs:

Hooking |RCE| to its VCS Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To configure a |RCE| instance to use a VCS server, see
:ref:`Configuring the VCS Server connection <control:manually-vcsserver-ini>`.

.. _vcs-server-options:

|RCE| VCS Server Options
^^^^^^^^^^^^^^^^^^^^^^^^

The following list shows the available options on the |RCM| side of the
connection to the VCS Server. The settings are configured per
instance in the
:file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file.

.. rst-class:: dl-horizontal

    \vcs.backends <available-vcs-systems>
        Set a comma-separated list of the |repo| options available from the
        web interface. The default is ``hg, git, svn``,
        which is all |repo| types available.

    \vcs.connection_timeout <seconds>
        Set the length of time in seconds that the VCS Server waits for
        requests to process. After the timeout expires,
        the request is closed. The default is ``3600``. Set to a higher
        number if you experience network latency, or timeout issues with very
        large push/pull requests.

    \vcs.server.enable <boolean>
        Enable or disable the VCS Server. The available options are ``true`` or
        ``false``. The default is ``true``.

    \vcs.server <host:port>
        Set the host, either hostname or IP Address, and port of the VCS server
        you wish to run with your |RCM| instance.

.. code-block:: ini

    ##################
    ### VCS CONFIG ###
    ##################
    # set this line to match your VCS Server
    vcs.server = 127.0.0.1:10004
    # Set to False to disable the VCS Server
    vcs.server.enable = True
    vcs.backends = hg, git, svn
    vcs.connection_timeout = 3600


.. _vcs-server-versions:

VCS Server Versions
^^^^^^^^^^^^^^^^^^^

An updated version of the VCS Server is released with each |RCE| version. Use
the VCS Server number that matches with the |RCE| version to pair the
appropriate ones together. For |RCE| versions pre 3.3.0,
VCS Server 1.X.Y works with |RCE| 3.X.Y, for example:

* VCS Server 1.0.0 works with |RCE| 3.0.0
* VCS Server 1.2.2 works with |RCE| 3.2.2

For |RCE| versions post 3.3.0, the VCS Server and |RCE| version numbers
match, for example:

* VCS Server |release| works with |RCE| |release|

.. _vcs-server-maintain:

VCS Server Memory Optimization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To configure the VCS server to manage the cache efficiently, you need to
configure the following options in the
:file:`/home/{user}/.rccontrol/{vcsserver-id}/vcsserver.ini` file. Once
configured, restart the VCS Server.

.. rst-class:: dl-horizontal

    \beaker.cache.repo_object.type = memorylru
        Configures the cache to discard the least recently used items.
        This setting takes the following valid options:

        * ``memorylru``: The default setting, which removes the least recently
          used items from the cache.
        * ``memory``: Runs the VCS Server without clearing the cache.
        * ``nocache``: Runs the VCS Server without a cache. This will
          dramatically reduce the VCS Server performance.

    \beaker.cache.repo_object.max_items = 100
        Sets the maximum number of items stored in the cache, before the cache
        starts to be cleared.

        As a general rule of thumb, running this value at 120 resulted in a
        5GB cache. Running it at 240 resulted in a 9GB cache. Your results
        will differ based on usage patterns and |repo| sizes.

        Tweaking this value to run at a fairly constant memory load on your
        server will help performance.

To clear the cache completely, you can restart the VCS Server.

.. important::

   While the VCS Server handles a restart gracefully on the web interface,
   it will drop connections during push/pull requests. So it is recommended
   you only perform this when there is very little traffic on the instance.

Use the following example to restart your VCS Server,
for full details see the :ref:`RhodeCode Control CLI <control:rcc-cli>`.

.. code-block:: bash

    $ rccontrol status

.. code-block:: vim

    - NAME: vcsserver-1
    - STATUS: RUNNING
    - TYPE: VCSServer
    - VERSION: 1.0.0
    - URL: http://127.0.0.1:10001

    $ rccontrol restart vcsserver-1
    Instance "vcsserver-1" successfully stopped.
    Instance "vcsserver-1" successfully started.

.. _vcs-server-config-file:

VCS Server Configuration
^^^^^^^^^^^^^^^^^^^^^^^^

You can configure settings for multiple VCS Servers on your
system using their individual configuration files. Use the following
properties inside the configuration file to set up your system. The default
location is :file:`home/{user}/.rccontrol/{vcsserver-id}/vcsserver.ini`.
For a more detailed explanation of the logger levers, see :ref:`debug-mode`.

.. rst-class:: dl-horizontal

    \host <ip-address>
        Set the host on which the VCS Server will run.

    \port <int>
        Set the port number on which the VCS Server will be available.

    \locale <locale_utf>
        Set the locale the VCS Server expects.

    \threadpool_size <int>
        Set the size of the threadpool used to communicate
        with the WSGI workers. This should be at least 6 times the number of
        WSGI worker processes.

    \timeout <seconds>
        Set the timeout for RPC communication in seconds.

.. note::

   After making changes, you need to restart your VCS Server to pick them up.

.. code-block:: ini

    ################################################################################
    # RhodeCode VCSServer - configuration                                          #
    #                                                                              #
    ################################################################################

    [DEFAULT]
    host = 127.0.0.1
    port = 9900
    locale = en_US.UTF-8
    # number of worker threads, this should be set based on a formula threadpool=N*6
    # where N is number of RhodeCode Enterprise workers, eg. running 2 instances
    # 8 gunicorn workers each would be 2 * 8 * 6 = 96, threadpool_size = 96
    threadpool_size = 16
    timeout = 0

    # cache regions, please don't change
    beaker.cache.regions = repo_object
    beaker.cache.repo_object.type = memorylru
    beaker.cache.repo_object.max_items = 1000

    # cache auto-expires after N seconds
    beaker.cache.repo_object.expire = 10
    beaker.cache.repo_object.enabled = true


    ################################
    ### LOGGING CONFIGURATION   ####
    ################################
    [loggers]
    keys = root, vcsserver, pyro4, beaker

    [handlers]
    keys = console

    [formatters]
    keys = generic

    #############
    ## LOGGERS ##
    #############
    [logger_root]
    level = NOTSET
    handlers = console

    [logger_vcsserver]
    level = DEBUG
    handlers =
    qualname = vcsserver
    propagate = 1

    [logger_beaker]
    level = DEBUG
    handlers =
    qualname = beaker
    propagate = 1

    [logger_pyro4]
    level = DEBUG
    handlers =
    qualname = Pyro4
    propagate = 1


    ##############
    ## HANDLERS ##
    ##############

    [handler_console]
    class = StreamHandler
    args = (sys.stderr,)
    level = DEBUG
    formatter = generic

    [handler_file]
    class = FileHandler
    args = ('vcsserver.log', 'a',)
    level = DEBUG
    formatter = generic

    [handler_file_rotating]
    class = logging.handlers.TimedRotatingFileHandler
    # 'D', 5 - rotate every 5days
    # you can set 'h', 'midnight'
    args = ('vcsserver.log', 'D', 5, 10,)
    level = DEBUG
    formatter = generic

    ################
    ## FORMATTERS ##
    ################

    [formatter_generic]
    format = %(asctime)s.%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s
    datefmt = %Y-%m-%d %H:%M:%S


.. _Ask Ubuntu: http://askubuntu.com/questions/162391/how-do-i-fix-my-locale-issue
