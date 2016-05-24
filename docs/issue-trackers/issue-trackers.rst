.. _rhodecode-issue-trackers-ref:

Issue Tracker Integration
=========================

You can set an issue tracker connection in two ways with |RCE|.

* At instance level you can set a default issue tracker.
* At |repo| level you can configure an integration with a different issue
  tracker.

To integrate |RCM| with an issue tracker you need to define a regular
expression that will fetch the issue ID stored in commit messages and replace
it with a URL. This enables |RCE| to generate a link matching each issue to the
target |repo|.

Default Issue Tracker Configuration
-----------------------------------

To integrate your issue tracker, use the following steps:

1. Open :menuselection:`Admin --> Settings --> Issue Tracker`.
2. In the new entry field, enter the following information:

    * :guilabel:`Description`: A name for this set of rules.
    * :guilabel:`Pattern`: The regular expression that will match issues
      tagged in commit messages, or more see :ref:`issue-tr-eg-ref`.
    * :guilabel:`URL`: The URL to your issue tracker.
    * :guilabel:`Prefix`: The prefix with which you want to mark issues.

3. Select **Add** so save the rule to your issue tracker configuration.

Repository Issue Tracker Configuration
--------------------------------------

You can configure specific |repos| to use a different issue tracker if
you need to connect to a non-default one. See the instructions in
:ref:`repo-it`

.. _issue-tr-eg-ref:

Jira Integration
----------------

* Regex = ``(?:^#|\s#)(\w+-\d+)``
* URL = ``https://myissueserver.com/issue/${id}``
* Issue Prefix = ``#``

Confluence (Wiki)
-----------------

* Regex = ``(?:conf-)([A-Z0-9]+)``
* URL = ``https://example.atlassian.net/display/wiki/${id}/${repo_name}``
* issue prefix = ``CONF-``

Redmine Integration
-------------------

* Regex = ``(issue-+\d+)``
* URL = ``https://myissueserver.com/redmine/issue/${id}``
* Issue Prefix = ``issue-``

Redmine (wiki)
--------------

* Regex = ``(?:wiki-)([a-zA-Z0-9]+)``
* URL = ``https://example.com/redmine/projects/wiki/${repo_name}``
* Issue prefix = ``Issue-``

Pivotal Tracker
---------------

* Regex = ``(?:pivot-)(?<project_id>\d+)-(?<story>\d+)``
* URL = ``https://www.pivotaltracker.com/s/projects/${project_id}/stories/${story}``
* Issue prefix = ``Piv-``

Trello
------

* Regex = ``(?:trello-)(?<card_id>[a-zA-Z0-9]+)``
* URL = ``https://trello.com/example.com/${card_id}``
* Issue prefix = ``Trello-``
