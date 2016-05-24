.. _squash-rebase:

How to Squash Commits in |hg|
=============================

To squash commits in |hg| you will need the ``histedit`` extensions enabled
in your :file:`~/.hgrc` file. Use the following example, or for more detailed
information see the :ref:`config-hgrc` section.

.. code-block:: ini

    [extensions]
    histedit =

Squashing Commits
-----------------

To squash commits, use the following instructions.

1. Using ``hg log``, or ``hg glog``, check your repository history and
   choose the revision upon which you want to squash commits.
2. The commit status needs to be in draft. If necessary, change the commit
   status to draft back as far as the chosen revision, using
   the following command: ``hg phase --draft --force -r rev-id``. It's not
   best practices to use ``--force`` on a main |repo|, but this example is
   based on a fork. To learn more about phases, read the `Mercurial Phases`_
   docs. See the following example:

.. code-block:: bash

    # Put commits into draft status if needed
    hg phase --draft --force -r 9039

    # Check the changlog to ensure the commits are in draft
    @  9041:c680f30edc60 [default] - draft
    |  7 weeks ago by Johannes Bornhold | B:,T:tip
    |  nix: Add version of transifex-client into default.nix
    |
    o  9040:66f03981cfcd [default] - draft
    |  7 weeks ago by lisaq | B:,T:
    |  fixes #1592 removing legacy css files
    |
    o  9039:388db711042f [default] - draft
    |  7 weeks ago by Brian | B:,T:
    |  docs: fixed *doCheck = false* with propogatedbuildinputs fragment
    |
    o  9038:ef41dce16c12 [default] - public
    |  8 weeks ago by Brian | B:,T:
    |  Docs: updating dependencies for Sphinx 131, but staying at 122 for now

3. Once the commits are in draft, run the ``hg histedit rev-id`` command,
   specifying the earliest draft commit. This will open the history edit
   function in your terminal, allowing you to fold the commit messages into
   one. Select a commit to use as the one into which the others will be
   squashed. Then save the file.

.. code-block:: bash

    # Run the history edit specifying the base revision
    hg histedit 9039

    pick 388db711042f 9039 docs: fixed *doCheck = false* with propogatedbuildinputs
    fold 66f03981cfcd 9040 fixes #1592 removing legacy css files
    fold c680f30edc60 9041 nix: Add version of transifex-client into default.nix

    # Edit history between 388db711042f and c680f30edc60
    #
    # Commits are listed from least to most recent
    #
    # Commands:
    #  p, pick = use commit
    #  e, edit = use commit, but stop for amending
    #  f, fold = use commit, but combine it with the one above
    #  d, drop = remove commit from history
    #  m, mess = edit message without changing commit content

4. Once those settings are saved, the terminal will open up an editor and you
   can change the commit message. When finished, save again.

.. code-block:: bash

   # add a new commit message or keep the original one
   docs: added translations and packaging. Squashed commit.

   # adding HG: in front of a line will remove it once saved
   HG:docs: added translations and packaging. Squashed commit.
   HG:nix: Add version of transifex-client into default.nix
   HG:docs: fixed *doCheck = false* with propogatedbuildinputs fragment

5. Your commit messages will now be squashed into a single commit. You will
   also get a message about a backup bundle where |hg| will store the history of
   the squashed commit.

.. code-block:: bash

    3 files updated, 0 files merged, 0 files removed, 0 files unresolved
    saved backup bundle to /tutorials-fork/.hg/strip-backup/38b711042f-backup.hg
    saved backup bundle to /tutorials-fork/.hg/strip-backup/f19da9449f-backup.hg

6. See the squashed commit message using the ``hg log`` or ``hg glog`` command.

.. code-block:: bash

    @  9039:44e6fc3bf6b5 [default] - draft
    |  7 weeks ago by Brian | B:,T:tip
    |  docs: added translations and packaging. Squashed commit.
    |
    o  9038:ef41dce16c12 [default] - draft
    |  8 weeks ago by Brian | B:,T:
    |  Docs: updating dependencies for Sphinx 131, but staying at 122
    |
    o    9037:411a82632f54 [default] - draft
    |\   7 weeks ago by Johannes Bornhold | B:,T:
    | |  release: Merge back stable into default after release 3.2.1


7. Once you have squashed the commits, to push these changes to the server you
   have two options:

   * Push with force using ``hg push --force`` which will create a new head.
   * Strip your commits on the server back to a previous revision, and then push
     the new history. To strip commits on the server, see the ``strip``
     information in the :ref:`api` documentation.

.. _Mercurial Phases: https://mercurial.selenic.com/wiki/Phases
