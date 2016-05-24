|RCE| 3.0.0 |RNS|
-----------------

As |RCM| 3.0 is a big release, the release notes have been split into the following sections:

* :ref:`general-rn-ref`
* :ref:`security-rn-ref`
* :ref:`api-rn-ref`
* :ref:`performance-rn-ref`
* :ref:`prs-rn-ref`
* :ref:`gists-rn-ref`
* :ref:`search-rn-ref`
* :ref:`fixes-rn-ref`

.. _general-rn-ref:

General
^^^^^^^
 * Released 2015-01-27
 * Basic |svn| support added
 * GPLv3 components removed
 * Server/Client architecture for VCS systems created
 * Python 2.5 and 2.6 support deprecated
 * Server info pages now show gist/archive cache storage, and also CPU/Memory/Load information.
 * Added new bulk commit (changeset) status comment form into compare view which enables bulk code-reviews without
   opening a pull-request.
 * License checks and limits now only apply to active users.
 * Removed CLI command for |repo| scans as it can be done via an API call.
 * VCS backends can be globally enabled/disabled from the :file:`rhodecode.ini` file.
 * Added a UI option to set default rendering to rst or markdown.
 * Added syntax highlighting to 2 way compare diff.
 * Markup rendering can now render checkboxes for easy checklists generation.
 * Gravatars are now retina ready.
 * Admins can define custom CSS or JavaScript in the header or footer via new pre/post code options.
 * Replaced ``graph.js`` with ``commits-graph.js`` html5 implementation.
 * Added editable owner field for repository groups, and user group.
 * Added an option to detach/delete user repositories when deleting users from the system.
 * Added a Supervisor control page that shows status of processes.
 * User admin grid can now filter by username OR email.
 * Added personal |repo| group link for easier fork creation.
 * Added support for using subdirectories when creating and uploading new files.
 * Added option to rename a file from the web interface.
 * Added arrow key navigation to file filter and fixed the back button behaviour.
 * Added fuzzy matching to file filter.
 * Added functionality to create folder structures along with files when adding content via the web interface.
 * Separated default permissions UI into `global`, `user`, or `object` permissions management.
 * Added an inheritance flag to object permissions which allows for explicit permissions which disregard global
   permissions.
 * Added post create repository group hook.
 * Added trigger push hooks on online file editor.
 * Added default title for pull request.
 * More detailed logs during Authentication.
 * More explicit logging when permission checks occur.
 * Switched the implementation of |git| ``fetch clone pull checkout`` commands to pure |py| without any subprocess
   calls.
 * Introduced the ``rcserver`` command for custom development.
 * Added the ability to force no cache archived via the ``GET no_cache`` flag

.. _security-rn-ref:

Security
^^^^^^^^

 * CSRF (Cross-Site Request Forgery) tokens now in all pages that use forms.
 * The ``clone_url`` field is now AES encrypted inside the database.
 * ACLs (Access Control Lists) are checked on the gist edit page for logged in users.
 * New repository groups and repositories are created with 0755 permissions and not not 0777.
 * Explicit RSS tokens are used for the RSS journal, when leaked, limits access to RSS only.
 * Fixed XSS issues when rendering raw SVG files.
 * Added force password reset option for users.
 * IP list now accepts comma-separated values, and also ranges using `-` to specify multiple addresses.
 * Added ``auth tokens``, these authentication tokens can be used as an alternative to passwords.
 * Added roles (``http, api, rss, all, vcs``) into authentication tokens (previously called ``apikeys``).
 * LDAP Group Support added.
 * Added JASIG CAS auth plugin support.
 * Added a plugin parameter that defines if a plugin can create new users on the fly.

.. _api-rn-ref:

API
^^^
 * Added permissions delegation when creating |repos| or |repo| groups.
 * Added ``strip`` support for |hg| and |git| |repos|.
 * Added comments API for commits.
 * Added add/remove methods for extra fields in repositories.
 * ``get_*`` calls now use ``permission()`` and ``permission_user_group()`` methods for unified permissions structure.
 * ``get_repo_nodes`` information sending has changed and is no longer a boolean flag, it's now ``basic`` or ``full``.
 * Due to configurable backends ``repo_type`` is now mandatory parameter for the ``create_repo`` call.

.. _performance-rn-ref:

Performance
^^^^^^^^^^^

 * Significant performance improvements across all application functions.
 * HTTP Authentication performance enhancements.
 * Added a ``scope`` variable to the permissions fetching function which improves building permission trees in large
   amounts by a factor of 10.
 * Implemented caching logic for all authentication plugins. The ``AUTH_CACHE_TTL = <int>`` property now allow you to
   set the cache in seconds.

.. _prs-rn-ref:

Pull Requests
^^^^^^^^^^^^^

 * Pull requests can be now updated and merged from the web interface
 * Fixed creating a Mercurial |pr| from a bookmark.
 * Forbid closing pull requests when calculated status is different that the approved or rejected version.
 * Properly display calculated pull request review status on listing page.
 * Disable delete comment button if |pr| is closed.

.. _gists-rn-ref:

Gists
^^^^^
 * New UI based on grids with filtering.
 * Super-admins can see all gists.
 * Gists can now be created with a custom names.

.. _search-rn-ref:

Search
^^^^^^

 * New API based indexer.
 * Added the ability to create size limits for indexed files.
 * Added a new mapping configuration file which gives a very high level of flexibility when creating full text search.

.. _fixes-rn-ref:

Fixes
^^^^^

 * General: fixed issues with dependent objects, such as ``users`` in ``user groups``. Cleaning up these dependent
   objects is now done in a safe way.
 * General: deleting a ``user group`` from **settings > advanced** will use force removal and cleanup from all
   associations.
 * General: fixed issue with filter proxy middleware it's now more error prone.
 * General: fixed issues with unable to create fork inside a group.
 * General: fixed bad logic in ``ext_json`` lib, that checked bool on microseconds, in case it was 0 bool it returned False.
 * General: authors in annotation mode shows authors of current source, not from all history (that is in normal mode)
 * Permissions: fix issue when inherit flag for user group stopped working after initial permissions set.
 * |git|: fixed shallow clones.
 * |git|: added ``\n`` into the service line of |git| protocol. It is in the specifications and some python clients
   require this.
 * |hg|: fix thread safety for mercurial ``in-memory`` commits.
 * Windows: fixed issue with shebang and env headers.
 * MySQL: fixed database fields with 256 char length with added indexes. Mysql had problems with them.
 * Database: fixed bad usage of matching using ``ILIKE``. Previously it could happen that if you had
   ``marcin_1@rhodecode.com`` and ``marcin_2@rhodecode.com`` emails, using ``marcin_@rhodecode.com`` would match both.
 * VCS: fixed issues with double new lines on the commit patches.
 * VCS: repository locking now requires write permission to repository. If we allowed locking with read,
   people can lock repository without an option to unlock it.
 * Models: removed the ``isdigit`` call that can create issues when names are actually numbers on fetching objects.
 * Files: Fix bug with show authors in annotate view.
 * Hooks: truncate excessive commit lists on ``post_push`` hook.
 * Hooks: in |git|, support added to set the default branch if it is not ``master``.
 * Notifications: now can be marked as read when you are not admin.
 * Notifications: marking all notifications as read will hide the counter.
 * Frontend: fixed branch-tag switcher multiple ajax calls.
 * Repository group: |repo| group owners can now change group settings even if they don't have access to top-level
   permissions.
 * Repositories: if you set ``Fork of`` in advanced repository settings it will now only show valid repositories
   with the same type.

