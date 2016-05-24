|RCE| 1.7.1 |RNS|
-----------------

General
^^^^^^^
 * released 2013-06-13

News
^^^^
 * Apply to children flag on repository group also adds users to private repositories, this is now consistent with user groups. Private repos default permissions are not affected by apply to children flag.
 * Removed unionrepo code as it's part of Mercurial 2.6
 * RhodeCode accepts now read only paths for serving repositories.

Fixes
^^^^^
 * Fixed issues with how mysql handles float values. Caused gists with expiration dates not work properly on MySQL.
 * Fixed issue with ldap enable/disable flag.