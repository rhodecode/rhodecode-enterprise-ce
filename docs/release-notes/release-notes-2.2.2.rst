|RCE| 2.2.2 |RNS|
-----------------

General
^^^^^^^
 * released 2013-11-19
 * Push & pull up to 4x faster
 * Security fixes

News
^^^^
 * Optimized the number of permission tree builds when doing push and pull operations which leads to a significant (up
   to 4x) performance increase.

Fixes
^^^^^
 * Fixed issue with pygrack using os.cwd for working dir, that caused issues in some operating systems.
 * Fixed dulwich parents function call used when building DAG graph.
 * Fixed issue with revoke permissions on repository group when apply to children was set to 'none'. This call could
   silently fail without proper notification to users.
 * Fixed issues with Mercurial hooks when creating remote repositories.
 * Strip passwords from clone urls for logging output.
 * Fixed LDAP issues with unicode. LDAP bind does not support unicode passwords.
 * Fixed admin UI which broke when using long names.
 * Fixed rendering of READMEs that contained different line endings.
 * Fixed issue with admin users of groups which could create repositories at top-level.