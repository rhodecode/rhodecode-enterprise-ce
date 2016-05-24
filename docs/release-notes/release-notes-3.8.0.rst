|RCE| 3.8.0 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

- 2016-02-10


Authentication
^^^^^^^^^^^^^^

- Mercurial: Added an option to avoid a loop when the password is wrong during
  VCS operations. This prevents accounts in external systems being locked
  due to too many login attempts from Mercurial. See the :ref:`hg-auth-loop`
  section for more details.
- Auth: Speed improvements in the permission calculation of API calls.

API
^^^

- Added a new method, `update_pull_request`, which allows users to
  update a pull request using the API.

Deprecation
^^^^^^^^^^^

- Support for Internet Explorer 9 ends with this release.

Pull Requests
^^^^^^^^^^^^^

- Added functionality that now automatically fills the title and description
  fields based on the forks or branches involved, and the commit messages.
- Added a new URL endpoint which redirects to the pull request page
  for a given pull request ID. This is intended to support automation of
  specific work flows. The URL is ``/pull_requests/<pull_request_id>``.
- Removed the :guilabel:`Close Pull Request` button. This functionality is
  still available in the status drop-down menu below the comment box.
- Improved the merge logic so that merges on the same branch are
  possible even if the reference type is not a branch, e.g. bookmark, tag, or
  a raw commit ID.
- Escaped the description field to prevent potential XSS attacks.

UI/UX
^^^^^

**D**

- Diff: Fixed display issues around side-by-side diffs.
- Diff: The side-by-side diff has been enhanced. Small arrows now allow you to
  jump to the next or previous change, and an editor mode is available as a
  helper for complex diffs.

**F**

- Files: Allow users to add empty files through the web interface.
- Files: Do not prompt users without write permissions to add files to an empty
  repository.
- Files: Prevent submitting multiple times when editing a file.
- Files: Render files with the extension :file:`.txt` as plain text.
- Files: Use the correct file name extension for markdown files.

**J**

- Journal: Fixed display issues in the admin journal.
- Journal: Improved the display of query examples for the search feature.

**L**

- License: The amount of active users is now shown on the license page and
  provides the ability to disable users in bulk mode.

**R**

- Repository group: The buttons to add a repository or a repository group are
  now displayed only if the user has those permissions for the current
  repository group.
- Repository: A more informative message is now displayed in case a Mercurial
  repository depends on the *largefiles* extension, but this extension is not
  enabled.
- Repository: Fixed the loading of the commit summary to avoid an additional
  page reload.

**S**

- Style: The text alignment around the settings area was improved.
- Style: IE10 no longer shows a wrong background color in the select widgets.
- Style: Small corrections in the navigation around the :guilabel:`My Account`
  menu.
- Style: Consistent display of user names in tabular lists of repositories
  and repository groups.
- Style: Adjust the help text around the gravatar in the profile page.
- Style: Added consistent use of the term *Commit* instead of a mix of
  *Changeset* and *Revision*.
- Style: Restrict the value for custom branding to 40 characters.
- Style: Consistent rendering of markdown content.
- Subversion: Display the clone URL as read only and show a detailed help
  message for Subversion repositories if the HTTP proxy for write access is not
  enabled.

Logging
^^^^^^^

- Logging: Added logging details about the added and removed users when a user
  group is updated.
- Logging: Removed excessive error logging when detecting the server address.
- Logging: Improvements to avoid an early import of Pyro4, this is important
  for advanced setups using asynchronous workers.

VCS Server
^^^^^^^^^^

- VCS Server: Keep the remote traceback in case of a remote exception. This
  results in more precise information in the log files and helps to track down
  problems easier.
- VCS Server: Only write a PID file if requested via the command line.
- VCS Server: Explicitly close file descriptors for Git based operations to
  avoid a potential leak of file descriptors.

General
^^^^^^^

**A**

- Admin: Fixed a bug that disallowed admins from deleting users which had
  entries in the IP whitelist.

**C**

- Compare: Return a **404 Not Found** when comparing a missing commit. This
  makes it consistent with the unified diff.
- Compare: Various fixes around the selection of the source and target commit.

**G**

- General: Allow admins to inject the initial API key in `setup_rhodecode`. This
  simplifies the bootstrapping of automated setups.
- General: Added the ``pool_recycle`` option to the example :file:`.ini` file.
- General: Updated `CodeMirror`_ to 5.4.0.
- General: Speed improvements in multiple places which allow users to select a
  repository or a repository group.
- Repository: Increase the maximum size for repository names and the clone URL
  to prevent problems in deeply nested structures.
- General: Avoid invalid email addresses causing issues when rendering
  avatar images when external authentication modules are used.

**R**

- Repository: Enable the Mercurial *largefiles* extension during the run of
  *Remap & Rescan*. This detects *largefiles* repositories and adds them to
  the system.
- Repository: Robust forking of Mercurial repositories which depend on the
  *largefiles* extension in cases where this extension is not globally
  enabled.
- Repository: Made the query of very large commit sets more robust on
  MySQL. This affects cases when more than 500 commits are involved.

**S**

- Settings: Save the correct value when disabling *largefiles* for a repository.
- Settings: Add misdirection to external links in the issue tracker settings.
- Settings: Avoid a jumping lock button in the case of a validation error being
  displayed.
- Settings: Speed up the repository settings by delaying the query for the fork
  selection element.

.. _CodeMirror: https://codemirror.net/
