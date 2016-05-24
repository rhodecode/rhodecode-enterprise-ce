|RCE| 3.4.1 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

* 2015-07-20

Packaging
^^^^^^^^^

- |RCT| are now bundled with |RCE| installations. This makes offline
  installations easier, and it also removes to need to install a separate
  ``virtualenv`` on your server.

Fixes
^^^^^

- Pull requests: Fixed an internal server error in case of a removed commit.
- VCS: Fix a performance regression around VCS operations.
