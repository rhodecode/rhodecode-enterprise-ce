Adding Custom Packages
======================

If you wish to make additional Python modules available to use with
extensions that you have developed, use the following information.

Prerequisite
------------

|RCC| manages the |RCE| environment using Supervisor. To add custom packages
you need to install your instance of |RCE| as a self managed
instance. This will let you to update the ``PYTHONPATH`` without |RCC|
overwriting it. You can then extend the ``PYTHONPATH`` to find packaged
outside of the |RCC| managed environment. To install |RCE| as a self-managed
service using |RCC|, see the
:ref:`Self-managed Instructions <control:set-self-managed-supervisor>`.

Adding Custom Packages
----------------------

Once you have your instance configured as self-managed, use the following steps.

1. Add the modules to the |RCE| instance directory,
   :file:`/home/{user}/.rccontrol/{instance-id}`.
2. Add this location to your ``PYTHONPATH`` environment variable. This is set
   in the :file:`/home/{user}/.rccontrol/supervisor/supervisor.ini` file. For
   more information about ``PYTHONPATH``, see the `PYTHONPATH documentation`_.

.. code-block:: ini

   [program:enterprise-1_script]
   numprocs = 1
   redirect_stderr = true
   environment = PYTHONPATH="",GIT_SSL_CAINFO="/home/user/.rccontrol-profile/etc/ca-bundle.crt"

3. Specify the hook for your added module on the
   :menuselection:`Admin --> Settings --> Hooks` page. For
   example, ``python:rcextensions/you.custom.hook``
4. Restart |RCE| using the ``rccontrol restart <instance-id>`` command.
   For more information, see the :ref:`RhodeCode Control CLI <control:rcc-cli>`
   documentation.

.. _PYTHONPATH documentation: https://docs.python.org/2/using/cmdline.html#envvar-PYTHONPATH
