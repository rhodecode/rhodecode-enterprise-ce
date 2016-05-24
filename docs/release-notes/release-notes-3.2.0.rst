|RCE| 3.2.0 |RNS|
-----------------

General
^^^^^^^
 * 2015-04-08

News
^^^^

- Administration: Improved the logging and rendering of tracebacks from the
  VCS Server. The logging configuration in the INI file should be updated.
  For information about these parts of |RCE|, see :ref:`vcs-server`, and
  :ref:`debug-mode`.
- Administration: Added the ability to set a per user language.
- Gists: Added an option to restrict gists to logged in users only.
- Pull requests: Reviewer status is reset after after an update.
- Pull requests: Improved logging during an update.
- Pull requests: Added various hooks around the life-cycle and review status
  changes of a |pr|.
- Security: Support added for `bcrypt`_ on Windows systems.
- Style: Added headers to tables which display commits, e.g. the changelog.
- Style: Redesigned the compare page for multiple commits.
- Style: Redesigned the error pages.
- Style: Redesigned the file details page.
- Style: Redesigned the summary pages of |repos|.
- Style: Improved the details form for managing authentication plugins.
- VCS Server: Robust push and pull operations if the VCSServer is restarted.

Fixes
^^^^^

- Administration: :ref:`remap-rescan` could cause issues with empty |repo|
  groups.
- Administration: Fix edit of an existing issue tracker entry.
- Comments: Allow to delete comments on regular commits.
- Comments: Fix batch comment functionality on the compare page.
- Diffs: Improve diff parser to better recognize special file names.
- |git|: Avoid errors when pushing into an empty |git| repository.
- File edit: Avoid internal server error for file edits on branches which are
  not the default branch.
- Pull requests: Show initial pull request comment.
- Security: Escape repository description to avoid XSS like vulnerabilities.
- Setup: Allow to setup a new system even with expired trial license.
- Style: Fixed styling of repository extra fields.
- Style: Fixed display issues on the file page when a line is selected and the
  history buttons are used to navigate back and forth.
- Style: Improve the display of the commit message on the file details page.
- Style: Improve :guilabel:`My Account` page for email addresses.
- Style: Improve :guilabel:`My Account` page for external user accounts, e.g. LDAP
- Style: Improve transition from file list to file details.
- Style: Remove light font face for improved readability on Windows.

.. _bcrypt: https://bcrypt.codeplex.com/