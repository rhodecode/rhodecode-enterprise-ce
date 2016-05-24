.. _rebase-rebase:

How to Rebase in |hg|
=====================

To rebase in |hg| you will need the ``rebase`` extensions enabled in your
:file:`~/.hgrc` file. Use the following example, or for more detailed
information see the :ref:`config-hgrc` section.

.. code-block:: ini

    [extensions]
    rebase =

Rebasing in |hg|
----------------

Occasionally you may have to rebase commits if you have created a new head on
your fork. In short, rebasing mean taking one commit and moving a commit, or
set of commits, from a different head on top of it. To do this, use the
following example:

1. Check your on the right branch, and move to the correct one if needed.

.. code-block:: bash

    # Display which branch you are on
    $ hg branch
    default

    # Move to the stable branch
    $ hg update stable

2. Look at your graphlog, and decide what commits need to be rebased. In this
   case, I want to rebase 1206 and 1207 on top of 1226. Note how these are
   already in a public state as I have already pushed to my fork.

.. code-block:: bash
   :emphasize-lines: 1,13,17

    | o  1226:1046ed30734d [stable] - public
    | |  3 days ago by Oliver Strobel | B:,T:
    | |  enterprise: catch failure to create repo_dir
    | |
    | o  1225:7aba10b8ee97 [stable] - public
    | |  3 days ago by Oliver Strobel | B:,T:
    | |  control: bump version to 1.1.9
    | |
    o |  1208:0ef7c9d4c1cc [default] - public
    | |  2 weeks ago by Oliver Strobel | B:,T:
    | |  Added tag 1.1.7 for changeset 3acf64b88845
    | |
    | | @  1207:39562e195e34 [stable] - public
    | | |  3 weeks ago by Brian | B:,T:
    | | |  docs: note added to *rccontrol install* regarding overwriting DB
    | | |
    | | o  1206:39562e195e34 [stable] - public
    | |/   3 weeks ago by Brian | B:,T:
    | |    docs: update command line install example

3. To do this use the following example.

   * Draft the commits back to the source revision.
   * ``-s`` is the source, essentially what you are rebasing.
   * ``-d`` is the destination, which is where you are putting it.

Rebasing the source commit will automatically rebase its descendants. In this
example I am using ``--force`` to draft commits already pushed to my fork.
Doing this is not best practices on a main |repo|.

.. code-block:: bash

    # Put the commits into draft status
    # This will draft all subsequent commits on the relevant branch
    hg phase --draft --force -r 1206

    # Rebase 1206 on top of 1226
    $ hg rebase -s 1206 -d 1226
    saved backup bundle to /repo-fork/.hg/strip-backup/39562e195e34-backup.hg

4. Once you have rebased the commits, check them on the graphlog

.. code-block:: bash
   :emphasize-lines: 1,5,9


    o  1233:707ef1590e71 [stable] - draft
    |  3 weeks ago by Brian | B:,T:tip
    |  docs: note added to *rccontrol install* regarding overwriting DB
    |
    o  1232:707ef1590e71 [stable] - draft
    |  3 weeks ago by Brian | B:,T:tip
    |  docs: update command line install example
    |
    @ |  1225:1046ed30734d [stable] - draft
    | |  3 days ago by Oliver Strobel | B:,T:
    | |  enterprise: catch failure to create repo_dir

5. Once you have finished your rebase, if the the original |repo| history on
   the server is different you have two options:

   * Push the specific revisions using ``hg push -r <revision>``, or push all
     with force using ``hg push --force`` which will create a new head.
   * Strip your commits on the server back to a previous revision, and then push
     the new history. To strip commits on the server, see the ``strip``
     information in the :ref:`api` documentation.

.. important::

   As with all examples, this one is rather straight forward but rebasing can
   become a complicated affair if you need to fix merges and conflicts
   during the rebase. For more detailed rebasing information, see the
   `Mercurial Rebase`_ page which has more detailed instructions for various
   scenarios.

.. _Mercurial Rebase: https://mercurial.selenic.com/wiki/RebaseExtension
.. _Mercurial Phases: https://mercurial.selenic.com/wiki/Phases

