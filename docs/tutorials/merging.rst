.. _merging:

Merging in |hg|
===============

Sometimes you will need to fix conflicts when merging files. In |hg| there
are a number of different options which you can use for handling merging, and
you can set your preferred one in the :file:`~/.hgrc` file. The options fall
into two categories *internal merging* or *tool merging*.

Internal merging marks the files with the ``<<<<<``,
``>>>>>``, and ``=======`` symbols denoting the position of the conflict
in the file and you resolve the changes on your terminal. The following
example sets `Meld`_ as the merge handler.

.. code-block:: ini

   [ui]
   merge = internal:merge

Tool merging differs slightly depending on the tool you use, but they will
all do the same thing. Highlight the conflict area in some manner, and allow
you to make the necessary changes to resolve the conflicts. Set a merge tool
using the following example.

.. code-block:: ini

    [merge-tools]
    meld3.executable = /usr/local/bin/meld

For more detailed information, see the :ref:`basic-vcs-cmds` section, or the
`Mercurial merge-tools`_ documentation. Use the following example steps to
handle merging conflicts.

1. Check the list of conflicts on the command line, in this example
   you can see the list as the ``default`` and ``stable`` branches are in the
   process of being merged.

.. code-block:: bash
    :emphasize-lines: 10-12,16-17,20-21

    $ hg branch
    stable
    $ hg merge default
    note: using 4480fbc4562c as ancestor of 7c9a8dfb9dd6 and fbefb727a452
          alternatively, use --config merge.preferancestor=a1e8bd6df0ce
    merging default.nix
    merging docs-internal/changelog.rst
    merging rhodecode/VERSION
    merging rhodecode/controllers/api/utils.py
    warning: conflicts during merge.
    merging rhodecode/controllers/api/utils.py incomplete!
    (edit conflicts, then use 'hg resolve --mark')
    merging rhodecode/lib/diffs.py
    merging rhodecode/model/scm.py
    merging rhodecode/tests/api/test_utils.py
    warning: conflicts during merge.
    merging rhodecode/tests/api/test_utils.py incomplete!
    (edit conflicts, then use 'hg resolve --mark')
    merging rhodecode/tests/models/test_scm.py
    warning: conflicts during merge.
    merging rhodecode/tests/models/test_scm.py incomplete!
    (edit conflicts, then use 'hg resolve --mark')
    merging vcsserver/default.nix
    merging vcsserver/vcsserver/VERSION
    42 files updated, 7 files merged, 2 files removed, 3 files unresolved
    use 'hg resolve' to retry unresolved file merges or 'hg update -C .' to abandon


2. Open each of the highlighted files, and fix the conflicts in each. Each merge
   conflict will look something like the following example, with the ``<<<<<``,
   ``>>>>>``, and ``=======`` symbols denoting the position of the conflict
   in the file. You need to fix the content so that it is correct.

.. code-block:: python

    # Change this example conflict
    def pre_request(worker, req):
    <<<<<<<<<<<<<<
        worker.log.debug("[%s] PRE WORKER: %s" %(worker.pid, req.method))
     ===============
        worker.log.debug("[%s] PRE WORKER: %s %s" % (worker.pid, req.method,
        req.path))
    >>>>>>>>>>>>>>

    # To this working code
    def pre_request(worker, req):
        worker.log.debug("[%s] PRE WORKER: %s %s" % (worker.pid, req.method,
        req.path))

3. Once you have finished fixing the conflicts, you need to mark them as
   resolved, and then commit the changes.

.. code-block:: bash

   # Mark the merges as resolved
   $ hg resolve --mark

   # Commit the changes
   $ hg commit -m "merge commit message"

5. Once you have finished your merge, if the the original |repo| history on
   the server is different you have two options:

   * Push with force using ``hg push --force`` which will create a new head.
   * Strip your commits on the server back to a previous revision, and then push
     the new history. To strip commits on the server, see the ``strip``
     information in the :ref:`api` documentation.

.. _Mercurial merge-tools: https://mercurial.selenic.com/wiki/MergeToolConfiguration
.. _Meld: http://meldmerge.org/