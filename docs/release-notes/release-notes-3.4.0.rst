|RCE| 3.4.0 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

 * 2015-07-06

News
^^^^

- API: Improved error handling in the calls `create_repo` and `update_repo`.
- API: Extend the call `create_repo`.
- API: Extend the call `update_repo`. It now supports the new parameter
  `fork_of`.
- API: Add new call `create_pull_request`.
- API: Rename call `changeset_comment` to `comment_commit`.
- General: Update many external dependencies to recent versions.
- General: Improved connection handling to the VCSServer in thread based
  scenarios.
- General: Generate replacement avatar images if Gravatar is not used.
- Hooks: Add the hooks `pre-push` and `pre-pull` for `rcextensions`.

Pull Requests
^^^^^^^^^^^^^

- Update inline comments during the update of a pull request. This can be
  enabled with a new option in the VCS settings.
- Always show information about the merge status.
- Allow to update the title and description of a pull request.
- Also allow the author to close a pull request.
- Order pull requests based on the numeric value instead of the
  string value.
- Disable merge if the target repository is locked.
- Fix link to commits of the pull request.
- Show update button in the case of missing commits.

Style
^^^^^

- Update of the page "Commit" to fit better into the current style.
- Update of the page "File" to fit better into the current style.
- Remove background color for closed pull requests.
- Standardise font sizes and spacing across the display of diffs and
  file sources.
- Use units from the binary system to display size information,
  e.g. `KiB` and `MiB`.
- Do not try to show gravatar images for group entries in select
  widgets.
- Style: Improve "increase context" and "ignore whitespace" links on the page
  "Commit".
- Show information in the profile of external users as read only.
- Improve spacing in the permissions overview of users and user groups.

Fixes
^^^^^

- Auth: Fix default user permissions for private repositories inside of a
  repository group.
- Auth: Do not inherit permissions from disabled user groups.
- Auth: Avoid generation of a new password for external user accounts on login.
- Files: Fix the handling of the file name extension on the page "Add File".
- Files: Fix the "Show all authors" link on the file page.
- General: Fix a filedescriptor leak inside of the WSGI processes around vcs
  operations.
- General: Fix system info page for Windows.
- General: Show version information in the footer if enabled.
- General: Avoid errors from the issue tracker patterns to bubble up in the
  system. Logging an error and ignoring the broken pattern instead.
- Gists: Store correct ACL level for anonymous gists.
- License: Ignore default user on user count.
- Repository: Clear user permissions when detaching related objects.
- Repository: Fix issue around tags with special characters for git.

VCS Server
^^^^^^^^^^

- Fix a filedescriptor leak around calls to git around vcs
  operations.
- Add solid handling of lookup errors and error during diff
  generation.
- VCSServer: Skip initialization of the locale subsystem if no valid locale can
  be found.
- VCSServer: Increased default value for the parameter `threadpool_size`.

Deprecations
^^^^^^^^^^^^

- API: The call `changeset_comment` is deprecated, use `comment_commit`
  instead. The old call will be still supported for a few more releases but
  eventually it will be removed.
