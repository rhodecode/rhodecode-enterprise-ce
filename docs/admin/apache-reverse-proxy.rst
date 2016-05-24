Apache Reverse Proxy
^^^^^^^^^^^^^^^^^^^^

Here is a sample configuration file for using Apache as a reverse proxy.

.. code-block:: apache

    <VirtualHost *:80>
            ServerName hg.myserver.com
            ServerAlias hg.myserver.com

            ## uncomment root directive if you want to serve static files by nginx
            ## requires static_files = false in .ini file
            DocumentRoot /path/to/installation/rhodecode/public

            <Proxy *>
              Order allow,deny
              Allow from all
            </Proxy>

            #important !
            #Directive to properly generate url (clone url) for pylons
            ProxyPreserveHost On

            #rhodecode instance
            ProxyPass / http://127.0.0.1:5000/
            ProxyPassReverse / http://127.0.0.1:5000/

            #to enable https use line below
            #SetEnvIf X-Url-Scheme https HTTPS=1

    </VirtualHost>

