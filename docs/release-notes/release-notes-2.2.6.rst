|RCE| 2.2.6 |RNS|
-----------------

General
^^^^^^^
 * 2014-12-03

News
^^^^
 - Repository locking requires at least write permission to repository.
 - API: added add/remove methods for extra fields
 - New repositories/ repository groups should be created using 0755 mode not 0777
 - Added editable owner field for repository groups
 - Added editable owner field for user groups
 - API: Permission delegation on grant/revoke user permission functions
 - Auth plugin can create user creation state on first login
 - New license logic

Fixes
^^^^^
 - Fix issue with unicode email addresses in custom gravatar template
 - Protect against empty author string
 - Fixed issue with multiprocess setup and cached global settings
 - Fixed issues with IIS and proxied ports
 - Fixed issue with mysql column size on installing RhodeCode
 - Fixed issue with API call for update repo when a repo inside a group
   was badly renamed when doing those calls