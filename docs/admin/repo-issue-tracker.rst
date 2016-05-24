.. _repo-it:

Repository Issue Tracker
========================

You can set an issue tracker connection in two ways with |RCE|.

* At instance level, for more information see the
  :ref:`rhodecode-issue-trackers-ref` section.
* At |repo| level. This allows you to configure a |repo| to use a different
  issue tracker to the default one.

Set an Issue Tracker per Repository
-----------------------------------

To configure a |repo| to work with a different issue tracker to the default one,
use the following steps:

1. Open :menuselection:`Admin --> Repositories --> repo name --> Edit --> Issue Tracker`
2. Uncheck the :guilabel:`Inherit from default settings` box.
3. Click :guilabel:`Add New`.
4. Fill in the following settings:

    * :guilabel:`Description`: A name for this set of rules.
    * :guilabel:`Pattern`: The regular expression that will match issues
      tagged in commit messages, or more see :ref:`issue-tr-eg-ref`.
    * :guilabel:`URL`: The URL to your issue tracker.
    * :guilabel:`Prefix`: The prefix with which you want to mark issues.

5. Click :guilabel:`Save`.
