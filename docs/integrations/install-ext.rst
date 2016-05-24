.. _install-rcx:

Install |RCX|
-------------

To install |RCX|, you need to have |RCT| installed. See the :ref:`install-tools`
and :ref:`tools-cli` sections. Use the ``--plugins`` option with
the ``rhodecode-extensions`` argument.

Upgrading |RCX|
^^^^^^^^^^^^^^^

.. important::

   You should back up any plugins or extensions that you have created before
   continuing.

To upgrade your |RCX|, use the following example:

1. From inside the |RCT| virtualenv, upgrade to the latest version:

.. code-block:: bash

    (venv)$ pip install -U https://my.rhodecode.com/dl/rhodecode-tools/latest
    Downloading/unpacking https://my.rhodecode.com/dl/rhodecode-tools/latest
      Downloading latest (143kB): 143kB downloaded
      Running setup.py (path:/tmp/pip-9qYsxf-build/setup.py) egg_info
      for package from https://my.rhodecode.com/dl/rhodecode-tools/latest

2. Once |RCT| are upgraded to the latest version, you can install the latest
   extensions using the following example:

.. code-block:: bash

    (venv)$ rhodecode-extensions --instance-name=enterprise-1 \
    --ini-file=rhodecode.ini --plugins

    Extension file already exists, do you want to overwrite it? [y/N]: y
    Writen new extensions file to rcextensions
    Copied hipchat_push_notify.py plugin to rcextensions
    Copied jira_pr_flow.py plugin to rcextensions
    Copied default_reviewers.py plugin to rcextensions
    Copied extract_commits.py plugin to rcextensions
    Copied extract_issues.py plugin to rcextensions
    Copied redmine_pr_flow.py plugin to rcextensions
    Copied extra_fields.py plugin to rcextensions
    Copied jira_smart_commits.py plugin to rcextensions
    Copied http_notify.py plugin to rcextensions
    Copied slack_push_notify.py plugin to rcextensions
    Copied slack_message.py plugin to rcextensions
    Copied extract_jira_issues.py plugin to rcextensions
    Copied extract_redmine_issues.py plugin to rcextensions
    Copied redmine_smart_commits.py plugin to rcextensions
    Copied send_mail.py plugin to rcextensions

