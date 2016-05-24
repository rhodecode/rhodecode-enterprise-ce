.. _slack-int:

Integrate Slack
===============

To integrate |RCE| and Slack, you need to configure some things on the Slack
side of the integration, and some things on the |RCE| side.

On the Slack side you need to allow incoming webhooks, see their
documentation on this, `Slack Webhooks`_. You will also need to get an
Authorization Token from Slack that will allow |RCE| to post to your account.

On the |RCE| side, this is an overview of what you need to do:

1. Configure the built-in Slack extensions to post to the correct Slack URL.
2. Set your Slack authentication details in the |RCX| :file:`__init.py__` file.
3. Configure the different hooks in the :file:`__init.py__` file to extract
   whatever information you want from |RCE|, and then using the Slack extensions
   post that information to your Slack channel.

.. hint::

    The below examples should help you to get started. Once you have your
    integration up and running, there is a more detailed Slack integration in
    the :ref:`int-full-blown` section.

Configure Built-in Extensions
-----------------------------

|RCE| comes with 3 Slack extensions: ``slack_message.py``,
``slack_push_notify.py``, and ``slack.py``. The default
location is :file:`/home/{user}/.rccontrol/{instance-id}/rcextensions`.

To enable these to post to your Slack account, configure each of
these files with the following Slack details.

.. code-block:: python

    BASE_URL = 'https://your.slack.com/api/link'
    INCOMING_WEBHOOK_URL = 'https://hooks.slack.com/services/your/hook/link'
    API_VERSION = 1

Configure |RCE| to Post to Slack
--------------------------------

In the |RCX| :file:`__init.py__` file, configure your Slack authentication
details. The default location is
:file:`/home/{user}/.rccontrol/{instance-id}/rcextensions`

.. code-block:: python

    CONFIG = DotDict(
        slack=DotDict(
            api_key='api-key',
            api_url='slack-incoming-hook-url',
            default_room='#slack-channel',
            default_plugin_config={},
        ),
    )

    # slack conf
    CONFIG.slack.default_plugin_config = {
        'INCOMING_WEBHOOK_URL': CONFIG.slack.api_url,
        'SLACK_TOKEN': CONFIG.slack.api_key,
        'SLACK_ROOM': CONFIG.slack.default_room,
        'SLACK_FROM': 'RhodeCode',
        'SLACK_FROM_ICON_EMOJI': ':rhodecode:',
    }

Add Push Notifications to Slack
-------------------------------

To add notification to Slack when someone pushes to |RCE|, configure the push
hook to extract the commits pushed, and then call the built-in
``slack_push_notify.py`` extension to post them into your chosen Slack
channel. To do this, add the following code to the push hook section of the
:file:`__init.py__` file

.. code-block:: python
   :emphasize-lines: 10-16,18-22

    def _push_hook(*args, **kwargs):
        """
        POST PUSH HOOK, this function will be executed after each push, it's
        executed after the build-in hook that RhodeCode uses for logging pushes
        kwargs available:
        """
        # backward compat
        kwargs['commit_ids'] = kwargs['pushed_revs']

        # fetch pushed commits, from commit_ids list
        call = load_extension('extract_commits.py')
        extracted_commits = {}
        if call:
            extracted_commits = call(**kwargs)
            # store the commits for the next call chain
        kwargs['COMMITS'] = extracted_commits

        # slack !
        call = load_extension('slack_push_notify.py')
        if call:
            kwargs.update(CONFIG.slack.default_plugin_config)
            call(**kwargs)
        return 0
    PUSH_HOOK = _push_hook


Add Pull Request Notifications to Slack
---------------------------------------

To add |pr| notifications to Slack, use the following example. This example
shows a merged |pr| notification. You can add similar notifications to the
following hooks in the :file:`__init.py__` file, and for those examples see
the :ref:`int-full-blown` section:

* ``_create_pull_request_hook``
* ``_review_pull_request_hook``
* ``_update_pull_request_hook``
* ``_close_pull_request_hook``

.. code-block:: python
   :emphasize-lines: 5-23

    def _merge_pull_request_hook(*args, **kwargs):
        """

        """
        # extract below from source repo as commits are there
        kwargs['REPOSITORY'] = kwargs['source']['repository']

        # fetch pushed commits, from commit_ids list
        call = load_extension('extract_commits.py')
        extracted_commits = {}
        if call:
            extracted_commits = call(**kwargs)
            # store the commits for the next call chain
        kwargs['COMMITS'] = extracted_commits

        # slack notification on merging PR
        call = load_extension('slack_message.py')
        if call:
            kwargs.update(CONFIG.slack.default_plugin_config)
            kwargs['SLACK_ROOM'] = '#develop'
            kwargs['SLACK_MESSAGE'] = 'Pull request <%s|#%s> (%s) was merged.' % (
                kwargs.get('url'), kwargs.get('pull_request_id'), kwargs.get('title'))
            call(**kwargs)

        return 0
    MERGE_PULL_REQUEST = _merge_pull_request_hook

.. _Slack Webhooks: https://api.slack.com/incoming-webhooks
