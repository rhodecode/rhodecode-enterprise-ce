|RCE| 4.0.0 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

- 2016-05-24

General
^^^^^^^

- Introduced Pyramid as a Pylons framework replacement. (porting still ongoing).
  Added few of components as plugins. Exposed RhodeCode plugins API for 3rd
  parties to extend RhodeCode functionality with custom pyramid apps. Pyramid
  is also our route to python3 support.
- Various UX/UI improvements.
  - new summary page
  - new file browser (more consistent)
  - re-done admin section and added Panels
  - various other tweaks and improvements
- Alternative fast and scalable HTTP based communication backend for VCServer.
  It soon will replace Pyro4.
- Rewrote few caching techniques used and simplified those


New Features
^^^^^^^^^^^^

- RhodeCode code-review live chat (EE only). A live communication
  tool built right into the code-review process to quickly
  collaborate on crucial parts of code.

- Elastic Search backend (EE only). Alternative backend to existing
  Whoosh to handle, large amount of data for full text search.

- Social Auth (EE only): added new social authentication backends including:
  Github, Twitter, Bitbucket and Google. It's possible now to use your
  Google account to log in to RhodeCode and take advantage of things like 2FA.

- Search: full text search now properly orders commits by date, and shows line
  numbers for file content search.


Security
^^^^^^^^

- Added new action loggers for actions like adding/revoking permissions.


Performance
^^^^^^^^^^^

- Optimized admin panels to faster load large amount of data
- Improved file tree loading speed
- New HTTP backend is ~10% faster, and doesn't require so many threads
  for vcsserver


Fixes
^^^^^

- Fixed backreferences to user group when deleting users
- Fixed LDAP group user-group matching
- Improved SVN support for various commands (MKOL, etc)