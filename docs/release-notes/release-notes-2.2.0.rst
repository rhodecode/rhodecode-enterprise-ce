|RCE| 2.2.0 |RNS|
-----------------

General
^^^^^^^
 * released 2013-10-23
 * Gists are editable
 * New keyboard shortcuts
 * Improved permission management
 * Speed improvements
 * Security improvements

News
^^^^
 * Gists are editable.
 * Gist URLs can take revisions as last parameter.
 * New keyboard shortcuts 'gg' and 'gG' open private/public Gists page.
 * New keyboard shortcut 'gF' opens files page with loaded files filter.
 * New keyboard shortcut 'gO' opens repository permissions settings.
 * 'Apply to children' becomes a 4-state radio button. It allows appling permissions to child objects of a repository group that are only repositories or only groups or both or none.
 * New permission for controlling repository creation with write access on repository groups.
 * Codemirror mode has added functionality of detection based on filename.
 * Added get_user function to auth plugins base. Can be overriden to customize other than standard user extraction, like the one needed for container auth.
 * API: added methods for permission managements for repo groups.
 * API: get_nodes API function is now callable not only by users with admin permissions but also with at least read permissions to a given repo.
 * Added stand-alone binary scripts for API, Gist, backup and extensions.
 * Extensions has additional notification plugins. Builtin plugins hipchat (hipchat notification on push), push_post( POST data after push). Use 'rhodecode-extensions --plugins' to install them.
 * Added captcha field to password_reset form.
 * Removed mailto: links, for better anti-spam protection on open instances.
 * Twice as fast page load of repository settings subpages.
 * Added checkbox in Map & Scan Admin Setting to verify and install any missing Git hooks that RhodeCode uses.
 * Bumped mako templates version to 0.9.0.
 * Bumped dulwich version to 0.9.3
 * Bumped mercurial version to 2.7.2.

Fixes
^^^^^
 * Fixed issue with container_auth tring to auth against non-container users.
 * Fixed issues when authentication via container failed on Git/hg operations when using non standard (REMOTE_USER) headers.
 * Fixed some JSON decode issue in Atlassian crowd auth plugin.
 * Fixed Git-related issue that didn't allow to push a non-master branch on the first push to the server.
 * Fixed issue on delete_user_group API call.
 * Fixed styling of password reset and register forms.
 * Fixed issue with Mercurial ui() object generation that caused certain extensions like hgsubversion to work incorrectly.
 * Fixed issue with revoked access to repo group for admins of repos inside those groups. In that case editing of these repos no longer causes an error.
 * Fixed sorting issues on tags/bookmarks/branches views.
 * Fixed issue when performing 'git update-server-info' while importing existing Git repositories. It makes sure now that clients can clone it.