|RCE| 4.2.0 |RNS|
-----------------

Release Date
^^^^^^^^^^^^

- 2016-06-30


General
^^^^^^^

- Autocomplete: add GET flag support to show/hide active users on autocomplete,
  also display this information in autocomplete data.  ref #3374
- Gravatar: add flag to show current gravatar + user as disabled user (non-active)
- Repos, repo groups, user groups: allow to use disabled users in owner field.
  This fixes #3374.
- Repos, repo groups, user groups: visually show what user is an owner of a
  resource, and if potentially he is disabled in the system.
- Pull requests: reorder navigation on repo pull requests, fixes #2995
- Dependencies: bump dulwich to 0.13.0

New Features
^^^^^^^^^^^^

- My account: made pull requests aggregate view for users look like not
  created in 1995. Now uses a consistent look with repo one.
- emails: expose profile link on registation email that super-admins receive.
  Implements #3999.
- Social auth: move the buttons to the top of nav so they are easier to reach.


Security
^^^^^^^^

- Encryption: allow to pass in alternative key for encryption values. Now
  users can use `rhodecode.encrypted_values.secret` that is alternative key,
  de-coupled from `beaker.session` key.
- Encryption: Implement a slightly improved AesCipher encryption.
  This addresses issues from #4036.
- Encryption: encrypted values now by default uses HMAC signatures to detect
  if data or secret key is incorrect. The strict checks can be disabled using
  `rhodecode.encrypted_values.strict = false` .ini setting


Performance
^^^^^^^^^^^

- Sql: use smarter JOINs when fetching repository information
- Helpers: optimize slight calls for link_to_user to save some intense queries.
- App settings: use computed caches for repository settings, this in some cases
  brings almost 4x performance increase for large repos with a lot of issue
  tracker patterns.


Fixes
^^^^^

- Fixed events on user pre/post create actions
- Authentication: fixed problem with saving forms with errors on auth plugins
- Svn: Avoid chunked transfer for Subversion that caused checkout issues in some cases.
- Users: fix generate new user password helper.
- Celery: fixed problem with workers running action in sync mode in some cases.
- Setup-db: fix redundant question on writable dir. The question needs to be
  asked only when the dir is actually not writable.
- Elasticsearch: fixed issues when searching single repo using elastic search
- Social auth: fix issues with non-active users using social authentication
  causing a 500 error.
- Fixed problem with largefiles extensions on per-repo settings using local
  .hgrc files present inside the repo directory.
