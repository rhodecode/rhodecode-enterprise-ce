.. _x-frame:

Securing HTTPS Connections
--------------------------

* To secure your |RCE| instance against `Cross Frame Scripting`_ exploits, you
  should configure your webserver ``x-frame-options`` setting.

* To configure your instance for `HTTP Strict Transport Security`_, you need to
  configure the ``Strict-Transport-Security`` setting.

Nginx
^^^^^

In your nginx configuration, add the following lines in the correct files. For
more detailed information see the :ref:`nginx-ws-ref` section.

.. code-block:: nginx

    # Add this line to the nginx.conf file
    add_header X-Frame-Options SAMEORIGIN;

    # This line needs to be added inside your virtual hosts block/file
    add_header Strict-Transport-Security "max-age=31536000; includeSubdomains;";

Apache
^^^^^^

In your :file:`apache2.conf` file, add the following line. For more detailed
information see the :ref:`apache-ws-ref` section.

.. code-block:: apache

    # Add this to your virtual hosts file
    Header always append X-Frame-Options SAMEORIGIN

    # Add this line in your virtual hosts file
    Header always set Strict-Transport-Security "max-age=63072000; includeSubdomains; preload"

|RCE| Configuration
^^^^^^^^^^^^^^^^^^^

|RCE| can also be configured to force strict *https* connections and Strict
Transport Security. To set this, configure the following options to ``true``
in the :file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini` file.

.. code-block:: ini

    ## force https in RhodeCode, fixes https redirects, assumes it's always https
    force_https = false

    ## use Strict-Transport-Security headers
    use_htsts = false


.. _Cross Frame Scripting: https://www.owasp.org/index.php/Cross_Frame_Scripting
.. _HTTP Strict Transport Security: https://www.owasp.org/index.php/HTTP_Strict_Transport_Security