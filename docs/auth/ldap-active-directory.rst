.. _ldap-act-dir-ref:

Active Directory
----------------

|RCM| can use Microsoft Active Directory for user authentication. This is
done through an LDAP or LDAPS connection to Active Directory. Use the
following example LDAP configuration setting to set your Active Directory
authentication.

.. code-block:: ini
    
    # Set the Base DN
    Base DN              = OU=SBSUsers,OU=Users,OU=MyBusiness,DC=v3sys,DC=local
    # Set the Active Directory SAM-Account-Name
    Login Attribute      = sAMAccountName
    # Set the Active Directory user name
    First Name Attribute = usernameame
    # Set the Active Directory user surname
    Last Name Attribute  = user_surname
    # Set the Active Directory user email
    E-mail Attribute     = userEmail