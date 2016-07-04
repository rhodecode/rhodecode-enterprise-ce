|RCE| 4.2.1 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

- 2016-07-04

Fixes
^^^^^

- ui: fixed empty labels caused by missing translation of JS components
- login: fixed bad routing URL in comments when user is not logged in.
- celery: make sure to run tasks in sync mode if connection to celery is lost.
