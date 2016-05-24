
|hg| Getting Started
--------------------

To work locally with |hg| |repos|, use the following configuration examples
and command line instructions.

* :ref:`config-hgrc`
* :ref:`config-hgignore`
* :ref:`basic-hg-cmds`

.. _config-hgrc:

Configure the ``.hgrc`` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :file:`~/.hgrc` file is a configuration file which control how |hg|
interacts between the server and your local setup.

For |hg| usage, you can configure this in your ``home`` directory and it will
apply to all |repos|. Use the following example configuration,
and put your own information into the relevant sections.

For more detailed information, and a full rundown of all configuration options,
see the `Mercurial .hgrc config`_ documentation.

.. code-block:: ini

    [ui]
    username = username <user@mail.com>
    password = password-here

    [defaults]
    commit = -v

    [auth]
    rcdev.prefix = code.server.com
    rcdev.username = username
    rcdev.password = set-pw

    [merge-tools]
    meld3.executable = /usr/local/bin/meld

    [diff]
    git = 1
    showfunc = 1
    unified = 8

    [alias]
    cherry-pick = graft
    pull = pull --rebase
    push-all = push
    push = push --rev .
    amend = commit --amend
    record-interactive=crecord

    [extensions]
    progress =
    mq =
    purge =
    bookmarks =
    hgext.churn =
    largefiles =
    rebase =
    crecord = /Users/brian/crecord/crecord

    [largefiles]
    patterns = re:.*\.(png|bmp|jpg|zip|tar|tar.gz|rar)$
    minsize = 10

    [progress]
    delay = 1.5

    [bookmarks]
    track.current = True

    [color]
    status.modified = green
    status.removed = red bold
    status.added = cyan bold
    status.unknown = white bold
    custom.rev = yellow
    custom.author = bold
    custom.book = green
    custom.branch = red bold underline
    custom.date = underline
    changeset.draft = yellow
    changeset.public = green

    [pager]
    pager = LESS='FSRX' less


.. _config-hgignore:

Configure the ``.hgignore`` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :file:`{~path}/{to}/{repo}/.hgignore` file is a configuration file that
instructs |hg| to ignore certain files and not commit them to the |repo|. Files
such as build files, or editor tracking files are usually not committed to a
|repo|.

Create the ``.hgignore`` file in your |repo|, and configure it using the
following example to ignore the files you do not wish to be added to version
control. For more information, see the `hgignore documentation`_

.. code-block:: vim

    syntax: glob
    result
    www
    *_build/*
    *result/*
    *.pyc
    *.pyo
    *.idea
    .DS_Store

.. _basic-hg-cmds:

Using basic |hg| commands
^^^^^^^^^^^^^^^^^^^^^^^^^

The following commands will get you through the basics of using |hg| on the
command line. For a full run through of all |hg| commands and options,
see the `Mercurial Command Line Reference Guide`_

* ``hg init`` - Create a |hg| |repo|.
* ``hg clone URI`` - Clone a |repo| to your local machine.
* ``hg status`` - Display the status of a |repo|.
* ``hg commit -m “xx”`` - Commit changes with an 'xx' commit message.
* ``hg pull`` - Pull changes on server into the local |repo|.
* ``hg push`` - Push your local changes to the server.
* ``hg outgoing`` - Display commits in your next push.
* ``hg incoming`` - Display commits being pulled locally on the next pull.
* ``hg heads`` - Display |repo| versions, when multiple heads get created you
  need to merge them.
* ``hg update -r REV`` - Revert to specified revision.
* ``hg update -C`` - Disregards any uncommited changes.
* ``hg merge -r tip`` - Merge changes with tip.
* ``hg log`` - Show the |repo| history.
* ``hg rollback`` - Rollback certain revisions.
* ``hg diff`` - Show file diffs on your terminal.


.. _Mercurial .hgrc config: http://www.selenic.com/mercurial/hgrc.5.html
.. _hgignore documentation: http://www.selenic.com/mercurial/hgignore.5.html
.. _Mercurial Command Line Reference Guide: http://www.selenic.com/mercurial/hg.1.html
.. _Git Command Line Reference Guide: http://git-scm.com/doc
.. _gitconfig documentation: http://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration
.. _gitignore documentation: http://git-scm.com/docs/gitignore