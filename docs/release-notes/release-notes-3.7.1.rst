|RCE| 3.7.1 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

- 2015-12-10

Security
^^^^^^^^

Removed logging of masked authentication tokens completely. This prevents
potentially logging parts of a user's password if they are not using tokens.

Admin
^^^^^

- Created the ability for |RCE| to auto-detect |hg| |repos| which require the
  *Largefiles* extension during *Remap and Rescan* operations.
- Allow the admin of a repository group to change the group's settings even if
  he/she does not have admin permission for the parent |repo| group.

Authentication
^^^^^^^^^^^^^^

Fixed support for non-ascii characters in passwords when authenticating
using external authentication tools such as LDAP.

Pull Requests
^^^^^^^^^^^^^

- Fixed an issue when merging Mercurial pull requests which are not based on
  branch names.
- Fixed generated URL creation when |RCE| is running under a URL prefix.

|SVN|
^^^^^

Fixed streaming issues when using Gunicorn based setups.

User Experience
^^^^^^^^^^^^^^^

Improved avatar rendering stability. Especially in the case of an invalid
email address being used with an external authentication backend.

