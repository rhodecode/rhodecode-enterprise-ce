.. _api:

API Documentation
=================

The |RCE| API uses a single scheme for calling all API methods. The API is
implemented with JSON protocol in both directions. To send API requests to
your instance of |RCE|, use the following URL format
``<your_server>/_admin``

.. note::

   To use the API, you should configure the :file:`~/.rhoderc` file with
   access details per instance. For more information, see
   :ref:`config-rhoderc`.


API ACCESS FOR WEB VIEWS
------------------------

API access can also be turned on for each web view in |RCE| that is
decorated with a `@LoginRequired` decorator. To enable API access, change
the standard login decorator to `@LoginRequired(api_access=True)`.

From |RCM| version 1.7.0 you can configure a white list
of views that have API access enabled by default. To enable these,
edit the |RCM| configuration ``.ini`` file. The default location is:

* |RCM| Pre-2.2.7 :file:`root/rhodecode/data/production.ini`
* |RCM| 3.0 :file:`/home/{user}/.rccontrol/{instance-id}/rhodecode.ini`

To configure the white list, edit this section of the file. In this
configuration example, API access is granted to the patch/diff raw file and
archive.

.. code-block:: ini

    ## List of controllers (using glob syntax) that AUTH TOKENS could be used for access.
    ## Adding ?auth_token = <token> to the url authenticates this request as if it
    ## came from the the logged in user who own this authentication token.
    ##
    ## Syntax is <ControllerClass>:<function_pattern>.
    ## The list should be "," separated and on a single line.
    ##
    api_access_controllers_whitelist = ChangesetController:changeset_patch,ChangesetController:changeset_raw,ilesController:raw,FilesController:archivefile,

After this change, a |RCE| view can be accessed without login by adding a
GET parameter ``?auth_token=<auth_token>`` to a url. For example to
access the raw diff.

.. code-block:: html

   http://<server>/<repo>/changeset-diff/<sha>?auth_token=<auth_token>

By default this is only enabled on RSS/ATOM feed views. Exposing raw diffs is a
good way to integrate with 3rd party services like code review, or build farms
that could download archives.

API ACCESS
----------

All clients are required to send JSON-RPC spec JSON data.

.. code-block:: bash

    {
        "id:"<id>",
        "auth_token":"<auth_token>",
        "method":"<method_name>",
        "args":{"<arg_key>":"<arg_val>"}
    }

Example call for auto pulling from remote repositories using curl:

.. code-block:: bash

    curl https://server.com/_admin/api -X POST -H 'content-type:text/plain' --data-binary '{"id":1,
    "auth_token":"xe7cdb2v278e4evbdf5vs04v832v0efvcbcve4a3","method":"pull", "args":{"repo":"CPython"}}'

Provide those parameters:
 - **id** A value of any type, which is used to match the response with the
   request that it is replying to.
 - **auth_token** for access and permission validation.
 - **method** is name of method to call
 - **args** is an ``key:value`` list of arguments to pass to method

.. note::

    To get your |authtoken|, from the |RCE| interface,
    go to:
    :menuselection:`username --> My account --> Auth tokens`

    For security reasons you should always create a dedicated |authtoken| for
    API use only.


The |RCE| API will always return a JSON-RPC response:

.. code-block:: bash

    {
        "id": <id>, # matching id sent by request
        "result": "<result>"|null, # JSON formatted result, null if any errors
        "error": "null"|<error_message> # JSON formatted error (if any)
    }

All responses from API will be with `HTTP/1.0 200 OK` status code.
If there is an error when calling the API, the *error* key will contain a
failure description and the *result* will be `null`.

API CLIENT
----------

To install the |RCE| API, see :ref:`install-tools`. To configure the API per
instance, see the :ref:`rc-tools` section as you need to configure a
:file:`~/.rhoderc` file with your |authtokens|.

Once you have set up your instance API access, use the following examples to
get started.

.. code-block:: bash

    # Getting the 'rhodecode' repository
    # from a RhodeCode Enterprise instance
    rhodecode-api --instance-name=enterprise-1 get_repo repoid:rhodecode

    Calling method get_repo => http://127.0.0.1:5000
    Server response
    {
        <json data>
    }

    # Creating a new mercurial repository called 'brand-new'
    # with a description 'Repo-description'
    rhodecode-api --instance-name=enterprise-1 create_repo repo_name:brand-new repo_type:hg description:Repo-description
    {
      "error": null,
      "id": 1110,
      "result": {
        "msg": "Created new repository `brand-new`",
        "success": true,
        "task": null
      }
    }

A broken example, what not to do.

.. code-block:: bash

    # A call missing the required arguments
    # and not specifying the instance
    rhodecode-api get_repo

    Calling method get_repo => http://127.0.0.1:5000
    Server response
    "Missing non optional `repoid` arg in JSON DATA"

You can specify pure JSON using the ``--format`` parameter.

.. code-block:: bash

    rhodecode-api --format=json get_repo repoid:rhodecode

In such case only output that this function shows is pure JSON, we can use that
and pipe output to some json formatter.

If output is in pure JSON format, you can pipe output to a JSON formatter.

.. code-block:: bash

    rhodecode-api --instance-name=enterprise-1 --format=json get_repo repoid:rhodecode | python -m json.tool

API METHODS
-----------

Each method by default required following arguments.

.. code-block:: bash

    id :      "<id_for_response>"
    auth_token : "<auth_token>"
    method :  "<method name>"
    args :    {}

Use each **param** from docs and put it in args, Optional parameters
are not required in args.

.. code-block:: bash

    args: {"repoid": "rhodecode"}

.. Note: From this point on things are generated by the script in
   `scripts/fabfile.py`. To change things below, update the docstrings in the
   ApiController.

.. --- API DEFS MARKER ---

pull
----

.. py:function:: pull(apiuser, repoid)

   Triggers a pull on the given repository from a remote location. You
   can use this to keep remote repositories up-to-date.

   This command can only be run using an |authtoken| with admin
   rights to the specified repository. For more information,
   see :ref:`config-token-ref`.

   This command takes the following options:

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: The repository name or repository ID.
   :type repoid: str or int

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       "msg": "Pulled from `<repository name>`"
       "repository": "<repository name>"
     }
     error :  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "Unable to pull changes from `<reponame>`"
     }


strip
-----

.. py:function:: strip(apiuser, repoid, revision, branch)

   Strips the given revision from the specified repository.

   * This will remove the revision and all of its decendants.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   This command takes the following options:

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: The repository name or repository ID.
   :type repoid: str or int
   :param revision: The revision you wish to strip.
   :type revision: str
   :param branch: The branch from which to strip the revision.
   :type branch: str

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       "msg": "'Stripped commit <commit_hash> from repo `<repository name>`'"
       "repository": "<repository name>"
     }
     error :  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "Unable to strip commit <commit_hash> from repo `<repository name>`"
     }


rescan_repos
------------

.. py:function:: rescan_repos(apiuser, remove_obsolete=<Optional:False>)

   Triggers a rescan of the specified repositories.

   * If the ``remove_obsolete`` option is set, it also deletes repositories
     that are found in the database but not on the file system, so called
     "clean zombies".

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   This command takes the following options:

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param remove_obsolete: Deletes repositories from the database that
       are not found on the filesystem.
   :type remove_obsolete: Optional(``True`` | ``False``)

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       'added': [<added repository name>,...]
       'removed': [<removed repository name>,...]
     }
     error :  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       'Error occurred during rescan repositories action'
     }


