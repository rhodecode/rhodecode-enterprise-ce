.. _rc-ext:

|RCX|
-----

|RCX| add additional functionality for push/pull/create/delete |repo| hooks.
These hooks can be used to send signals to build-bots such as `Jenkins`_. It
also adds built in plugin and extension support. Once installed, you will see
a :file:`rcextensions` folder in the instance directory, for example:
:file:`home/{user}/.rccontrol/{instance-id}/rcextensions`

Built-in Plugins
^^^^^^^^^^^^^^^^

* A number of `Jira`_ plugins, enabling you to integrate with that issue
  tracker: ``extract_jira_issues.py``, ``jira_pr_flow.py``,
  ``jira_smart_commits.py``
* A number of `Redmine`_ plugins, enabling you to integrate with that issue
  tracker: ``extract_redmine_issues.py``, ``redmine_pr_flow.py``,
  ``redmine_smart_commits.py``.
* ``hipchat.py`` and ``hipchat_push.py`` enable you to integrate with
  `HipChat`_ and set channel or user notifications.
* ``slack.py``, ``slack_message.py``, and ``slack_push_notify.py`` enable
  you to integrate with `Slack`_ and set channel or user notifications.

Built-in Extensions
^^^^^^^^^^^^^^^^^^^

* ``commit_parser.py``: Enables you to parse commit messages,
  and set a list of users to get notifications about change sets.
* ``default_reviewers.py``: Enables you to add default reviewers to a |pr|.
* ``extra_fields.py``: Returns a list of extra fields added to a |repo|.
* ``http_notify``: Enables you to send data over a web hook.
* ``mail.py`` : This extension uses the |RCE| mail configuration from the
  instance :file:`rhodecode.ini` file to send email.
* ``push_post.py``: Enables you to set up push based actions such as
  automated Jenkins builds.

Event Listeners
^^^^^^^^^^^^^^^

To enable the extensions to listen to the different events that they are
configured for, you need to also set up an event listener (hook). Event
listeners are configured in the
:file:`/home/{user}/.rccontrol/{instance-id}/rcextensions/__init.__.py` file.

For more details, see the example hook in :ref:`event-listener`.

.. _Jenkins: http://jenkins-ci.org/
.. _HipChat: https://www.hipchat.com/
.. _Slack: https://slack.com/
.. _Redmine: http://www.redmine.org/
.. _Jira: https://www.atlassian.com/software/jira
