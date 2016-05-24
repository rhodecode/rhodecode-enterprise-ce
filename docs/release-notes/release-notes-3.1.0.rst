|RCE| 3.1.0 |RNS|
-----------------

General
^^^^^^^
 * 2015-03-17

News
^^^^

- API: extended the API regarding |prs|. Added the following operations to
  support CI integrations.

  * ``get_pull_request``
  * ``get_pull_requests``
  * ``merge_pull_request``
  * ``close_pull_request``
  * ``comment_pull_request``

- VCS Server: improved handling for the user in the event that no
  VCS Server is enabled.
- VCS Server: Added the ``vcs.server.enable`` configuration option,
  see :ref:`vcs-server`
- VCS Server: improved system stability if the VCS Server is not installed.
- Style: changed icon colors for the vcs back ends; Git,
  Mercurial and Subversion.

Fixes
^^^^^

- Security: fixed XSS vulnerability in files view.
- Pull Request: fixed dataTable integration for IE8 in Pull Request overview.
- Files: adding a new file via web form has been fixed.
- Diff: renames of files which have spaces in their file names are now displayed
  correctly.
- Settings: Remove supervisor statistics page.
- Style: improved headers on all Pull Request related pages to make them more
  consistent.
- Style: improved headers on all repository related pages to make them more
  consistent.
- Style: updated icons.
- Style: removed border around checkboxes in IE10.
- Style: improved display of permission summaries in admin settings for all
  browsers.
- Style: fixed alignment of form labels across all browsers.
- Style: improved title on the Changeset page.
- Style: fixed display of select widgets in IE8 and IE9.
- Style: fixed password input field for IE8.
- Style: fixed button positioning in inline comment forms of diffs for IE8.