invalidate_cache
----------------

.. py:function:: invalidate_cache(apiuser, repoid, delete_keys=<Optional:False>)

   Invalidates the cache for the specified repository.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   This command takes the following options:

   :param apiuser: This is filled automatically from |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Sets the repository name or repository ID.
   :type repoid: str or int
   :param delete_keys: This deletes the invalidated keys instead of
       just flagging them.
   :type delete_keys: Optional(``True`` | ``False``)

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       'msg': Cache for repository `<repository name>` was invalidated,
       'repository': <repository name>
     }
     error :  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error : {
        'Error occurred during cache invalidation action'
     }


lock
----

.. py:function:: lock(apiuser, repoid, locked=<Optional:None>, userid=<Optional:<OptionalAttr:apiuser>>)

   Sets the lock state of the specified |repo| by the given user.
   From more information, see :ref:`repo-locking`.

   * If the ``userid`` option is not set, the repository is locked to the
     user who called the method.
   * If the ``locked`` parameter is not set, the current lock state of the
     repository is displayed.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   This command takes the following options:

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Sets the repository name or repository ID.
   :type repoid: str or int
   :param locked: Sets the lock state.
   :type locked: Optional(``True`` | ``False``)
   :param userid: Set the repository lock to this user.
   :type userid: Optional(str or int)

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       'repo': '<reponame>',
       'locked': <bool: lock state>,
       'locked_since': <int: lock timestamp>,
       'locked_by': <username of person who made the lock>,
       'lock_reason': <str: reason for locking>,
       'lock_state_changed': <bool: True if lock state has been changed in this request>,
       'msg': 'Repo `<reponame>` locked by `<username>` on <timestamp>.'
       or
       'msg': 'Repo `<repository name>` not locked.'
       or
       'msg': 'User `<user name>` set lock state for repo `<repository name>` to `<new lock state>`'
     }
     error :  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       'Error occurred locking repository `<reponame>`
     }


get_locks
---------

.. py:function:: get_locks(apiuser, userid=<Optional:<OptionalAttr:apiuser>>)

   Displays all repositories locked by the specified user.

   * If this command is run by a non-admin user, it returns
     a list of |repos| locked by that user.

   This command takes the following options:

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param userid: Sets the userid whose list of locked |repos| will be
       displayed.
   :type userid: Optional(str or int)

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result : {
           [repo_object, repo_object,...]
       }
       error :  null


get_ip
------

.. py:function:: get_ip(apiuser, userid=<Optional:<OptionalAttr:apiuser>>)

   Displays the IP Address as seen from the |RCE| server.

   * This command displays the IP Address, as well as all the defined IP
     addresses for the specified user. If the ``userid`` is not set, the
     data returned is for the user calling the method.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   This command takes the following options:

   :param apiuser: This is filled automatically from |authtoken|.
   :type apiuser: AuthUser
   :param userid: Sets the userid for which associated IP Address data
       is returned.
   :type userid: Optional(str or int)

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result : {
                    "server_ip_addr": "<ip_from_clien>",
                    "user_ips": [
                                   {
                                      "ip_addr": "<ip_with_mask>",
                                      "ip_range": ["<start_ip>", "<end_ip>"],
                                   },
                                   ...
                                ]
       }


show_ip
-------

.. py:function:: show_ip(apiuser, userid=<Optional:<OptionalAttr:apiuser>>)

   Displays the IP Address as seen from the |RCE| server.

   * This command displays the IP Address, as well as all the defined IP
     addresses for the specified user. If the ``userid`` is not set, the
     data returned is for the user calling the method.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   This command takes the following options:

   :param apiuser: This is filled automatically from |authtoken|.
   :type apiuser: AuthUser
   :param userid: Sets the userid for which associated IP Address data
       is returned.
   :type userid: Optional(str or int)

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result : {
                    "server_ip_addr": "<ip_from_clien>",
                    "user_ips": [
                                   {
                                      "ip_addr": "<ip_with_mask>",
                                      "ip_range": ["<start_ip>", "<end_ip>"],
                                   },
                                   ...
                                ]
       }


get_license_info
----------------

.. py:function:: get_license_info(apiuser)

   Returns the |RCE| license information.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       'rhodecode_version': <rhodecode version>,
       'token': <license token>,
       'issued_to': <license owner>,
       'issued_on': <license issue date>,
       'expires_on': <license expiration date>,
       'type': <license type>,
       'users_limit': <license users limit>,
       'key': <license key>
     }
     error :  null


set_license_key
---------------

.. py:function:: set_license_key(apiuser, key)

   Sets the |RCE| license key.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param key: This is the license key to be set.
   :type key: str

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg" : "updated license information",
                 "key": <key>
               }
       error:  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "license key is not valid"
       or
       "trial licenses cannot be uploaded"
       or
       "error occurred while updating license"
     }


get_server_info
---------------

.. py:function:: get_server_info(apiuser)

   Returns the |RCE| server information.

   This includes the running version of |RCE| and all installed
   packages. This command takes the following options:

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       'modules': [<module name>,...]
       'py_version': <python version>,
       'platform': <platform type>,
       'rhodecode_version': <rhodecode version>
     }
     error :  null


get_user
--------

.. py:function:: get_user(apiuser, userid=<Optional:<OptionalAttr:apiuser>>)

   Returns the information associated with a username or userid.

   * If the ``userid`` is not set, this command returns the information
     for the ``userid`` calling the method.

   .. note::

      Normal users may only run this command against their ``userid``. For
      full privileges you must run this command using an |authtoken| with
      admin rights.

   This command takes the following options:

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param userid: Sets the userid for which data will be returned.
   :type userid: Optional(str or int)

   Example output:

   .. code-block:: bash

       {
         "error": null,
         "id": <id>,
         "result": {
           "active": true,
           "admin": false,
           "api_key": "api-key",
           "api_keys": [ list of keys ],
           "email": "user@example.com",
           "emails": [
             "user@example.com"
           ],
           "extern_name": "rhodecode",
           "extern_type": "rhodecode",
           "firstname": "username",
           "ip_addresses": [],
           "language": null,
           "last_login": "Timestamp",
           "lastname": "surnae",
           "permissions": {
             "global": [
               "hg.inherit_default_perms.true",
               "usergroup.read",
               "hg.repogroup.create.false",
               "hg.create.none",
               "hg.extern_activate.manual",
               "hg.create.write_on_repogroup.false",
               "hg.usergroup.create.false",
               "group.none",
               "repository.none",
               "hg.register.none",
               "hg.fork.repository"
             ],
             "repositories": { "username/example": "repository.write"},
             "repositories_groups": { "user-group/repo": "group.none" },
             "user_groups": { "user_group_name": "usergroup.read" }
           },
           "user_id": 32,
           "username": "username"
         }
       }


get_users
---------

.. py:function:: get_users(apiuser)

   Lists all users in the |RCE| user database.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   This command takes the following options:

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
           result: [<user_object>, ...]
       error:  null


create_user
-----------

