.. _config-database:

Make Database Changes
---------------------

.. important::

   If you do change the |repo| database that |RCEE| uses, then you will need to
   upgrade the database, and also remap and rescan the |repos|. More detailed
   information is available in the
   :ref:`Alternative upgrade documentation <control:install-port>`.

If you need to change database connection details for a |RCEE| instance,
use the following steps:

1. Open the :file:`rhodecode.ini` file for the instance you wish to edit. The
   default location is
   :file:`home/{user}/.rccontrol/{instance-id}/rhodecode.ini`
2. When you open the file, find the database configuration section,
   and use the below example to change the
   connection details:

.. code-block:: ini

    #########################################################
    ### DB CONFIGS - EACH DB WILL HAVE IT'S OWN CONFIG    ###
    #########################################################

    # Default SQLite config
    sqlalchemy.db1.url = sqlite:////home/brian/.rccontrol/enterprise-1/rhodecode.db

    # Use this example for a PostgreSQL
    sqlalchemy.db1.url = postgresql://postgres:qwe@localhost/rhodecode

    # see sqlalchemy docs for other advanced settings
    sqlalchemy.db1.echo = false
    sqlalchemy.db1.pool_recycle = 3600
    sqlalchemy.db1.convert_unicode = true
