.. _apache-conf-eg:

Apache Configuration Examples
-----------------------------

Use the following example to securely configure your Apache HTTP virtual hosts
file.

.. code-block:: apache

    <VirtualHost *:80>
        ServerName hg.myserver.com
        ServerAlias hg.myserver.com

        <Proxy *>
          Order allow,deny
          Allow from all
        </Proxy>

        # important !
        # Directive to properly generate url (clone url) for pylons

        ProxyPreserveHost On

        #rhodecode instance
        ProxyPass / http://127.0.0.1:5000/
        ProxyPassReverse / http://127.0.0.1:5000/

        # Set strict HTTPS
        Header always set Strict-Transport-Security "max-age=63072000; includeSubdomains; preload"

        # Set x-frame options
        Header always append X-Frame-Options SAMEORIGIN

        # To enable https use line below
        # SetEnvIf X-Url-Scheme https HTTPS=1

        # Secure your Diffie-hellmann deployment
        SSLProtocol             all -SSLv2 -SSLv3
        SSLCipherSuite          ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA
        SSLHonorCipherOrder     on
        SSLOpenSSLConfCmd DHParameters "{path to dhparams.pem}"

    </VirtualHost>

Use the following example to configure Apache for a multi-node setup. The
timeout setting should be increased if you experience timeouts when working
with large |repos|.

.. code-block:: apache

    #
    # Timeout: The number of seconds before receives and sends time out.
    #
    Timeout 600

    <VirtualHost *:80>

            ProxyRequests off

            #important !
            #Directive to properly generate url (clone url) for pylons
            ProxyPreserveHost On

            ServerName your.rce.com
            ServerAlias your.rce.com

            <Proxy balancer://mycluster>
                    # WebHead1
                    BalancerMember http://10.58.1.171:10002 route=1
                    # WebHead2
                    BalancerMember http://10.58.1.172:10001 route=2

                    # Security "technically we aren't blocking
                    # anyone but this the place to make those
                    # chages
                    Order Deny,Allow
                    Deny from none
                    Allow from all

                    # Load Balancer Settings
                    # We will be configuring a simple Round
                    # Robin style load balancer. This means
                    # that all webheads take an equal share of
                    # of the load.
                    ProxySet stickysession=ROUTEID

            </Proxy>

            # balancer-manager
            # This tool is built into the mod_proxy_balancer
            # module and will allow you to do some simple
            # modifications to the balanced group via a gui
            # web interface.
            <Location /balancer-manager>
                    SetHandler balancer-manager

                    # recommend locking this one down to your
                    # your office
                   Order deny,allow
                    Allow from all
            </Location>

            # Point of Balance
            # This setting will allow to explicitly name the
            # the location in the site that we want to be
            # balanced, in this example we will balance "/"
            # or everything in the site.
            ProxyPass /balancer-manager !
            ProxyPass / balancer://mycluster/

            ProxyPassReverse / balancer://mycluster/

    </VirtualHost>
