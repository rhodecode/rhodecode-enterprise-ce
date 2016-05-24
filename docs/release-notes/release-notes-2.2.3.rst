|RCE| 2.2.3 |RNS|
-----------------

General
^^^^^^^
 * released 2013-11-27
 * Asynchronous & more stable repo forking & creation
 * Inheritable repository group permissions

News
^^^^
 * Bumped Mercurial to 2.8.0.
 * Bumped Mergely to latest version.
 * Permissions from a repository group can be inherited to child repositories.
 * Added side-by-side diff link to compare files diff view.
 * Forking and creation of repositories can be done asynchronously via Celery.
 * Forking and creation of repositories is more stable in terms of concurrency and file system errors.
 * Added new visual option for number of records on admin 'data grids'.
 * Repository admins can add/delete repository extra fields.
 * Improved validators of remote clone urls for Git and Mercurial.

Fixes
^^^^^
 * Fixed page links at Gists which lost filter settings on click.
 * Fixed how auth plugins handle groups.
 * Fixed issue on mismatch of repository fork VCS type (Git or Mercurial).
 * Fixed admin UI forms which broke when using long names.
 * Fixed LookupError exceptions when ambiguous identifier was given.
 * Fixed issues which occured with Git under Windows.
