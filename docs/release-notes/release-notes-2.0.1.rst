|RCE| 2.0.1 |RNS|
-----------------

General
^^^^^^^
 * released 2013-08-14

News
^^^^
 * Create Pull-request button is visible for all logged in users, not only for those with a created repo permission set.
 * New UI on repository groups, now consistent with other views.
 * UI improvements on pull request reviewers.
 * Repository admin can revoke reviewers from pull requests.
 * Super admins can directly edit groups/users at permission box.
 * Links in footer point to website and new support pages.

Fixes
^^^^^
 * Fixed download button size.
 * Fixed empty dot occuring on page titles when no site customization was set.
 * Fixed issue #893, some static resources were called without url() leading to bad address when used with proxy prefix.
 * Fixed missing external values from user forms.
 * Fixed one Git call in pygrack that defaulted to hardcoded 'git' instead of customized path from RhodeCode settings.
 * Fixed issue with html on revoke buttons on pull request reviewers.
 * Fixed all occurences of bad permission check that didn't allow repository admins to do certain actions. Only global admins could run them.
 * Fixed gist url filtering for public gists.
 * Newly registered users now default to 'rhodecode' as authentication type.
 * Bumped Waitress version that allows setting `asyncore_use_poll` in settings to overcome 1024 open sockets limit with default `select()` implementation.