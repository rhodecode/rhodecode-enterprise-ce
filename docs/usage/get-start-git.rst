
|git| Getting Started
---------------------


To work locally with |git| |repos|, use the following configuration examples
and command line instructions.

* :ref:`config-git-config`
* :ref:`config-gitignore`
* :ref:`use-basic-git`

.. _config-git-config:

Configure the ``.gitconfig`` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :file:`~/.gitconfig` file is a configuration file which controls how
|git| interacts between the server and your local setup.

For |git|, you can set this up in your ``home`` directory and it will be
applied to all |repos|. Use the following example configuration to set up
your file, and put your own information into the relevant sections.

For more detailed information, and a full rundown of all configuration options,
see the `gitconfig documentation`_.

.. code-block:: ini

    [user]
    name = username
    email = user@mail.com

    [core]
    editor = vim
    whitespace = fix,-indent-with-non-tab,trailing-space,cr-at-eol
    excludesfile = ~/.gitignore

    [rerere]
    enabled = 1
    autoupdate = 1

    [push]
    default = matching

    [color]
    ui = auto

    [color "branch"]
    current = yellow bold
    local = green bold
    remote = cyan bold

    [color "diff"]
    meta = yellow bold
    frag = magenta bold
    old = red bold
    new = green bold
    whitespace = red reverse

    [color "status"]
    added = green bold
    changed = yellow bold
    untracked = red bold

    [diff]
    tool = vimdiff

    [difftool]
    prompt = false

    [alias]
    a = add --all
    ai = add -i
    ap = apply
    as = apply --stat
    ac = apply --check

.. _config-gitignore:

Configure the ``.gitignore`` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :file:`{~path}/{to}/{repo}/.gitignore` file is a configuration file that
tells |git| to ignore certain files and not commit them to the |repo|. Files
such as build files, or editor tracking files are usually not committed to a
|repo|.

Create the ``.gitignore`` file in your |repo| and configure it using the
following example to ignore the files you do not wish to be added to version
control. For more information, see the `gitignore documentation`_

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

.. _use-basic-git:

Using basic |git| commands
^^^^^^^^^^^^^^^^^^^^^^^^^^

The following commands will get you through the basics of using |git| on the
command line. For a full run through of all |git| commands and options,
see the `Git Command Line Reference Guide`_

* ``git init`` - create a new git repository.
* ``git clone URI`` - Clone a |repo| to your local machine.
* ``git add <filename>`` - Add a file to staging.
* ``git commit -m "Commit message"`` - Commit files in staging to the |repo|
* ``git push origin master`` - Push changes to the ``master`` branch.
* ``git checkout -b feature_name`` - Create a new branch named *feature_name*
  and switch to it using.
* ``git checkout master`` - Switch back to the master branch.
* ``git branch -d feature_name`` - Delete the branced named *feature_name*.
* ``git pull`` - Pull changes on the server into the local |repo|.
* ``git merge <branch>`` - Merge another branch into your active branch.


.. _Mercurial .hgrc config: http://www.selenic.com/mercurial/hgrc.5.html
.. _hgignore documentation: http://www.selenic.com/mercurial/hgignore.5.html
.. _Mercurial Command Line Reference Guide: http://www.selenic.com/mercurial/hg.1.html
.. _Git Command Line Reference Guide: http://git-scm.com/doc
.. _gitconfig documentation: http://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration
.. _gitignore documentation: http://git-scm.com/docs/gitignore