|RCE| 4.1.2 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

- 2016-06-16

Fixes
^^^^^

- ssl: fixed http middleware so it works correctly with pyramid views. This
  fixed http -> https redirection problems on login.

- ldap: fixed ldap usergroup authentication plugin so after upgrade it's
   possible to change the settings again (EE only).
