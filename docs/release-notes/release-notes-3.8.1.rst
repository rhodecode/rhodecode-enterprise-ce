|RCE| 3.8.1 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

- 2016-03-10


General
^^^^^^^

- Fixed the problem due to a missing index when migrating from very old databases.
- Fixed problem with being unable to delete users which have set permissions on user groups.

Authentication
^^^^^^^^^^^^^^

- Take user group base DN in LDAP filtering.

API
^^^

- Better error handling if an inactive user account is used to make an API call.

VCS Server
^^^^^^^^^^

- Avoid error message around missing “object_store” being printed in logs.