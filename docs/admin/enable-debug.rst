.. _debug-mode:

Enabling Debug Mode
-------------------

To enable debug mode on a |RCE| instance you need to set the debug property
in the :file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file. To
do this, use the following steps

1. Open the file and set the ``debug`` line to ``true``
2. Restart you instance using the ``rccontrol restart`` command,
   see the following example:

You can also set the log level, the follow are the valid options;
``debug``, ``info``, ``warning``, or ``fatal``.

.. code-block:: ini

    [DEFAULT]
    debug = true
    pdebug = false

.. code-block:: bash

    # Restart your instance
    $ rccontrol restart enterprise-1
    Instance "enterprise-1" successfully stopped.
    Instance "enterprise-1" successfully started.

Debug and Logging Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Further debugging and logging settings can also be set in the
:file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file.

In the logging section, the various packages that run with |RCE| can have
different debug levels set. If you want to increase the logging level change
``level = DEBUG`` line to one of the valid options.

You also need to change the log level for handlers. See the example
``##handler`` section below. The ``handler`` level takes the same options as
the ``debug`` level.

.. code-block:: ini

    ################################
    ### LOGGING CONFIGURATION   ####
    ################################
    [loggers]
    keys = root, routes, rhodecode, sqlalchemy, beaker, pyro4, templates

    [handlers]
    keys = console, console_sql, file, file_rotating

    [formatters]
    keys = generic, color_formatter, color_formatter_sql

    #############
    ## LOGGERS ##
    #############
    [logger_root]
    level = NOTSET
    handlers = console

    [logger_routes]
    level = DEBUG
    handlers =
    qualname = routes.middleware
    ## "level = DEBUG" logs the route matched and routing variables.
    propagate = 1

    [logger_beaker]
    level = DEBUG
    handlers =
    qualname = beaker.container
    propagate = 1

    [logger_pyro4]
    level = DEBUG
    handlers =
    qualname = Pyro4
    propagate = 1

    [logger_templates]
    level = INFO
    handlers =
    qualname = pylons.templating
    propagate = 1

    [logger_rhodecode]
    level = DEBUG
    handlers =
    qualname = rhodecode
    propagate = 1

    [logger_sqlalchemy]
    level = INFO
    handlers = console_sql
    qualname = sqlalchemy.engine
    propagate = 0

    ##############
    ## HANDLERS ##
    ##############

    [handler_console]
    class = StreamHandler
    args = (sys.stderr,)
    level = INFO
    formatter = generic

    [handler_console_sql]
    class = StreamHandler
    args = (sys.stderr,)
    level = WARN
    formatter = generic

    [handler_file]
    class = FileHandler
    args = ('rhodecode.log', 'a',)
    level = INFO
    formatter = generic

    [handler_file_rotating]
    class = logging.handlers.TimedRotatingFileHandler
    # 'D', 5 - rotate every 5days
    # you can set 'h', 'midnight'
    args = ('rhodecode.log', 'D', 5, 10,)
    level = INFO
    formatter = generic
