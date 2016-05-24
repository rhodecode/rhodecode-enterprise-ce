    LDAP Host hostname1,hostname2 # testing here
    Port port
    Account: `uid=admin,cn=users,cn=accounts,dc=localdomain,dc=tld`
    Password: userpassword #Testing this here
    Connection Security LDAPS
    Certificate Checks ``NEVER``
    Base DN cn=users,cn=accounts,dc=localdomain,dc=tld
    LDAP Search Filter (objectClass=person)
    LDAP Search Scope SUBTREE
    Login Attribute uid
    First Name Attribute givenname
    Last Name Attribute sn
    Email Attribute mail
