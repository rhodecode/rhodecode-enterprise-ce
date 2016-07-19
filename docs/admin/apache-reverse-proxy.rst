Apache Reverse Proxy
^^^^^^^^^^^^^^^^^^^^

Here is a sample configuration file for using Apache as a reverse proxy.

.. code-block:: apache

    <VirtualHost *:80>
            ServerName hg.myserver.com
            ServerAlias hg.myserver.com

            ## uncomment to serve static files by Apache
            ## ProxyPass /_static !
            ## Alias /_static /path/to/.rccontrol/enterprise-1/static

            <Proxy *>
              Order allow,deny
              Allow from all
            </Proxy>

            ## Important !
            ## Directive to properly generate url (clone url) for pylons
            ProxyPreserveHost On

            ## RhodeCode instance running
            ProxyPass / http://127.0.0.1:10002/
            ProxyPassReverse / http://127.0.0.1:10002/

            ## to enable https use line below
            #SetEnvIf X-Url-Scheme https HTTPS=1

    </VirtualHost>

