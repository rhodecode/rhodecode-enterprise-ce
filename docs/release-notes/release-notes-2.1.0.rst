|RCE| 2.1.0 |RNS|
-----------------

General
^^^^^^^
 * released 2013-09-25
 * Pull requests work for Mercurial and Git
 * New IP Whitelist inheritance
 * Ability to check for new update of RhodeCode Enterprise
 * Multiple API keys per user
 * Strong performance improvements
 * Shortcuts

News
^^^^
 * Added Git pull request functionality
 * Multiple API keys and the option to add additional API keys for a user together with description and expiration.
 * Users can now delete files via web interface.
 * Moved Gravatar configuration from .ini files to web interface.
 * Moved custom clone URL configuration from .ini files to web interface.
 * Default IP whitelist is now inheritable by all users. This allows to setup system-wide IP restrictions for all users.
 * Added intermediate waiting page for forks creation. After the fork is created the user is redirected to the forked
   repo summary page.
 * Next/prev links on changeset are now lazy calculated with onClick actions which can boost initial rendering speed
   of pages by 2-3x.
 * New repo switcher based on select2. Now with keyboard control and repository groups searching.Added basic keyboard
   navigation shortcuts, simply call '?' to show them.
 * Added check for update mechanism in web interface.
 * All alerts and confirmations can be closed with an 'x' button in the corner.
 * Updated Mercurial to 2.7.1
 * Updated Waitress to 0.8.7

Fixes
^^^^^
 * Updated Google Noto Sans web font to fix issues for older IE versions
 * Fixed Git backend calls to not use grep. Users are not required anymore to install it for Windows.
 * Fixed sorting by revision in dashboard view.
 * Container auth plugin preserves modified details after user is created and edited.
 * Fixed issue with deleting notifications for some users.
 * Fixed issue when external auth systems always regenerated tokens when user logged in (due to temp passwords on those
   accounts)
 * Fixed some JS errors on summary page.
 * Fixed issue when external auth plugins wanted to create new users after the free limit is reached and failed with an
   error.
 * Removed broken prerender calls in pagination.