.. _dh-nginx:

Diffie-Hellman Security
-----------------------

To secure your web server, the `Guide to Deploying Diffie-Hellman for TLS`_
contains important information worth reading. This link contains a good
`nginx secure configuration`_ example. The documentation below also contains
good security settings with some additional |RCE| specific examples.

To secure your deployment of Diffie-Hellman, configure the following:

* Generate a strong Diffie-hellman group, 2048-bit or stronger.

.. code-block:: bash

    # to generate your dhparam.pem file, run in the terminal
    openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

* Configure your server to only use modern, secure cipher suites in the
  virtual hosts configuration file.

.. code-block:: nginx

    # Set the TLS protocols and to only use modern, secure cipher suites.
    ssl_ciphers "ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA:ECDHE-RSA-DES-CBC3-SHA:EDH-RSA-DES-CBC3-SHA:AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-SHA256:AES128-SHA256:AES256-SHA:AES128-SHA:DES-CBC3-SHA:HIGH:!aNULL:!eNULL:!EXPORT:!DES:!MD5:!PSK:!RC4";
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;

    # Diffie-Hellman parameter for DHE ciphersuites, recommended 2048 bits
    ssl_dhparam /etc/nginx/ssl/dhparam.pem;

.. _Guide to Deploying Diffie-Hellman for TLS: https://weakdh.org/sysadmin.html
.. _nginx secure configuration: https://gist.github.com/plentz/6737338
