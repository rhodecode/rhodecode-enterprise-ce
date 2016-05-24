.. _apache-wsgi-ref:

Apache WSGI Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

|RCM| can also be set up with Apache under ``mod_wsgi``. To configure this
use the following steps.

1. Install ``mod_wsgi`` using the following command:
   ``aptitude install libapache2-mod-wsgi``.
2. Enable ``mod_wsgi`` using the following command: ``a2enmod wsgi``
3. Create a ``wsgi`` dispatch script, using the following examples.

.. code-block:: bash

   WSGIDaemonProcess pylons \
   threads=4 \
   # check the python virtual env location
   python-path=/home/web/rhodecode/pyenv/lib/python2.6/site-packages
   # Check the install location
   WSGIScriptAlias / /home/web/rhodecode/dispatch.wsgi
   WSGIPassAuthorization On
     # user=www-data group=www-data # Enable if running Apache as root

.. note::

   Do not set ``processes=num`` in this configuration file. Running |RCE| in
   multiprocess mode with Apache is not supported.

The following is an example ``wsgi`` dispatch script.

.. code-block:: python

    import os
    os.environ["HGENCODING"] = "UTF-8"
    os.environ['PYTHON_EGG_CACHE'] = '/home/web/rhodecode/.egg-cache'

    # Set the current dir
    os.chdir('/home/web/rhodecode/')

    import site
    site.addsitedir("/home/web/rhodecode/pyenv/lib/python2.6/site-packages")

    from paste.deploy import loadapp
    from paste.script.util.logging_config import fileConfig

    fileConfig('/home/web/rhodecode/production.ini')
    application = loadapp('config:/home/web/rhodecode/production.ini')

.. note::

   When using `mod_wsgi` the same version of |hg| must be running in your
   system's |PY| environment and on |RCM|. To check the |RCM| version,
   on the interface go to
   :menuselection:`Admin --> Settings --> System Info`