.. py:function:: create_user(apiuser, username, email, password=<Optional:''>, firstname=<Optional:''>, lastname=<Optional:''>, active=<Optional:True>, admin=<Optional:False>, extern_name=<Optional:'rhodecode'>, extern_type=<Optional:'rhodecode'>, force_password_change=<Optional:False>)

   Creates a new user and returns the new user object.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   This command takes the following options:

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param username: Set the new username.
   :type username: str or int
   :param email: Set the user email address.
   :type email: str
   :param password: Set the new user password.
   :type password: Optional(str)
   :param firstname: Set the new user firstname.
   :type firstname: Optional(str)
   :param lastname: Set the new user surname.
   :type lastname: Optional(str)
   :param active: Set the user as active.
   :type active: Optional(``True`` | ``False``)
   :param admin: Give the new user admin rights.
   :type admin: Optional(``True`` | ``False``)
   :param extern_name: Set the authentication plugin name.
       Using LDAP this is filled with LDAP UID.
   :type extern_name: Optional(str)
   :param extern_type: Set the new user authentication plugin.
   :type extern_type: Optional(str)
   :param force_password_change: Force the new user to change password
       on next login.
   :type force_password_change: Optional(``True`` | ``False``)

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg" : "created new user `<username>`",
                 "user": <user_obj>
               }
       error:  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "user `<username>` already exist"
       or
       "email `<email>` already exist"
       or
       "failed to create user `<username>`"
     }


update_user
-----------

.. py:function:: update_user(apiuser, userid, username=<Optional:None>, email=<Optional:None>, password=<Optional:None>, firstname=<Optional:None>, lastname=<Optional:None>, active=<Optional:None>, admin=<Optional:None>, extern_type=<Optional:None>, extern_name=<Optional:None>)

   Updates the details for the specified user, if that user exists.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   This command takes the following options:

   :param apiuser: This is filled automatically from |authtoken|.
   :type apiuser: AuthUser
   :param userid: Set the ``userid`` to update.
   :type userid: str or int
   :param username: Set the new username.
   :type username: str or int
   :param email: Set the new email.
   :type email: str
   :param password: Set the new password.
   :type password: Optional(str)
   :param firstname: Set the new first name.
   :type firstname: Optional(str)
   :param lastname: Set the new surname.
   :type lastname: Optional(str)
   :param active: Set the new user as active.
   :type active: Optional(``True`` | ``False``)
   :param admin: Give the user admin rights.
   :type admin: Optional(``True`` | ``False``)
   :param extern_name: Set the authentication plugin user name.
       Using LDAP this is filled with LDAP UID.
   :type extern_name: Optional(str)
   :param extern_type: Set the authentication plugin type.
   :type extern_type: Optional(str)


   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg" : "updated user ID:<userid> <username>",
                 "user": <user_object>,
               }
       error:  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to update user `<username>`"
     }


delete_user
-----------

.. py:function:: delete_user(apiuser, userid)

   Deletes the specified user from the |RCE| user database.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   .. important::

      Ensure all open pull requests and open code review
      requests to this user are close.

      Also ensure all repositories, or repository groups owned by this
      user are reassigned before deletion.

   This command takes the following options:

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param userid: Set the user to delete.
   :type userid: str or int

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg" : "deleted user ID:<userid> <username>",
                 "user": null
               }
       error:  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to delete user ID:<userid> <username>"
     }


get_user_group
--------------

.. py:function:: get_user_group(apiuser, usergroupid)

   Returns the data of an existing user group.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param usergroupid: Set the user group from which to return data.
   :type usergroupid: str or int

   Example error output:

   .. code-block:: bash

       {
         "error": null,
         "id": <id>,
         "result": {
           "active": true,
           "group_description": "group description",
           "group_name": "group name",
           "members": [
             {
               "name": "owner-name",
               "origin": "owner",
               "permission": "usergroup.admin",
               "type": "user"
             },
             {
             {
               "name": "user name",
               "origin": "permission",
               "permission": "usergroup.admin",
               "type": "user"
             },
             {
               "name": "user group name",
               "origin": "permission",
               "permission": "usergroup.write",
               "type": "user_group"
             }
           ],
           "owner": "owner name",
           "users": [],
           "users_group_id": 2
         }
       }


get_user_groups
---------------

.. py:function:: get_user_groups(apiuser)

   Lists all the existing user groups within RhodeCode.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   This command takes the following options:

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser

   Example error output:

   .. code-block:: bash

       id : <id_given_in_input>
       result : [<user_group_obj>,...]
       error : null


create_user_group
-----------------

.. py:function:: create_user_group(apiuser, group_name, description=<Optional:''>, owner=<Optional:<OptionalAttr:apiuser>>, active=<Optional:True>)

   Creates a new user group.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   This command takes the following options:

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param group_name: Set the name of the new user group.
   :type group_name: str
   :param description: Give a description of the new user group.
   :type description: str
   :param owner: Set the owner of the new user group.
       If not set, the owner is the |authtoken| user.
   :type owner: Optional(str or int)
   :param active: Set this group as active.
   :type active: Optional(``True`` | ``False``)

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg": "created new user group `<groupname>`",
                 "user_group": <user_group_object>
               }
       error:  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "user group `<group name>` already exist"
       or
       "failed to create group `<group name>`"
     }


update_user_group
-----------------

.. py:function:: update_user_group(apiuser, usergroupid, group_name=<Optional:''>, description=<Optional:''>, owner=<Optional:None>, active=<Optional:True>)

   Updates the specified `user group` with the details provided.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param usergroupid: Set the id of the `user group` to update.
   :type usergroupid: str or int
   :param group_name: Set the new name the `user group`
   :type group_name: str
   :param description: Give a description for the `user group`
   :type description: str
   :param owner: Set the owner of the `user group`.
   :type owner: Optional(str or int)
   :param active: Set the group as active.
   :type active: Optional(``True`` | ``False``)

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       "msg": 'updated user group ID:<user group id> <user group name>',
       "user_group": <user_group_object>
     }
     error :  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to update user group `<user group name>`"
     }


delete_user_group
-----------------

.. py:function:: delete_user_group(apiuser, usergroupid)

   Deletes the specified `user group`.

   This command can only be run using an |authtoken| with admin rights to
   the specified repository.

   This command takes the following options:

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param usergroupid:
   :type usergroupid: int

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       "msg": "deleted user group ID:<user_group_id> <user_group_name>"
     }
     error :  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to delete user group ID:<user_group_id> <user_group_name>"
       or
       "RepoGroup assigned to <repo_groups_list>"
     }


add_user_to_user_group
----------------------

.. py:function:: add_user_to_user_group(apiuser, usergroupid, userid)

   Adds a user to a `user group`. If the user already exists in the group
   this command will return false.

   This command can only be run using an |authtoken| with admin rights to
   the specified user group.

   This command takes the following options:

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param usergroupid: Set the name of the `user group` to which a
       user will be added.
   :type usergroupid: int
   :param userid: Set the `user_id` of the user to add to the group.
   :type userid: int

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
         "success": True|False # depends on if member is in group
         "msg": "added member `<username>` to user group `<groupname>` |
                 User is already in that group"

     }
     error :  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to add member to user group `<user_group_name>`"
     }


remove_user_from_user_group
---------------------------

.. py:function:: remove_user_from_user_group(apiuser, usergroupid, userid)

   Removes a user from a user group.

   * If the specified user is not in the group, this command will return
     `false`.

   This command can only be run using an |authtoken| with admin rights to
   the specified user group.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param usergroupid: Sets the user group name.
   :type usergroupid: str or int
   :param userid: The user you wish to remove from |RCE|.
   :type userid: str or int

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "success":  True|False,  # depends on if member is in group
                 "msg": "removed member <username> from user group <groupname> |
                         User wasn't in group"
               }
       error:  null


