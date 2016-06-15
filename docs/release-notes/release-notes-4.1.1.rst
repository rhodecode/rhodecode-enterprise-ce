|RCE| 4.1.1 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

- 2016-06-14

Fixes
^^^^^

- security: fixed permissions issues on pyramid auth-plugins views.
  They no longer raise an internal server error page when accessed unauthorized.

- search: use better ElasticSearch repo filters. (EE only)
