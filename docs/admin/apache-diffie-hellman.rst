.. _dh-apache:

Diffie-Hellman Security
-----------------------

To secure your web server, the `Guide to Deploying Diffie-Hellman for TLS`_
contains important information worth reading. This link contains some good
`secure Apache configuration`_ examples.

To secure your deployment of Diffie-Hellman, configure the following:

1. Generate a strong Diffie-hellman group, 2048-bit or stronger.

.. code-block:: bash

    # to generate your dhparam.pem file, run in the terminal
    openssl dhparam -out /etc/apache/ssl/dhparam.pem 2048

2. Configure your server to only use modern, secure cipher suites in the
   virtual hosts configuration file.

.. code-block:: apache

    # Set the protocol to only use modern, secure cipher suites.
    SSLProtocol             all -SSLv2 -SSLv3
    SSLHonorCipherOrder     on
    SSLCipherSuite          ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA

    # Specify your DH params file as follows
    SSLOpenSSLConfCmd DHParameters "{path to dhparams.pem}"


.. _Guide to Deploying Diffie-Hellman for TLS: https://weakdh.org/sysadmin.html
.. _secure Apache configuration: http://www.apache-ssl.org/httpd.conf.example
