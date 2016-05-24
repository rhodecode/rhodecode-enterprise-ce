.. _hooks:

Hooks
-----

Within |RCM| there are two types of supported hooks.

* **Internal built-in hooks**: The internal |hg| or |git| hooks are
  triggered by different VCS operations, like push, pull,
  or clone and are non-configurable, but you can add your own VCS hooks,
  see :ref:`custom-hooks`.
* **User defined hooks**: User defined hooks centre around the lifecycle of
  certain actions such are |repo| creation, user creation etc. The actions
  these hooks trigger can be rejected based on the API permissions of the
  user calling them.

Those custom hooks can be called using |RCT|, see :ref:`rc-tools`. To create
a custom hook, see the :ref:`event-listener` section.

.. _event-listener:

Making your Extension listen for Events
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To create a hook to work with a plugin or extension,
you need configure a listener in the
:file:`/home/{user}/{instance-id}/rcextensions/__init__.py` file,
and use the ``load_extension`` method.

Use the following example to create your extensions.
In this example:

* The hook is calling the ``('my_post_push_extension.py')`` extension.
* The hook is listening to |RCM| for pushes to |repos|.
* This highlighted code is the hook, and configured in the ``__init__.py`` file.
* It is inserted into the ``def _pushhook(*args, **kwargs)`` section,
  if it is not in the default ``__ini__.py`` file, use the below
  non-highlighted section to create it.

.. code-block:: python
   :emphasize-lines: 23-38

    # ==========================================================================
    #  POST PUSH HOOK
    # ==========================================================================

    # this function will be executed after each push is executed after the
    # build-in hook that RhodeCode uses for logging pushes
    def _pushhook(*args, **kwargs):
        """
        Post push hook
        kwargs available:

          :param server_url: url of instance that triggered this hook
          :param config: path to .ini config used
          :param scm: type of VS 'git' or 'hg'
          :param username: name of user who pushed
          :param ip: ip of who pushed
          :param action: push
          :param repository: repository name
          :param repo_store_path: full path to where repositories are stored
          :param pushed_revs: list of pushed revisions
        """

        # Your hook code goes in here
        call = load_extension('my_post_push_extension.py')
        if call:
            # extra arguments in kwargs
            call_kwargs = dict()
            call_kwargs.update(kwargs)
            my_kw = {
                'reviewers_extra_field': 'reviewers',
                # defines if we have a comma
                # separated list of reviewers
                # in this repo stored in extra_fields
            }
            call_kwargs.update(my_kw) # pass in hook args
            parsed_revs = call(**call_kwargs)
            # returns list of dicts with changesets data

        # Default code
        return 0
    PUSH_HOOK = _pushhook

Once your plugin and hook are configured, restart your instance of |RCM| and
your event listener will triggered as soon as a user pushes to a |repo|.
