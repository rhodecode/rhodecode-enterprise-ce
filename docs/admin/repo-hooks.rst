.. _repo-hooks:

|RCE| Repository Hooks
======================

|RCE| installs hooks inside each of the |repos| that it manages. These
hooks enable users to execute custom actions based on certain events.
This is the complete list of |repos| hooks and the events which trigger them:

.. rst-class:: dl-horizontal

    \--CREATE_REPO_HOOK
        Any time a |repo| is created.

    \--CREATE_REPO_GROUP_HOOK
        Any time a |repo| group is created.

    \--CREATE_USER_HOOK
        Any time a user is created.

    \--DELETE_REPO_HOOK
        Any time a |repo| is created.

    \--DELETE_USER_HOOK
        Any time a user is deleted.

    \--PRE_CREATE_USER_HOOK
        Any time a user is created but before the action is executed by |RCE|.

    \--PRE_PULL
        Any pull from a |repo| but before the action is executed by |RCE|.

    \--PRE_PUSH
        Any push to a |repo| but before the action is executed by |RCE|.

    \--POST_PUSH
        After any push to a |repo|.

    \--PUSH_HOOK
        Any push to a |repo|, including editing tags or branches.
        Commits via API actions that update references are also counted.

    \--PULL_HOOK
        Any pull from a Repository.

Using Repository Hooks
----------------------

To use these hooks you need to install |RCX|. For more information, see the
:ref:`install-rcx` section.

Creating Extensions
-------------------

To create your own extensions using these hooks, see the :ref:`dev-plug`
section.
