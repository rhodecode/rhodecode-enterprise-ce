|RCE| 1.7.2 |RNS|
-----------------

General
^^^^^^^
 * released 2013-07-18

News
^^^^
 * Added handling of copied files in diffs.
 * Implemented issue #387 side-by-side diffs view.
 * Added option to specify other than official bugtracker url to post issues with RhodeCode.
 * Markdown renderer now uses github flavored syntax with a better newline handling
 * Added User pre-create, create and delete hooks for rcextensions.
 * Branch selectors: show closed branches too for Mercurial.
 * Updated codemirror to latest version and added syntax coloring dropdown for various languages CodeMirror supports.
 * Added --no-public-access / --public-access flags into setup-rhodecode command to enable setup without public access.
 * Various small updates to pull requests.
 * Bumped Mercurial version to latest.
 * Diffs view doesn't show content of delete files anymore.

Fixes
^^^^^
 * Added missing __get_cs_or_redirect method for file history. Fixes issue with displaying a history of file that is not present at tip.
 * Pull request: urlify description and fix javascript injection.
 * Fixed some missing IP extraction for action logger.
 * Fixed bug with log_delete hook didn't properly store user who triggered delete action.
 * Fixed show as raw link for private gists.
 * Fixes issue #860. IMC web commits poisoned caches when they failed with commit.
 * Fixes issue #856 file upload >1000 bytes on windows throws exception.