.. _ldap-gloss-ref:

|LDAP| Glossary
---------------

This topic aims to give you a concise overview of the different settings and
requirements that enabling |LDAP| on |RCE| requires.

Required settings
^^^^^^^^^^^^^^^^^

The following LDAP attributes are required when enabling |LDAP| on |RCE|.

* **Hostname** or **IP Address**: Use a comma separated list for failover
  support.
* **First Name**
* **Surname**
* **Email**
* **Port**: Port `389` for unencrypted LDAP or port `636` for SSL-encrypted
  LDAP (LDAPS).
* **Base DN (Distinguished Name)**: The Distinguished Name (DN)
  is how searches for users will be performed, and these searches can be
  controlled by using an LDAP Filter or LDAP Search Scope. A DN is a sequence of
  relative distinguished names (RDN) connected by commas. For example,
      
.. code-block:: vim
    
    DN: cn='Monty Python',ou='people',dc='example',dc='com'
            
* **Connection security level**: The following are the valid types:
   
  * *No encryption*: This connection type uses a plain non-encrypted connection.
  * *LDAPS connection*: This connection type uses end-to-end SSL. To enable
    an LDAPS connection you must set the following requirements:

      * You must specify port `636`
      * Certificate checks are required.
      * To enable ``START_TLS`` on LDAP connection, set the path to the SSL
        certificate in the default LDAP configuration file. The default
        `ldap.conf` file is located in `/etc/openldap/ldap.conf`.

.. code-block:: vim
    
   TLS_CACERT	/etc/ssl/certs/ca.crt

* The LDAP username or account used to connect to |RCE|. This will be added
  to the LDAP filter for locating the user object.
* For example, if an LDAP filter is specified as `LDAPFILTER`,
  the login attribute is specified as `uid`, and the user connects as
  `jsmith`, then the LDAP Filter will be like the following example.
      
.. code-block:: vim
                      
   (&(LDAPFILTER)(uid=jsmith))
    
* The LDAP search scope must be set. This limits how far LDAP will search for
  a matching object.

  * ``BASE`` Only allows searching of the Base DN.
  * ``ONELEVEL`` Searches all entries under the Base DN,
    but not the Base DN itself.
  * ``SUBTREE`` Searches all entries below the Base DN, but not Base DN itself.
      
.. note::
            
   When using ``SUBTREE`` LDAP filtering it is useful to limit object location.
 
Optional settings
^^^^^^^^^^^^^^^^^

The following are optional when enabling LDAP on |RCM|
 
* An LDAP account is only required if the LDAP server does not allow
  anonymous browsing of records.
* An LDAP password is only required if the LDAP server does not allow
  anonymous browsing of records
* Using an LDAP filter is optional. An LDAP filter defined by `RFC 2254`_. This
  is more useful that the LDAP Search Scope if set to `SUBTREE`. The filter
  is useful for limiting which LDAP objects are identified as representing
  Users for authentication. The filter is augmented by Login Attribute
  below. This can commonly be left blank.
* Certificate Checks are only required if you need to use LDAPS.
  You can use the following levels of LDAP service with RhodeCode Enterprise:

   * **NEVER** : A serve certificate will never be requested or checked.
   * **ALLOW** : A server certificate is requested. Failure to provide a
     certificate or providing a bad certificate will not terminate the session.
   * **TRY** : A server certificate is requested. Failure to provide a
     certificate does not halt the session; providing a bad certificate
     halts the session.
   * **DEMAND** : A server certificate is requested and must be provided
     and authenticated for the session to proceed.
   * **HARD** : The same as DEMAND.

.. note::

   Only **DEMAND** or **HARD** offer full SSL security while the other
   options are vulnerable to man-in-the-middle attacks.

   |RCE| uses ``OPENLDAP`` libraries. This allows **DEMAND** or
   **HARD** LDAPS connections to use self-signed certificates or
   certificates that do not have traceable certificates of authority.
   To enable this functionality install the SSL certificates in the
   following directory: `/etc/openldap/cacerts`


.. _RFC 2254: http://www.rfc-base.org/rfc-2254.html