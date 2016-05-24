|RCE| 2.2.4 |RNS|
-----------------

General
^^^^^^^
 * released 2013-12-30
 * More secure output of a remote clone URL
 * Extended API calls
 * Support for latest Git versions

News
^^^^
 * Password in a remote clone URL are not displayed anymore.
 * Better Windows support on server info page.
 * Extended API: added permission delegation to grant/revoke calls.
 * Extended API: added copy_permissions flag to create_repo_group.
 * Extended API: added apply_to_children to grant/revoke methods of repo groups.

Fixes
^^^^^
 * Fixed forking into a repository group.
 * Fixed detection of remote Git repositories.
 * Fixed issue with API calls on repo names with groups.
 * Fixed unescaped characters which broke Javascript in the 2-side diff view.
 * Fixed git clone command by adding -q flag due to changes in the latest Git.
