|RCE| 3.3.0 |RNS|
-----------------

General
^^^^^^^
 * 2015-05-18

News
^^^^

- Administration: Clean up |repo| groups which have been deleted on the
  file system.
- Docs: Overhaul the section about integrations and extensions.
- Docs: Document how to configure the file `.rhoderc`
- Docs: Extend the documentation about the usage of Gunicorn and horizontal
  scaling.
- Docs: Document that we don't support the |git| dump protocol and provide a
  workaround for very old servers.
- General: Decouple from external links to allow easier maintenance.
- Pull requests: Show a warning message if the commits are missing in the
  source |repo| and suggest suitable next steps.
- Pull requests: New lab setting which enables the invalidation of inline
  comments during an update; currently all comments are invalidated.
- Pull requests: Add keyboard shortcut `g p` to navigate to the |prs|
  page of the current |repo|.
- Pull requests: Send notifications when a new reviewer is added to a |pr|.
- Pull requests: Show information about the target of a |pr|.
- Pull requests: Show progress after clicking the button "Update" on a |pr|.
- Pull requests: Show a more informative flash message after a successful
  update of a |pr|.
- Style: Unify how gravatars are displayed for a more consistent look.
- Style: Better display of the |pr| page in smaller browser windows for
  IE.
- Style: Better alignment of the status indicator in the list of reviewers of a
  |pr|.
- UX: Add flash message if a |repo| has been deleted in the file system.
- UX: Consistent usage of |authtoken| in the settings section.
- UX: Better help message for the authentication plugins configuration.
- VCSServer: Add support for an external configuration file.



Fixes
^^^^^


- API: Multiple fixes for the call `update_repo_group`, adjusting parent path
  if a new parent is specified and allow to update the owner.
- API: Fix the handling of boolean values in the call `create_repo`.
- API: Fix usage of the parameter `password` in the call `create_user`.
- API: Make the call `strip` more robust.
- Auth: Better support for the parameter "Base DN" in the plugin
  `auth_ldap_group`.
- Auth: Avoid concurrency issue when forking a |repo| and celery is
  enabled.
- Compare: Avoid duplication of diff content in the case of commit range
  comparison.
- DB: Improve `Pullrequest.revisions` to work even for empty |prs|.
- DB: Avoid extremely large varchar columns for MySQL and MariaDB
- Files: Fix an issue around "Compare to revision" for diffs which are bigger
  than the per file limit.
- Files: Present submodules with an absolute URL as real links.
- |Repo| settings: Allow to rename |svn| |repos|.
- Search: |Repo| search allows to use uppercase characters in |repo|
  names.
- Style: Gist header alignment issues fixed.
- Style: Line heights in side by side diff display improved.
- UX: Hide "Add comments" button if the comments form is already open.
- UX: Fix links of bookmarks and tags on the overview pages.
- VCSServer: More robust locale handling.
