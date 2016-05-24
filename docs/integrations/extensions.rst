.. _dev-plug:

Developing Plugins/Extensions
-----------------------------

An Extension or a Plugin is simply a |PY| module with a ``run`` method that
expects a number of parameters, depending on which event it is listening
for. To get an extension working, use the following steps:

1. Create an extension or plugin using the below example.
2. Save the plugin inside the
   :file:`/home/{user}/.rccontrol/{instance-id}/rcextensions` folder.
3. Add a hook to the
   :file:`/home/{user}/.rccontrol/{instance-id}/rcextensions/__init__.py` file.
   For more information, see :ref:`event-listener`.
4. Restart your |RCM| instance.

Extension example
^^^^^^^^^^^^^^^^^

In the following example, the ``run`` method listens for a push to a |repo|
and parses the commit.

.. code-block:: python

	def run(*args, **kwargs):

	    revs = kwargs.get('pushed_revs')
	    if not revs:
	        return 0

	    from rhodecode.lib.utils2 import extract_mentioned_users
	    from rhodecode.model.db import Repository

	    repo = Repository.get_by_repo_name(kwargs['repository'])
	    changesets = []
	    reviewers = []

	    # reviewer fields from extra_fields, users can store their custom
	    # reviewers inside the extra fields to pre-define a set of people who
	    # will get notifications about changesets
	    field_key = kwargs.get('reviewers_extra_field')
	    if field_key:
	        for xfield in repo.extra_fields:
	            if xfield.field_key == field_key:
	                reviewers.extend(xfield.field_value.split())

	    vcs_repo = repo.scm_instance_no_cache()
	    for rev in kwargs['pushed_revs']:
	        cs = vcs_repo.get_changeset(rev) # or get_commit. See API doc
	        cs_data = cs.__json__()
	        cs_data['mentions'] = extract_mentioned_users(cs_data['message'])
	        cs_data['reviewers'] = reviewers
	        # optionally add more logic to parse the commits, like reading extra
	        # fields of repository to read managers of reviewers
	        changesets.append(cs_data)

	    return changesets
	    