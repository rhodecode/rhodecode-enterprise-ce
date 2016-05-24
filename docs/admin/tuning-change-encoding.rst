.. _change-encoding:

Change Default Encoding
-----------------------

|RCE| uses ``utf8`` encoding by default. You can change the default encoding
in the :file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file. To
change the default encoding used by |RCE|, set a new value for the
``default_encoding``.

.. code-block:: ini

        # default encoding used to convert from and to unicode
        # can be also a comma separated list of encoding in case of mixed
        # encodings
        default_encoding = utf8

.. note::

       Changing the default encoding will affect many parts of your |RCE|
       installation, including committers names,
       file names, and the encoding of commit messages.