grant_user_permission_to_user_group
-----------------------------------

.. py:function:: grant_user_permission_to_user_group(apiuser, usergroupid, userid, perm)

   Set permissions for a user in a user group.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param usergroupid: Set the user group to edit permissions on.
   :type usergroupid: str or int
   :param userid: Set the user from whom you wish to set permissions.
   :type userid: str
   :param perm: (usergroup.(none|read|write|admin))
   :type perm: str

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       "msg": "Granted perm: `<perm_name>` for user: `<username>` in user group: `<user_group_name>`",
       "success": true
     }
     error :  null


revoke_user_permission_from_user_group
--------------------------------------

.. py:function:: revoke_user_permission_from_user_group(apiuser, usergroupid, userid)

   Revoke a users permissions in a user group.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param usergroupid: Set the user group from which to revoke the user
       permissions.
   :type: usergroupid: str or int
   :param userid: Set the userid of the user whose permissions will be
       revoked.
   :type userid: str

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       "msg": "Revoked perm for user: `<username>` in user group: `<user_group_name>`",
       "success": true
     }
     error :  null


grant_user_group_permission_to_user_group
-----------------------------------------

.. py:function:: grant_user_group_permission_to_user_group(apiuser, usergroupid, sourceusergroupid, perm)

   Give one user group permissions to another user group.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param usergroupid: Set the user group on which to edit permissions.
   :type usergroupid: str or int
   :param sourceusergroupid: Set the source user group to which
       access/permissions will be granted.
   :type sourceusergroupid: str or int
   :param perm: (usergroup.(none|read|write|admin))
   :type perm: str

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       "msg": "Granted perm: `<perm_name>` for user group: `<source_user_group_name>` in user group: `<user_group_name>`",
       "success": true
     }
     error :  null


revoke_user_group_permission_from_user_group
--------------------------------------------

.. py:function:: revoke_user_group_permission_from_user_group(apiuser, usergroupid, sourceusergroupid)

   Revoke the permissions that one user group has to another.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param usergroupid: Set the user group on which to edit permissions.
   :type usergroupid: str or int
   :param sourceusergroupid: Set the user group from which permissions
       are revoked.
   :type sourceusergroupid: str or int

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       "msg": "Revoked perm for user group: `<user_group_name>` in user group: `<target_user_group_name>`",
       "success": true
     }
     error :  null


get_pull_request
----------------

.. py:function:: get_pull_request(apiuser, repoid, pullrequestid)

   Get a pull request based on the given ID.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Repository name or repository ID from where the pull
       request was opened.
   :type repoid: str or int
   :param pullrequestid: ID of the requested pull request.
   :type pullrequestid: int

   Example output:

   .. code-block:: bash

     "id": <id_given_in_input>,
     "result":
       {
           "pull_request_id":   "<pull_request_id>",
           "url":               "<url>",
           "title":             "<title>",
           "description":       "<description>",
           "status" :           "<status>",
           "created_on":        "<date_time_created>",
           "updated_on":        "<date_time_updated>",
           "commit_ids":        [
                                    ...
                                    "<commit_id>",
                                    "<commit_id>",
                                    ...
                                ],
           "review_status":    "<review_status>",
           "mergeable":         {
                                    "status":  "<bool>",
                                    "message": "<message>",
                                },
           "source":            {
                                    "clone_url":     "<clone_url>",
                                    "repository":    "<repository_name>",
                                    "reference":
                                    {
                                        "name":      "<name>",
                                        "type":      "<type>",
                                        "commit_id": "<commit_id>",
                                    }
                                },
           "target":            {
                                    "clone_url":   "<clone_url>",
                                    "repository":    "<repository_name>",
                                    "reference":
                                    {
                                        "name":      "<name>",
                                        "type":      "<type>",
                                        "commit_id": "<commit_id>",
                                    }
                                },
          "author":             <user_obj>,
          "reviewers":          [
                                    ...
                                    {
                                       "user":          "<user_obj>",
                                       "review_status": "<review_status>",
                                    }
                                    ...
                                ]
       },
      "error": null


get_pull_requests
-----------------

.. py:function:: get_pull_requests(apiuser, repoid, status=<Optional:'new'>)

   Get all pull requests from the repository specified in `repoid`.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Repository name or repository ID.
   :type repoid: str or int
   :param status: Only return pull requests with the specified status.
       Valid options are.
       * ``new`` (default)
       * ``open``
       * ``closed``
   :type status: str

   Example output:

   .. code-block:: bash

     "id": <id_given_in_input>,
     "result":
       [
           ...
           {
               "pull_request_id":   "<pull_request_id>",
               "url":               "<url>",
               "title" :            "<title>",
               "description":       "<description>",
               "status":            "<status>",
               "created_on":        "<date_time_created>",
               "updated_on":        "<date_time_updated>",
               "commit_ids":        [
                                        ...
                                        "<commit_id>",
                                        "<commit_id>",
                                        ...
                                    ],
               "review_status":    "<review_status>",
               "mergeable":         {
                                       "status":      "<bool>",
                                       "message:      "<message>",
                                    },
               "source":            {
                                        "clone_url":     "<clone_url>",
                                        "reference":
                                        {
                                            "name":      "<name>",
                                            "type":      "<type>",
                                            "commit_id": "<commit_id>",
                                        }
                                    },
               "target":            {
                                        "clone_url":   "<clone_url>",
                                        "reference":
                                        {
                                            "name":      "<name>",
                                            "type":      "<type>",
                                            "commit_id": "<commit_id>",
                                        }
                                    },
              "author":             <user_obj>,
              "reviewers":          [
                                        ...
                                        {
                                           "user":          "<user_obj>",
                                           "review_status": "<review_status>",
                                        }
                                        ...
                                    ]
           }
           ...
       ],
     "error": null


merge_pull_request
------------------

.. py:function:: merge_pull_request(apiuser, repoid, pullrequestid, userid=<Optional:<OptionalAttr:apiuser>>)

   Merge the pull request specified by `pullrequestid` into its target
   repository.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: The Repository name or repository ID of the
       target repository to which the |pr| is to be merged.
   :type repoid: str or int
   :param pullrequestid: ID of the pull request which shall be merged.
   :type pullrequestid: int
   :param userid: Merge the pull request as this user.
   :type userid: Optional(str or int)

   Example output:

   .. code-block:: bash

     "id": <id_given_in_input>,
     "result":
       {
           "executed":         "<bool>",
           "failure_reason":   "<int>",
           "merge_commit_id":  "<merge_commit_id>",
           "possible":         "<bool>"
       },
     "error": null


close_pull_request
------------------

.. py:function:: close_pull_request(apiuser, repoid, pullrequestid, userid=<Optional:<OptionalAttr:apiuser>>)

   Close the pull request specified by `pullrequestid`.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Repository name or repository ID to which the pull
       request belongs.
   :type repoid: str or int
   :param pullrequestid: ID of the pull request to be closed.
   :type pullrequestid: int
   :param userid: Close the pull request as this user.
   :type userid: Optional(str or int)

   Example output:

   .. code-block:: bash

     "id": <id_given_in_input>,
     "result":
       {
           "pull_request_id":  "<int>",
           "closed":           "<bool>"
       },
     "error": null


