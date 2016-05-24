.. _rebase-rebase-git:

How to Rebase in |git|
======================

Rebasing can take two form in |git|.

* Rebasing changes when you pull from upstream
* Rebasing one branch on top of another

If you need to understand more about branching, and the terminology, see the
:ref:`branch-wf` section.

Rebasing When Pulling from Upstream
-----------------------------------

This will pull any changes from the remote server, and rebase the changes on
your local branch on top of them.

.. code-block:: bash

    # Move to the branch you wish to rebase
    $ git checkout branchname

    # Pull changes on master and rebase on top of latest changes
    $ git pull --rebase upstream master

    # Push the rebase to origin
    $ git push -f origin branchname

Rebasing Branches
-----------------

Rebasing branches in |git| means that you take one branch and rebase the work
on that branch on top of another. In the following example, the
``triple`` branch will be rebased on top of the ``second-pass`` branch.

1. List the available branches in your |repo|.

.. code-block:: bash

    $ git branch
      first-pass
    * master
      second-pass
      triple

2. Rebase the ``triple`` on top of the ``second-pass`` branch.

.. code-block:: bash

    $ git rebase second-pass triple
    First, rewinding head to replay your work on top of it...
    Fast-forwarded triple to second-pass.
