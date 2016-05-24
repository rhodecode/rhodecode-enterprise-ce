.. _svn-http:

|svn| With Write Over HTTP
--------------------------

To use |svn| with write access, the currently supported method is over HTTP.
This requires you to configure your local machine so that it can access your
|RCE| instance.

Prerequisites
^^^^^^^^^^^^^

- Enable lab setting on your |RCE| instance, see :ref:`lab-settings`.
- You need to install the following tools on your local machine: ``Apache`` and
  ``mod_dav_svn``. Use the following Ubuntu as an example.

.. code-block:: bash

    $ sudo apt-get install apache2 libapache2-mod-svn

Once installed you need to enable ``dav_svn``:

.. code-block:: bash

    $ sudo a2enmod dav_svn

Configuring Apache Setup
^^^^^^^^^^^^^^^^^^^^^^^^

.. tip::

   It is recommended to run Apache on a port other than 80, due to possible
   conflicts with other HTTP servers like nginx. To do this, set the
   ``Listen`` parameter in the ``/etc/apache2/ports.conf`` file, for example
   ``Listen 8090``

   It is also recommended to run apache as the same user as |RCE|, otherwise
   permission issues could occur. To do this edit the ``/etc/apache2/envvars``

   .. code-block:: apache

      export APACHE_RUN_USER=ubuntu
      export APACHE_RUN_GROUP=ubuntu

1. To configure Apache, create and edit a virtual hosts file, for example
   :file:`/etc/apache2/sites-available/default.conf`, or create another
   virtual hosts file and add a location section inside the
   ``<VirtualHost>`` section.

.. code-block:: apache

    <Location />
        DAV svn
        # Must be explicit path, relative not supported
        SVNParentPath /PATH/TO/REPOSITORIES
        SVNListParentPath On
        Allow from all
        Order allow,deny
    </Location>

.. note::

   Once configured, check that you can see the list of repositories on your
   |RCE| instance.

2. Go to the :menuselection:`Admin --> Settings --> Labs` page, and
   enable :guilabel:`Proxy Subversion HTTP requests`, and specify the
   :guilabel:`Subversion HTTP Server URL`.

Using |svn|
^^^^^^^^^^^

Once |svn| has been enabled on your instance, you can use it using the
following examples. For more |svn| information, see the `Subversion Red Book`_

.. code-block:: bash

    # To clone a repository
    svn clone http://my-svn-server.example.com/my-svn-repo

    # svn commit
    svn commit

.. _Subversion Red Book: http://svnbook.red-bean.com/en/1.7/svn-book.html#svn.ref.svn
