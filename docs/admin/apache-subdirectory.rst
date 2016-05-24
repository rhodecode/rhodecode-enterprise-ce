.. _apache-sub-ref:

Apache URL Prefix Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the following example to configure Apache to use a URL prefix.

.. code-block:: apache

    <Location /<someprefix> > # Change <someprefix> into your chosen prefix
      ProxyPass http://127.0.0.1:5000/<someprefix>
      ProxyPassReverse http://127.0.0.1:5000/<someprefix>
      SetEnvIf X-Url-Scheme https HTTPS=1
    </Location>

In addition to the regular Apache setup you will need to add the following
lines into the ``rhodecode.ini`` file.

* In the the ``[app:main]`` section of your ``rhodecode.ini`` file add the
  following line.

.. code-block:: ini

    filter-with = proxy-prefix

* At the end of the ``rhodecode.ini`` file add the following section.

.. code-block:: ini

    [filter:proxy-prefix]
    use = egg:PasteDeploy#prefix
    prefix = /<someprefix> # Change <someprefix> into your chosen prefix
