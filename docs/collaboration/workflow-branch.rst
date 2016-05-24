.. _branch-wf:

Branching Workflow
==================

The branching workflow is usually used with specific guidelines about how to
use and name branches. A general rule of thumb is that each branch should be
specifically named and used for a defined purpose. See the
:ref:`forks-branches-ref` section for detailed steps about how to create
branches.

.. code-block:: bash

    # Mercurial Branch
    $ hg bookmark issue-568

    # Git Branch
    $ git branch issue-568
    $ git checkout issue-568


Branching Overview
------------------

.. image:: ../images/git-flow-diagram.png
    :align: center

:Legend: The following code examples correspond with the numbered steps in
    the diagram.

.. code-block:: bash

    #1 clone your fork locally and pull the latest changes from upstream
    $ git clone git://your-fork
    $ git pull --rebase upstream master

    #2 create a new branch
    $ git checkout -b branch-1

    #3 push the branch to your remote fork
    $ git push origin branch-1

    #4  Open a pull request from your fork to upstream/master

    #5 Merge your pull request with the upstream/master
    $ git merge --no-ff pull request

    #6 pull and rebase your work plus any other work to your local branch
    $ git checkout master
    $ git pull --rebase upstream master

    #7 push the new commit history to your fork
    $ git push origin master



Setting up a Branching Workflow
-------------------------------

Setting up a branching workflow requires giving users access to the |repo|.
For more information, see the :ref:`permissions-info-add-group-ref` section.

Using a Branching Workflow
--------------------------

If you are on a team that uses a branching workflow, see the
:ref:`forks-branches-ref` section for how to create branches, and also the
:ref:`pull-requests-ref` section. You may also find the
:ref:`squash-rebase` section useful.

