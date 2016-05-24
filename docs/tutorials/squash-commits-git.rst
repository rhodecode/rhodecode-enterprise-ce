.. _squash-git:

How to Squash Commits in |git|
==============================

To squash commits in |git|, use the following steps.

1. Use ``git log`` to view the commits messages on your branch, and decide
   how many you want to squash into one commit.

2. Using the ``rebase`` command, chose the number of commits you wish to
   squash. This will then open the list of commits in your default editor
   allowing you to chose what to do with each.

.. code-block:: bash

    # Squash the last 4 commits
    $ git rebase -i HEAD~4

3. When the editor opens, pick the main commit, and the commits you wish
   to squash, and then save. This will then open the editor on the
   next phase where you can edit the picked commit.

.. code-block:: bash

    pick 575447a realign bike handlebars
    s 583e99c Add hipster bullhorn handlebars (dont judge me)
    s 8829a05 Add initial disc brakes for stopping
    s 91322e6 Add BikeEvent administration

    # Rebase d839c1a..583e99c onto d839c1a (2 TODO item(s))
    #
    # Commands:
    # p, pick = use commit
    # r, reword = use commit, but edit the commit message
    # e, edit = use commit, but stop for amending
    # s, squash = use commit, but meld into previous commit
    # f, fixup = like "squash", but discard this commits log message
    # x, exec = run command (the rest of the line) using shell

4. Edit the picked commit to explain the squash in more detail, and then save.

.. code-block:: bash

    # This is a combination of 4 commits.
    # The first commit's message is:

    The full bike setup, with brakes, handlebars, and alignment fixed.

5. Using ``git log``, you should now see your squashed commit message

.. code-block:: bash

    $ git log
    commit c5424b2619b1a7c01f817279df787660c76081ea
    Author: user <user@ubuntu>
    Date:   Wed Nov 4 19:45:37 2015 +0100

        The full bike setup, including handlebars, brakes, and alignment.

6. If you have already push to the remote |repo|, you will need to push your
   changes using force, ``git push --force``
