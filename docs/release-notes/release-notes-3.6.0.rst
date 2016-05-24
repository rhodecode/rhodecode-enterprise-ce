|RCE| 3.6.0 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

* 2015-10-19

Pull Requests
^^^^^^^^^^^^^

- The :guilabel:`Inline Comments` notification now links to the
  first inline comment, enabling faster comment navigation.
- Added a link to inline comments which links to the the
  previous and next one, enabling faster comment navigation.
- Pull request handling has been made more robust to avoid an internal server
  error after an update which had commits removed or stripped from the
  repository.

User Experience
^^^^^^^^^^^^^^^

- Consistent date display in the list of |repo| forks, multi-commit
  compare view.
- Consistent sorting of the permissions box on the various settings pages.
- A yellow indicator has been added to highlight the selected inline comment
  on a pull request.
- The expand button for commit messages now works to minimize also.
- Language improvements on various settings pages to clarify user options.
- Consistent sorting of |repo| permissions so that it is easier to find
  specific users for |repos| which have many permission entries.

API
^^^

- Added a new API call ``get_license_info`` which provides details about
  the current license to automate processing.
- Added a new API call ``set_license_key`` which allows the license key to
  be set via the API.

News
^^^^

- General: Updated the hgsubversion module to prepare for the update to a more
  recent |hg| version.
- General: Added an overview of external dependencies and their licenses.
- Repository: Link Git submodules if they point to a full URL.
- Settings: Extend the internal settings handling to prepare for per repository
  settings.

VCS Server
^^^^^^^^^^

- VCS Server: Support IPv6 addresses in the VCS Server configuration.
- VCS Server: Prepare for the Mercurial update to version 3.5.

Fixes
^^^^^

- Admin: Fill default values in the :guilabel:`Global permissions` form for user
  settings.
- Admin: Improve the issue tracker form patterns, especially when
  editing an existing pattern.
- Admin: Bring back the :guilabel:`Admin` column into the users overview. Use
  symbols for both Boolean states.
- Auth: Avoid querying all groups when using LDAP.
- Compare: Do not offer the comment button if the comparison is empty.
- DB: Migrate the locking information for repositories to a three tuple for
  old entries.
- DB: Add tables to support per repository settings.
- Diff: Remove link from context lines in diffs.
- Files: Preview functionality when editing RST files.
- General: Avoid logging an error if a commit with a not existing hash is
  requested.
- General: Fix scrolling to inline comments for Firefox browsers based on the
  anchor from the URL.
- Gist: Fix display in IE8 for very long lines.
- Git: Support branch names which include ``/``.
- Repository: Keep line breaks in the repository description.
- Search: Fix an issue around the highlighting of search results. Sometimes
  matches were not highlighted when there were multiple matches in one line.

Style
^^^^^

- Fixed overlapped displaying of notifications when a new user registers an
  account.
- Consistent display of labels for version control tags.
- Better alignment of the changelog graph.
- Fix rendering of the avatar images on IE9.
- Adjust the button style on the user profile edit page.
- Consistent styling of :guilabel:`Delete` buttons.
- Changelog graph for Subversion repositories was not aligned well.
- Changelog filter button style corrected.
- Adjust link colors in password forgotten form.
- Alignment of file names in diffs.
- Adjust the alignment of the permission summary title for user groups.
- Adjust the colour of form labels in the login and register forms.
- Remove the scroll bars from text areas in IE9.
