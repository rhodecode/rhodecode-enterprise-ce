|RCE| 1.7.0 |RNS|
-----------------

General
^^^^^^^
 * released 2013-06-08

News
^^^^
 * Manage User's Groups(teams): create, delete, rename, add/remove users inside by delegated user group admins.
 * Implemented simple Gist functionality.
 * External authentication got special flag to control user activation.
 * Created whitelist for API access. Each view can now be accessed by api_key if added to whitelist.
 * Added dedicated file history page.
 * Added compare option into bookmarks
 * Improved diff display for binary files and renames.
 * Archive downloading are now stored in main action journal.
 * Switch gravatar to always use ssl.
 * Implements #842 RhodeCode version disclosure.
 * Allow underscore to be the optionally first character of username.

Fixes
^^^^^
 * #818: Bookmarks Do Not Display on Changeset View.
 * Fixed default permissions population during upgrades.
 * Fixed overwrite default user group permission flag.
 * Fixed issue with h.person() function returned prematurly giving only email info from changeset metadata.
 * get_changeset uses now mercurial revrange to filter out branches. Switch to branch it's around 20% faster this way.
 * Fixed some issues with paginators on chrome.
 * Forbid changing of repository type.
 * Adde missing permission checks in list of forks in repository settings.
 * Fixes #834 hooks error on remote pulling.
 * Fixes issues #849. Web Commits functionality failed for non-ascii files.
 * Fixed #850. Whoosh indexer should use the default revision when doing index.
 * Fixed #851 and #563 make-index crashes on non-ascii files.
 * Fixes #852, flash messages had issies with non-ascii messages