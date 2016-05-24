.. _merging-empty-repo-ref:

Merging Forks with an Empty Repository
======================================

When a new repository is created, it has no commits. If the empty repository is
forked, neither |repo| will have any shared information to link them together,
making it impossible to create a |pr| to merge them.

To avoid this problem, create an initial commit on the new repository before
forking it. It can be accomplished, for example, by adding a README file to the
master repository and commiting it to the server before forking.

In case the fork was already made and you are unable to push or merge due to the
lack of a common commit between both repositories, the following steps would
enable you to fix this problem.

1. Create a commit on the master repository.
2. Pull the changes from the fork to the master repository, and rebase them
   on top of the new commit.

    .. code-block:: bash

       #pull from the fork into master
       $ hg pull -r fork-commit-id

3. If the changes were made locally, push the changes to the server.
4. On the forked repository, pull the changes from master.

Now you should be able to create a |pr| or merge between both repositories.