comment_pull_request
--------------------

.. py:function:: comment_pull_request(apiuser, repoid, pullrequestid, message=<Optional:None>, status=<Optional:None>, userid=<Optional:<OptionalAttr:apiuser>>)

   Comment on the pull request specified with the `pullrequestid`,
   in the |repo| specified by the `repoid`, and optionally change the
   review status.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: The repository name or repository ID.
   :type repoid: str or int
   :param pullrequestid: The pull request ID.
   :type pullrequestid: int
   :param message: The text content of the comment.
   :type message: str
   :param status: (**Optional**) Set the approval status of the pull
       request. Valid options are:
       * not_reviewed
       * approved
       * rejected
       * under_review
   :type status: str
   :param userid: Comment on the pull request as this user
   :type userid: Optional(str or int)

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result :
       {
           "pull_request_id":  "<Integer>",
           "comment_id":       "<Integer>"
       }
     error :  null


create_pull_request
-------------------

.. py:function:: create_pull_request(apiuser, source_repo, target_repo, source_ref, target_ref, title, description=<Optional:''>, reviewers=<Optional:None>)

   Creates a new pull request.

   Accepts refs in the following formats:

       * branch:<branch_name>:<sha>
       * branch:<branch_name>
       * bookmark:<bookmark_name>:<sha> (Mercurial only)
       * bookmark:<bookmark_name> (Mercurial only)

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param source_repo: Set the source repository name.
   :type source_repo: str
   :param target_repo: Set the target repository name.
   :type target_repo: str
   :param source_ref: Set the source ref name.
   :type source_ref: str
   :param target_ref: Set the target ref name.
   :type target_ref: str
   :param title: Set the pull request title.
   :type title: str
   :param description: Set the pull request description.
   :type description: Optional(str)
   :param reviewers: Set the new pull request reviewers list.
   :type reviewers: Optional(list)


update_pull_request
-------------------

.. py:function:: update_pull_request(apiuser, repoid, pullrequestid, title=<Optional:''>, description=<Optional:''>, reviewers=<Optional:None>, update_commits=<Optional:None>, close_pull_request=<Optional:None>)

   Updates a pull request.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: The repository name or repository ID.
   :type repoid: str or int
   :param pullrequestid: The pull request ID.
   :type pullrequestid: int
   :param title: Set the pull request title.
   :type title: str
   :param description: Update pull request description.
   :type description: Optional(str)
   :param reviewers: Update pull request reviewers list with new value.
   :type reviewers: Optional(list)
   :param update_commits: Trigger update of commits for this pull request
   :type: update_commits: Optional(bool)
   :param close_pull_request: Close this pull request with rejected state
   :type: close_pull_request: Optional(bool)

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result :
       {
           "msg": "Updated pull request `63`",
           "pull_request": <pull_request_object>,
           "updated_reviewers": {
             "added": [
               "username"
             ],
             "removed": []
           },
           "updated_commits": {
             "added": [
               "<sha1_hash>"
             ],
             "common": [
               "<sha1_hash>",
               "<sha1_hash>",
             ],
             "removed": []
           }
       }
     error :  null


get_repo
--------

.. py:function:: get_repo(apiuser, repoid, cache=<Optional:True>)

   Gets an existing repository by its name or repository_id.

   The members section so the output returns users groups or users
   associated with that repository.

   This command can only be run using an |authtoken| with admin rights,
   or users with at least read rights to the |repo|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: The repository name or repository id.
   :type repoid: str or int
   :param cache: use the cached value for last changeset
   :type: cache: Optional(bool)

   Example output:

   .. code-block:: bash

       {
         "error": null,
         "id": <repo_id>,
         "result": {
           "clone_uri": null,
           "created_on": "timestamp",
           "description": "repo description",
           "enable_downloads": false,
           "enable_locking": false,
           "enable_statistics": false,
           "followers": [
             {
               "active": true,
               "admin": false,
               "api_key": "****************************************",
               "api_keys": [
                 "****************************************"
               ],
               "email": "user@example.com",
               "emails": [
                 "user@example.com"
               ],
               "extern_name": "rhodecode",
               "extern_type": "rhodecode",
               "firstname": "username",
               "ip_addresses": [],
               "language": null,
               "last_login": "2015-09-16T17:16:35.854",
               "lastname": "surname",
               "user_id": <user_id>,
               "username": "name"
             }
           ],
           "fork_of": "parent-repo",
           "landing_rev": [
             "rev",
             "tip"
           ],
           "last_changeset": {
             "author": "User <user@example.com>",
             "branch": "default",
             "date": "timestamp",
             "message": "last commit message",
             "parents": [
               {
                 "raw_id": "commit-id"
               }
             ],
             "raw_id": "commit-id",
             "revision": <revision number>,
             "short_id": "short id"
           },
           "lock_reason": null,
           "locked_by": null,
           "locked_date": null,
           "members": [
             {
               "name": "super-admin-name",
               "origin": "super-admin",
               "permission": "repository.admin",
               "type": "user"
             },
             {
               "name": "owner-name",
               "origin": "owner",
               "permission": "repository.admin",
               "type": "user"
             },
             {
               "name": "user-group-name",
               "origin": "permission",
               "permission": "repository.write",
               "type": "user_group"
             }
           ],
           "owner": "owner-name",
           "permissions": [
             {
               "name": "super-admin-name",
               "origin": "super-admin",
               "permission": "repository.admin",
               "type": "user"
             },
             {
               "name": "owner-name",
               "origin": "owner",
               "permission": "repository.admin",
               "type": "user"
             },
             {
               "name": "user-group-name",
               "origin": "permission",
               "permission": "repository.write",
               "type": "user_group"
             }
           ],
           "private": true,
           "repo_id": 676,
           "repo_name": "user-group/repo-name",
           "repo_type": "hg"
         }
       }


get_repos
---------

.. py:function:: get_repos(apiuser)

   Lists all existing repositories.

   This command can only be run using an |authtoken| with admin rights,
   or users with at least read rights to |repos|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: [
                 {
                   "repo_id" :          "<repo_id>",
                   "repo_name" :        "<reponame>"
                   "repo_type" :        "<repo_type>",
                   "clone_uri" :        "<clone_uri>",
                   "private": :         "<bool>",
                   "created_on" :       "<datetimecreated>",
                   "description" :      "<description>",
                   "landing_rev":       "<landing_rev>",
                   "owner":             "<repo_owner>",
                   "fork_of":           "<name_of_fork_parent>",
                   "enable_downloads":  "<bool>",
                   "enable_locking":    "<bool>",
                   "enable_statistics": "<bool>",
                 },
                 ...
               ]
       error:  null


get_repo_changeset
------------------

.. py:function:: get_repo_changeset(apiuser, repoid, revision, details=<Optional:'basic'>)

   Returns information about a changeset.

   Additionally parameters define the amount of details returned by
   this function.

   This command can only be run using an |authtoken| with admin rights,
   or users with at least read rights to the |repo|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: The repository name or repository id
   :type repoid: str or int
   :param revision: revision for which listing should be done
   :type revision: str
   :param details: details can be 'basic|extended|full' full gives diff
       info details like the diff itself, and number of changed files etc.
   :type details: Optional(str)


get_repo_changesets
-------------------

