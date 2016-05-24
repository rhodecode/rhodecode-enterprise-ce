Nginx Configuration Example
---------------------------

Use the following example to configure Nginx as a your web server.

.. code-block:: nginx

    upstream rc {

        server 127.0.0.1:5000;

        # add more instances for load balancing
        # server 127.0.0.1:5001;
        # server 127.0.0.1:5002;
    }

    ## gist alias

    server {
        listen          443;
        server_name     gist.myserver.com;
        access_log      /var/log/nginx/gist.access.log;
        error_log       /var/log/nginx/gist.error.log;

        ssl on;
        ssl_certificate     gist.rhodecode.myserver.com.crt;
        ssl_certificate_key gist.rhodecode.myserver.com.key;

        ssl_session_timeout 5m;

        ssl_protocols SSLv3 TLSv1;
        ssl_ciphers DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA:EDH-RSA-DES-CBC3-SHA:AES256-SHA:DES-CBC3-SHA:AES128-SHA:RC4-SHA:RC4-MD5;
        ssl_prefer_server_ciphers on;
        add_header Strict-Transport-Security "max-age=31536000; includeSubdomains;";

        # Diffie-Hellman parameter for DHE ciphersuites, recommended 2048 bits
        ssl_dhparam /etc/nginx/ssl/dhparam.pem;

        rewrite ^/(.+)$ https://rhodecode.myserver.com/_admin/gists/$1;
        rewrite (.*)    https://rhodecode.myserver.com/_admin/gists;
    }

    server {
        listen          443;
        server_name     rhodecode.myserver.com;
        access_log      /var/log/nginx/rhodecode.access.log;
        error_log       /var/log/nginx/rhodecode.error.log;

        ssl on;
        ssl_certificate     rhodecode.myserver.com.crt;
        ssl_certificate_key rhodecode.myserver.com.key;

        ssl_session_timeout 5m;

        ssl_protocols SSLv3 TLSv1;
        ssl_ciphers DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA:EDH-RSA-DES-CBC3-SHA:AES256-SHA:DES-CBC3-SHA:AES128-SHA:RC4-SHA:RC4-MD5;
        ssl_prefer_server_ciphers on;

        ## uncomment root directive if you want to serve static files by nginx
        ## requires static_files = false in .ini file
        # root /path/to/installation/rhodecode/public;

        include         /etc/nginx/proxy.conf;
            location / {
                try_files $uri @rhode;
            }

       location @rhode {
            proxy_pass      http://rc;
            }
    }
