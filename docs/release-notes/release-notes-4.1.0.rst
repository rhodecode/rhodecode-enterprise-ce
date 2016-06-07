|RCE| 4.1.0 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

- 2016-06-XX

General
^^^^^^^

- Migrated more views to Pyramid. Those now include login, social plugins, search
- Started Implementing Pyramid Events system in exchange to rcextensions callbacks
- JS routes assets are now generated in development mode automatically
- ini: Add fallback authentication plugin setting. In case only one
  authentication backend is enabled users can now enable fallback auth if
  they cannot log-in due to external servers being down

New Features
^^^^^^^^^^^^

- search: add syntax highlighting, line numbers and line context to file
  content search results
- Go To switcher now searches commit hashes as well
- Token based authentication is now in CE edition as well
- User groups: added autocomplete widget to be able to select members of
  other group as part of current group.

Security
^^^^^^^^

- Added new action loggers for actions like adding/revoking permissions.
- permissions: show origin of permissions in permissions summary. Allows users
  to see where and how permissions are inherited

Performance
^^^^^^^^^^^



Fixes
^^^^^

- api: gracefully handle errors on repos that are damaged or missing
  from filesystem.
- logging: log the original error when a merge failure occurs
- #3965 Cannot change the owner of a user's group by using the API