.. py:function:: get_repo_changesets(apiuser, repoid, start_rev, limit, details=<Optional:'basic'>)

   Returns a set of changesets limited by the number of commits starting
   from the `start_rev` option.

   Additional parameters define the amount of details returned by this
   function.

   This command can only be run using an |authtoken| with admin rights,
   or users with at least read rights to |repos|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: The repository name or repository ID.
   :type repoid: str or int
   :param start_rev: The starting revision from where to get changesets.
   :type start_rev: str
   :param limit: Limit the number of changesets to this amount
   :type limit: str or int
   :param details: Set the level of detail returned. Valid option are:
       ``basic``, ``extended`` and ``full``.
   :type details: Optional(str)

   .. note::

      Setting the parameter `details` to the value ``full`` is extensive
      and returns details like the diff itself, and the number
      of changed files.


get_repo_nodes
--------------

.. py:function:: get_repo_nodes(apiuser, repoid, revision, root_path, ret_type=<Optional:'all'>, details=<Optional:'basic'>)

   Returns a list of nodes and children in a flat list for a given
   path at given revision.

   It's possible to specify ret_type to show only `files` or `dirs`.

   This command can only be run using an |authtoken| with admin rights,
   or users with at least read rights to |repos|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: The repository name or repository ID.
   :type repoid: str or int
   :param revision: The revision for which listing should be done.
   :type revision: str
   :param root_path: The path from which to start displaying.
   :type root_path: str
   :param ret_type: Set the return type. Valid options are
       ``all`` (default), ``files`` and ``dirs``.
   :type ret_type: Optional(str)
   :param details: Returns extended information about nodes, such as
       md5, binary, and or content.  The valid options are ``basic`` and
       ``full``.
   :type details: Optional(str)
   :param max_file_bytes: Only return file content under this file size bytes
   :type details: Optional(int)

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: [
                 {
                   "name" : "<name>"
                   "type" : "<type>",
                   "binary": "<true|false>" (only in extended mode)
                   "md5"  : "<md5 of file content>" (only in extended mode)
                 },
                 ...
               ]
       error:  null


create_repo
-----------

.. py:function:: create_repo(apiuser, repo_name, repo_type, owner=<Optional:<OptionalAttr:apiuser>>, description=<Optional:''>, private=<Optional:False>, clone_uri=<Optional:None>, landing_rev=<Optional:'rev:tip'>, enable_statistics=<Optional:False>, enable_locking=<Optional:False>, enable_downloads=<Optional:False>, copy_permissions=<Optional:False>)

   Creates a repository.

   * If the repository name contains "/", all the required repository
     groups will be created.

     For example "foo/bar/baz" will create |repo| groups "foo" and "bar"
     (with "foo" as parent). It will also create the "baz" repository
     with "bar" as |repo| group.

   This command can only be run using an |authtoken| with at least
   write permissions to the |repo|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repo_name: Set the repository name.
   :type repo_name: str
   :param repo_type: Set the repository type; 'hg','git', or 'svn'.
   :type repo_type: str
   :param owner: user_id or username
   :type owner: Optional(str)
   :param description: Set the repository description.
   :type description: Optional(str)
   :param private:
   :type private: bool
   :param clone_uri:
   :type clone_uri: str
   :param landing_rev: <rev_type>:<rev>
   :type landing_rev: str
   :param enable_locking:
   :type enable_locking: bool
   :param enable_downloads:
   :type enable_downloads: bool
   :param enable_statistics:
   :type enable_statistics: bool
   :param copy_permissions: Copy permission from group in which the
       repository is being created.
   :type copy_permissions: bool


   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg": "Created new repository `<reponame>`",
                 "success": true,
                 "task": "<celery task id or None if done sync>"
               }
       error:  null


   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
        'failed to create repository `<repo_name>`
     }


add_field_to_repo
-----------------

.. py:function:: add_field_to_repo(apiuser, repoid, key, label=<Optional:''>, description=<Optional:''>)

   Adds an extra field to a repository.

   This command can only be run using an |authtoken| with at least
   write permissions to the |repo|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Set the repository name or repository id.
   :type repoid: str or int
   :param key: Create a unique field key for this repository.
   :type key: str
   :param label:
   :type label: Optional(str)
   :param description:
   :type description: Optional(str)


remove_field_from_repo
----------------------

.. py:function:: remove_field_from_repo(apiuser, repoid, key)

   Removes an extra field from a repository.

   This command can only be run using an |authtoken| with at least
   write permissions to the |repo|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Set the repository name or repository ID.
   :type repoid: str or int
   :param key: Set the unique field key for this repository.
   :type key: str


update_repo
-----------

.. py:function:: update_repo(apiuser, repoid, name=<Optional:None>, owner=<Optional:<OptionalAttr:apiuser>>, group=<Optional:None>, fork_of=<Optional:None>, description=<Optional:''>, private=<Optional:False>, clone_uri=<Optional:None>, landing_rev=<Optional:'rev:tip'>, enable_statistics=<Optional:False>, enable_locking=<Optional:False>, enable_downloads=<Optional:False>, fields=<Optional:''>)

   Updates a repository with the given information.

   This command can only be run using an |authtoken| with at least
   write permissions to the |repo|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: repository name or repository ID.
   :type repoid: str or int
   :param name: Update the |repo| name.
   :type name: str
   :param owner: Set the |repo| owner.
   :type owner: str
   :param group: Set the |repo| group the |repo| belongs to.
   :type group: str
   :param fork_of: Set the master |repo| name.
   :type fork_of: str
   :param description: Update the |repo| description.
   :type description: str
   :param private: Set the |repo| as private. (True | False)
   :type private: bool
   :param clone_uri: Update the |repo| clone URI.
   :type clone_uri: str
   :param landing_rev: Set the |repo| landing revision. Default is
       ``tip``.
   :type landing_rev: str
   :param enable_statistics: Enable statistics on the |repo|,
       (True | False).
   :type enable_statistics: bool
   :param enable_locking: Enable |repo| locking.
   :type enable_locking: bool
   :param enable_downloads: Enable downloads from the |repo|,
       (True | False).
   :type enable_downloads: bool
   :param fields: Add extra fields to the |repo|. Use the following
       example format: ``field_key=field_val,field_key2=fieldval2``.
       Escape ', ' with \,
   :type fields: str


fork_repo
---------

.. py:function:: fork_repo(apiuser, repoid, fork_name, owner=<Optional:<OptionalAttr:apiuser>>, description=<Optional:''>, copy_permissions=<Optional:False>, private=<Optional:False>, landing_rev=<Optional:'rev:tip'>)

   Creates a fork of the specified |repo|.

   * If using |RCE| with Celery this will immediately return a success
     message, even though the fork will be created asynchronously.

   This command can only be run using an |authtoken| with fork
   permissions on the |repo|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Set repository name or repository ID.
   :type repoid: str or int
   :param fork_name: Set the fork name.
   :type fork_name: str
   :param owner: Set the fork owner.
   :type owner: str
   :param description: Set the fork descripton.
   :type description: str
   :param copy_permissions: Copy permissions from parent |repo|. The
       default is False.
   :type copy_permissions: bool
   :param private: Make the fork private. The default is False.
   :type private: bool
   :param landing_rev: Set the landing revision. The default is tip.

   Example output:

   .. code-block:: bash

       id : <id_for_response>
       api_key : "<api_key>"
       args:     {
                   "repoid" :          "<reponame or repo_id>",
                   "fork_name":        "<forkname>",
                   "owner":            "<username or user_id = Optional(=apiuser)>",
                   "description":      "<description>",
                   "copy_permissions": "<bool>",
                   "private":          "<bool>",
                   "landing_rev":      "<landing_rev>"
                 }

   Example error output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg": "Created fork of `<reponame>` as `<forkname>`",
                 "success": true,
                 "task": "<celery task id or None if done sync>"
               }
       error:  null


