|RCE| 2.2.1 |RNS|
-----------------

General
^^^^^^^
 * released 2013-10-25

News
^^^^
 * No news

Fixes
^^^^^
 * Fixed issue with forking.
 * Fixed redirection to previous location which was lost via container auth login.
 * API: removed urllib.unquote_plus on raw body. This caused a bug with '+' chars beeing stripped out of sent JSON BODY.