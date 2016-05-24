|RCE| 3.7.0 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

- 2015-11-09

Pull Requests
^^^^^^^^^^^^^

- Added a |pr| update overview which lists the added, updated, and removed
  files as an automated comment each time a |pr| is updated.
- The :guilabel:`Comment` functionality is no longer displayed on closed
  |prs|.
- Main comments which don’t change the review status are now submitted via
  ajax, and no longer require a page refresh.

Repository Settings
^^^^^^^^^^^^^^^^^^^

Added per |repo| settings functionality, and these override the global
settings. You can now configure the following settings per |repo|. For more
information, see the :ref:`permissions-info-add-group-ref` section.

- The VCS settings on the
  :menuselection:`Admin --> Repo name --> Edit --> VCS` page.
- The Issue Tracker settings on the
  :menuselection:`Admin --> Repo name --> Edit --> Issue Tracker` page.

Fixes
^^^^^

- Auth: Updated authentication logging to avoid logging an error if a user does
  not yet exist in the database.
- Admin: Fixed a redirect issue when clicking the admin menu.
- Style: Fixed misaligned previous/next |pr| comment links.
- Repository Scan: Fixed a potential race condition during initial |repo| scan. 

User Experience
^^^^^^^^^^^^^^^

- Buttons: Fixed comments duplicating when someone clicks the
  :guilabel:`comment` button multiple times.
- Buttons: Fixed an error showing when someone clicks the :guilabel:`delete`
  button multiple times.
- Auto Complete: Optimized the user autocomplete listing performance.

News
^^^^

- Mercurial: Changing large files settings now works without having to
  restart the |RCE| instance.
- Settings: The issue tracker patterns form now save changes in bulk
  rather than having to save changes individually.

Style
^^^^^

- Multiple tweaks for IE8 around alert messages and the changelog display.
- Adjusted the styling of the |pr| merge and preview buttons for comments.

Deprecations
^^^^^^^^^^^^

- Internet Explorer 8. This is the last release which officially supports IE8.
