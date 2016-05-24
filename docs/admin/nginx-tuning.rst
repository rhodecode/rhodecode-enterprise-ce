.. _nginx-tuning:

Nginx Tuning
------------

Set the following properties in your ``/etc/nginx/proxy.conf`` so it does not
timeout during large pushes.

.. code-block:: nginx

    proxy_redirect              off;
    proxy_set_header            Host $host;

    ## needed for container auth
    # proxy_set_header            REMOTE_USER $remote_user;
    # proxy_set_header            X-Forwarded-User $remote_user;

    proxy_set_header            X-Url-Scheme $scheme;
    proxy_set_header            X-Host $http_host;
    proxy_set_header            X-Real-IP $remote_addr;
    proxy_set_header            X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header            Proxy-host $proxy_host;
    proxy_buffering             off;
    proxy_connect_timeout       7200;
    proxy_send_timeout          7200;
    proxy_read_timeout          7200;
    proxy_buffers               8 32k;
    # Set this to a larger number if you experience timeouts
    client_max_body_size        1024m;
    client_body_buffer_size     128k;
    large_client_header_buffers 8 64k;
    add_header X-Frame-Options SAMEORIGIN;
    add_header Strict-Transport-Security "max-age=31536000; includeSubdomains;";
