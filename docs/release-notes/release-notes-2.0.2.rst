|RCE| 2.0.2 |RNS|
-----------------

General
^^^^^^^
 * released 2013-08-27

News
^^^^
 * Completely new my account page.
 * Added created_on field for repository groups.
 * Users can now define extra email addresses in their account page.
 * Updated codemirror to latest version with Nginx, Jade, Smartymixed modes.
 * Better MIME-type detection of files with pygments to improve online editor syntax and mode detection.
 * Added option to enable Captcha on registration page. It helps fight spam on open RhodeCode Enterprise instances.

Fixes
^^^^^
 * Many fixes for Internet Explorer 8 and newer.
 * Fix largefiles user cache location by explicitly setting the location in RhodeCode database.
 * Fixed "Remove Pull Request" button HTML on "my account" page.
 * Allow admin flag control for external authentication accounts
 * Changed landing_rev format to <rev_type>:<rev> to overcome issues with same names in different rev types like
   bookmarks and branches.
 * Add strip to attr_login for LDAP Auth plugin which is a very sensitive about whitespaces. Leaving whitespaces in
   there causes hard to debug issues.