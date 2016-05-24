|RCE| 1.6.0 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

 * released 2013-05-12

Fixes
^^^^^
 * #818: Bookmarks Do Not Display on Changeset View.
 * Fixed issue with forks form errors rendering.
 * #819 review status is showed in the main changelog.
 * Permission update function is idempotent, and doesn't override default permissions when doing upgrades.
 * Fixed some unicode problems with git file path.
 * Fixed broken handling of adding an htsts headers.
 * Fixed redirection loop on changelog for empty repository.
 * Fixed issue with web-editor that didn't preserve executable bit after editing files.