delete_repo
-----------

.. py:function:: delete_repo(apiuser, repoid, forks=<Optional:''>)

   Deletes a repository.

   * When the `forks` parameter is set it's possible to detach or delete
     forks of deleted repository.

   This command can only be run using an |authtoken| with admin
   permissions on the |repo|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Set the repository name or repository ID.
   :type repoid: str or int
   :param forks: Set to `detach` or `delete` forks from the |repo|.
   :type forks: Optional(str)

   Example error output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg": "Deleted repository `<reponame>`",
                 "success": true
               }
       error:  null


comment_commit
--------------

.. py:function:: comment_commit(apiuser, repoid, commit_id, message, userid=<Optional:<OptionalAttr:apiuser>>, status=<Optional:None>)

   Set a commit comment, and optionally change the status of the commit.
   This command can be executed only using api_key belonging to user
   with admin rights, or repository administrator.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Set the repository name or repository ID.
   :type repoid: str or int
   :param commit_id: Specify the commit_id for which to set a comment.
   :type commit_id: str
   :param message: The comment text.
   :type message: str
   :param userid: Set the user name of the comment creator.
   :type userid: Optional(str or int)
   :param status: status, one of 'not_reviewed', 'approved', 'rejected',
      'under_review'
   :type status: str

   Example error output:

   .. code-block:: json

       {
           "id" : <id_given_in_input>,
           "result" : {
               "msg": "Commented on commit `<commit_id>` for repository `<repoid>`",
               "status_change": null or <status>,
               "success": true
           },
           "error" :  null
       }


changeset_comment
-----------------

.. py:function:: changeset_comment(apiuser, repoid, revision, message, userid=<Optional:<OptionalAttr:apiuser>>, status=<Optional:None>)

   .. deprecated:: 3.4.0

      Please use method `comment_commit` instead.


   Set a changeset comment, and optionally change the status of the
   changeset.

   This command can only be run using an |authtoken| with admin
   permissions on the |repo|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Set the repository name or repository ID.
   :type repoid: str or int
   :param revision: Specify the revision for which to set a comment.
   :type revision: str
   :param message: The comment text.
   :type message: str
   :param userid: Set the user name of the comment creator.
   :type userid: Optional(str or int)
   :param status: Set the comment status. The following are valid options:
       * not_reviewed
       * approved
       * rejected
       * under_review
   :type status: str

   Example error output:

   .. code-block:: json

       {
           "id" : <id_given_in_input>,
           "result" : {
               "msg": "Commented on commit `<revision>` for repository `<repoid>`",
               "status_change": null or <status>,
               "success": true
           },
           "error" : null
       }


grant_user_permission
---------------------

.. py:function:: grant_user_permission(apiuser, repoid, userid, perm)

   Grant permissions for the specified user on the given repository,
   or update existing permissions if found.

   This command can only be run using an |authtoken| with admin
   permissions on the |repo|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Set the repository name or repository ID.
   :type repoid: str or int
   :param userid: Set the user name.
   :type userid: str
   :param perm: Set the user permissions, using the following format
       ``(repository.(none|read|write|admin))``
   :type perm: str

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg" : "Granted perm: `<perm>` for user: `<username>` in repo: `<reponame>`",
                 "success": true
               }
       error:  null


revoke_user_permission
----------------------

.. py:function:: revoke_user_permission(apiuser, repoid, userid)

   Revoke permission for a user on the specified repository.

   This command can only be run using an |authtoken| with admin
   permissions on the |repo|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Set the repository name or repository ID.
   :type repoid: str or int
   :param userid: Set the user name of revoked user.
   :type userid: str or int

   Example error output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg" : "Revoked perm for user: `<username>` in repo: `<reponame>`",
                 "success": true
               }
       error:  null


grant_user_group_permission
---------------------------

.. py:function:: grant_user_group_permission(apiuser, repoid, usergroupid, perm)

   Grant permission for a user group on the specified repository,
   or update existing permissions.

   This command can only be run using an |authtoken| with admin
   permissions on the |repo|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Set the repository name or repository ID.
   :type repoid: str or int
   :param usergroupid: Specify the ID of the user group.
   :type usergroupid: str or int
   :param perm: Set the user group permissions using the following
       format: (repository.(none|read|write|admin))
   :type perm: str

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       "msg" : "Granted perm: `<perm>` for group: `<usersgroupname>` in repo: `<reponame>`",
       "success": true

     }
     error :  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to edit permission for user group: `<usergroup>` in repo `<repo>`'
     }


revoke_user_group_permission
----------------------------

.. py:function:: revoke_user_group_permission(apiuser, repoid, usergroupid)

   Revoke the permissions of a user group on a given repository.

   This command can only be run using an |authtoken| with admin
   permissions on the |repo|.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repoid: Set the repository name or repository ID.
   :type repoid: str or int
   :param usergroupid: Specify the user group ID.
   :type usergroupid: str or int

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg" : "Revoked perm for group: `<usersgroupname>` in repo: `<reponame>`",
                 "success": true
               }
       error:  null


get_repo_group
--------------

.. py:function:: get_repo_group(apiuser, repogroupid)

   Return the specified |repo| group, along with permissions,
   and repositories inside the group

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repogroupid: Specify the name of ID of the repository group.
   :type repogroupid: str or int


   Example output:

   .. code-block:: bash

       {
         "error": null,
         "id": repo-group-id,
         "result": {
           "group_description": "repo group description",
           "group_id": 14,
           "group_name": "group name",
           "members": [
             {
               "name": "super-admin-username",
               "origin": "super-admin",
               "permission": "group.admin",
               "type": "user"
             },
             {
               "name": "owner-name",
               "origin": "owner",
               "permission": "group.admin",
               "type": "user"
             },
             {
               "name": "user-group-name",
               "origin": "permission",
               "permission": "group.write",
               "type": "user_group"
             }
           ],
           "owner": "owner-name",
           "parent_group": null,
           "repositories": [ repo-list ]
         }
       }


get_repo_groups
---------------

.. py:function:: get_repo_groups(apiuser)

   Returns all repository groups.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser


create_repo_group
-----------------

.. py:function:: create_repo_group(apiuser, group_name, description=<Optional:''>, owner=<Optional:<OptionalAttr:apiuser>>, copy_permissions=<Optional:False>)

   Creates a repository group.

   * If the repository group name contains "/", all the required repository
     groups will be created.

     For example "foo/bar/baz" will create |repo| groups "foo" and "bar"
     (with "foo" as parent). It will also create the "baz" repository
     with "bar" as |repo| group.

   This command can only be run using an |authtoken| with admin
   permissions.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param group_name: Set the repository group name.
   :type group_name: str
   :param description: Set the |repo| group description.
   :type description: str
   :param owner: Set the |repo| group owner.
   :type owner: str
   :param copy_permissions:
   :type copy_permissions:

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
         "msg": "Created new repo group `<repo_group_name>`"
         "repo_group": <repogroup_object>
     }
     error :  null


   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       failed to create repo group `<repogroupid>`
     }


