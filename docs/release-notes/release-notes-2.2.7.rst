|RCE| 2.2.7 |RNS|
-----------------

General
^^^^^^^
 * 2015-02-03

Fixes
^^^^^

 * Security: fixed severe issue with leaking of auth_tokens(api_keys) on the
   following API calls; ``get_repo``,
   ``update_repo``, ``get_locks``, and ``get_user_groups``.
