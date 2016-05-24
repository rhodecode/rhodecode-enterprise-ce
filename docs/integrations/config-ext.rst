.. _config-ext:

Configure |RCX|
---------------

To get the the built in plugins and extensions working the way you want them
to, you have to configure them to work with your services. An overview of
what needs to be done is:

* :ref:`config-rcx-plugin` to carry out your desired actions once its hook is
  triggered. There are default actions built in, but you may wish to alter
  those.
* :ref:`config-rcx-hook` to execute actions for the plugin, when certain
  actions are carried out with |RCE|.

.. _config-rcx-plugin:

Tweak a Default Plugin
^^^^^^^^^^^^^^^^^^^^^^

Each of the default plugins comes with a standard configuration, but you may
wish to change those settings. In this example, the Redmine plugin watches
for the words defined in the ``HASH_REGEX`` variable and takes actions if one
of those words is used in conjunction with a ``#{number}``, which matches a
ticket number in Redmine. You can configure this to work differently based on
the `Redmine documentation`_.

.. code-block:: python
   :emphasize-lines: 3-5, 37

    import re

    HASH_REGEX = re.compile(
        r"(?:fix|fixes|fixing|close|closes|closing)\s*#([0-9]+)\b",
        re.IGNORECASE)


    def link_to_commit(repo_url, commit_id):
        rev_url = '%s/changeset/%s' % (repo_url, commit_id)
        return '"%s":%s' % (commit_id[:6], rev_url)


    def run(*args, **kwargs):
        issues = kwargs['RM_ISSUES']
        if not issues:
            return 0

        # repo extra fields can control this, they should be propagated with
        # extract repo fields
        tracker_url = kwargs.get('redmine_tracker_url') or kwargs['RM_URL']
        project_id = kwargs.get('redmine_project_id') or kwargs['RM_PROJECT']
        api_key = kwargs.get('redmine_api_key') or kwargs['RM_APIKEY']

        if project_id:
            from redmine import Redmine
            remote_redmine = Redmine(tracker_url, key=api_key)
            project = remote_redmine.project.get(project_id)
            repo_url = '%(server_url)s/%(repository)s' % kwargs
            # for each fetched issue id make a redmine api call
            for _id, details in issues.items():
                commits = ', '.join([link_to_commit(repo_url,
                                                    x['raw_id'],)
                                                    for x in details])
                issue = project.issues.get(int(_id))
                if issue:
                    issue.notes = 'Issue resolved by %s' % (commits,)
                    issue.status_id = 3  # Resolved
                    issue.save()


.. _config-rcx-hook:

Configure a Hook
^^^^^^^^^^^^^^^^

To configure the default hooks in the
:file:`/home/{user}/.rccontrol/{instance-id}/rcextensions/__init.py__` file,
use the following steps.

1. Configure the connection details, either in the file or import from a
   dictionary. For these connection scenarios the following details need to
   be configured.

* **REDMINE_URL** = '<redmine-url>'
* **REDMINE_API_KEY** = '<secret>'
* **SLACK_API_URL** = '<slack-url>?token=<secret>'
* **SLACK_API_KEY** = '<secret>'

2. You will also need to configure other variables, such as the
   **SLACK_ROOM** or **RM_PROJECT** (Redmine Project). These set where the
   commit message is posted. Various hooks can take different variables and
   they are documented in the file.

3. Inside each hook you can then configure it to carry out actions
   per service. In this example, the push hook is pushing to the Redmine and
   Slack plugins on each push if the hook criteria are matched.

.. code-block:: python
   :emphasize-lines: 21-29, 37-44

    def _push_hook(*args, **kwargs):
        kwargs['commit_ids'] = kwargs['pushed_revs']

        call = load_extension('extra_fields.py')
        if call:
            repo_extra_fields = call(**kwargs)
            # now update if we have extra fields, they have precedence
            # this way users can store any configuration inside
            # the database per repo
            for key, data in repo_extra_fields.items():
                kwargs[key] = data['field_value']

        # fetch pushed commits
        call = load_extension('extract_commits.py')
        extracted_commits = {}
        if call:
            extracted_commits = call(**kwargs)
            # store the commits for the next call chain
        kwargs['COMMITS'] = extracted_commits

        # slack !
        call = load_extension('slack.py')
        if call:
            kwargs['INCOMING_WEBHOOK_URL'] = SLACK_API_URL
            kwargs['SLACK_TOKEN'] = SLACK_API_KEY
            kwargs['SLACK_ROOM'] = '#slack-channel'
            kwargs['SLACK_FROM'] = 'Slack-Message-Poster'
            kwargs['SLACK_FROM_ICON_EMOJI'] = ':slack-emoji:'
            call(**kwargs)

        # fetch issues from given commits
        call = load_extension('extract_issues.py')
        issues = {}
        if call:
            issues = call(**kwargs)

        # redmine smart commits
        call = load_extension('redmine_smart_commits.py')
        if call:
            kwargs['RM_URL'] = REDMINE_URL
            kwargs['RM_APIKEY'] = REDMINE_API_KEY
            kwargs['RM_PROJECT'] = None  # uses extra_fields from repo
            kwargs['RM_ISSUES'] = issues
            call(**kwargs)

        return 0
    PUSH_HOOK = _push_hook


.. _Redmine documentation: http://www.redmine.org/projects/redmine/wiki/Rest_api
