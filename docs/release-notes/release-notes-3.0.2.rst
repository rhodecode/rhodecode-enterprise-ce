|RCE| 3.0.2 |RNS|
-----------------

General
^^^^^^^
 * 2015-02-16

News
^^^^

 * Style: Overhaul of typography styling
 * Consistent use of product name in application
 * Action Parser: More robust handling of data
 * Permissions: More consistent sorting of permissions
 * Gists: Added a ``noindex`` flag for private Gists

Fixes
^^^^^

 * LDAP: renamed LDAP plugins for backwards compatibility. The original
   plugin is called ``auth_ldap`` and group support is with the
   ``auth_ldap_group`` plugin.
 * |svn|: Support "0" to get the first commit via API from Subversion
   repositories
 * Style: fixed display issues with select boxes in IE
 * Style: fixed highlighting of commits in compare view
 * Style: Preserve new-line breaks in commit messages
 * Style: fixed icons on code-block elements
 * Style: fixed side-by-side diff header
 * Style: fixed form-inputs on login pages
 * Style: fixed multiple minor display issues in the diff display