update_repo_group
-----------------

.. py:function:: update_repo_group(apiuser, repogroupid, group_name=<Optional:''>, description=<Optional:''>, owner=<Optional:<OptionalAttr:apiuser>>, parent=<Optional:None>, enable_locking=<Optional:False>)

   Updates repository group with the details given.

   This command can only be run using an |authtoken| with admin
   permissions.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repogroupid: Set the ID of repository group.
   :type repogroupid: str or int
   :param group_name: Set the name of the |repo| group.
   :type group_name: str
   :param description: Set a description for the group.
   :type description: str
   :param owner: Set the |repo| group owner.
   :type owner: str
   :param parent: Set the |repo| group parent.
   :type parent: str or int
   :param enable_locking: Enable |repo| locking. The default is false.
   :type enable_locking: bool


delete_repo_group
-----------------

.. py:function:: delete_repo_group(apiuser, repogroupid)

   Deletes a |repo| group.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repogroupid: Set the name or ID of repository group to be
       deleted.
   :type repogroupid: str or int

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       'msg': 'deleted repo group ID:<repogroupid> <repogroupname>
       'repo_group': null
     }
     error :  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to delete repo group ID:<repogroupid> <repogroupname>"
     }


grant_user_permission_to_repo_group
-----------------------------------

.. py:function:: grant_user_permission_to_repo_group(apiuser, repogroupid, userid, perm, apply_to_children=<Optional:'none'>)

   Grant permission for a user on the given repository group, or update
   existing permissions if found.

   This command can only be run using an |authtoken| with admin
   permissions.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repogroupid: Set the name or ID of repository group.
   :type repogroupid: str or int
   :param userid: Set the user name.
   :type userid: str
   :param perm: (group.(none|read|write|admin))
   :type perm: str
   :param apply_to_children: 'none', 'repos', 'groups', 'all'
   :type apply_to_children: str

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg" : "Granted perm: `<perm>` (recursive:<apply_to_children>) for user: `<username>` in repo group: `<repo_group_name>`",
                 "success": true
               }
       error:  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to edit permission for user: `<userid>` in repo group: `<repo_group_name>`"
     }


revoke_user_permission_from_repo_group
--------------------------------------

.. py:function:: revoke_user_permission_from_repo_group(apiuser, repogroupid, userid, apply_to_children=<Optional:'none'>)

   Revoke permission for a user in a given repository group.

   This command can only be run using an |authtoken| with admin
   permissions on the |repo| group.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repogroupid: Set the name or ID of the repository group.
   :type repogroupid: str or int
   :param userid: Set the user name to revoke.
   :type userid: str
   :param apply_to_children: 'none', 'repos', 'groups', 'all'
   :type apply_to_children: str

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg" : "Revoked perm (recursive:<apply_to_children>) for user: `<username>` in repo group: `<repo_group_name>`",
                 "success": true
               }
       error:  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to edit permission for user: `<userid>` in repo group: `<repo_group_name>`"
     }


grant_user_group_permission_to_repo_group
-----------------------------------------

.. py:function:: grant_user_group_permission_to_repo_group(apiuser, repogroupid, usergroupid, perm, apply_to_children=<Optional:'none'>)

   Grant permission for a user group on given repository group, or update
   existing permissions if found.

   This command can only be run using an |authtoken| with admin
   permissions on the |repo| group.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repogroupid: Set the name or id of repository group
   :type repogroupid: str or int
   :param usergroupid: id of usergroup
   :type usergroupid: str or int
   :param perm: (group.(none|read|write|admin))
   :type perm: str
   :param apply_to_children: 'none', 'repos', 'groups', 'all'
   :type apply_to_children: str

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       "msg" : "Granted perm: `<perm>` (recursive:<apply_to_children>) for user group: `<usersgroupname>` in repo group: `<repo_group_name>`",
       "success": true

     }
     error :  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to edit permission for user group: `<usergroup>` in repo group: `<repo_group_name>`"
     }


revoke_user_group_permission_from_repo_group
--------------------------------------------

.. py:function:: revoke_user_group_permission_from_repo_group(apiuser, repogroupid, usergroupid, apply_to_children=<Optional:'none'>)

   Revoke permission for user group on given repository.

   This command can only be run using an |authtoken| with admin
   permissions on the |repo| group.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param repogroupid: name or id of repository group
   :type repogroupid: str or int
   :param usergroupid:
   :param apply_to_children: 'none', 'repos', 'groups', 'all'
   :type apply_to_children: str

   Example output:

   .. code-block:: bash

       id : <id_given_in_input>
       result: {
                 "msg" : "Revoked perm (recursive:<apply_to_children>) for user group: `<usersgroupname>` in repo group: `<repo_group_name>`",
                 "success": true
               }
       error:  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to edit permission for user group: `<usergroup>` in repo group: `<repo_group_name>`"
     }


get_gist
--------

.. py:function:: get_gist(apiuser, gistid, content=<Optional:False>)

   Get the specified gist, based on the gist ID.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param gistid: Set the id of the private or public gist
   :type gistid: str
   :param content: Return the gist content. Default is false.
   :type content: Optional(bool)


get_gists
---------

.. py:function:: get_gists(apiuser, userid=<Optional:<OptionalAttr:apiuser>>)

   Get all gists for given user. If userid is empty returned gists
   are for user who called the api

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param userid: user to get gists for
   :type userid: Optional(str or int)


create_gist
-----------

.. py:function:: create_gist(apiuser, files, owner=<Optional:<OptionalAttr:apiuser>>, gist_type=<Optional:u'public'>, lifetime=<Optional:-1>, acl_level=<Optional:u'acl_public'>, description=<Optional:''>)

   Creates a new Gist.

   :param apiuser: This is filled automatically from the |authtoken|.
   :type apiuser: AuthUser
   :param files: files to be added to the gist. The data structure has
       to match the following example::

         {'filename': {'content':'...', 'lexer': null},
          'filename2': {'content':'...', 'lexer': null}}

   :type files: dict
   :param owner: Set the gist owner, defaults to api method caller
   :type owner: Optional(str or int)
   :param gist_type: type of gist ``public`` or ``private``
   :type gist_type: Optional(str)
   :param lifetime: time in minutes of gist lifetime
   :type lifetime: Optional(int)
   :param acl_level: acl level for this gist, can be
       ``acl_public`` or ``acl_private`` If the value is set to
       ``acl_private`` only logged in users are able to access this gist.
       If not set it defaults to ``acl_public``.
   :type acl_level: Optional(str)
   :param description: gist description
   :type description: Optional(str)

   Example  output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       "msg": "created new gist",
       "gist": {}
     }
     error :  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to create gist"
     }


delete_gist
-----------

.. py:function:: delete_gist(apiuser, gistid)

   Deletes existing gist

   :param apiuser: filled automatically from apikey
   :type apiuser: AuthUser
   :param gistid: id of gist to delete
   :type gistid: str

   Example output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : {
       "deleted gist ID: <gist_id>",
       "gist": null
     }
     error :  null

   Example error output:

   .. code-block:: bash

     id : <id_given_in_input>
     result : null
     error :  {
       "failed to delete gist ID:<gist_id>"
     }
