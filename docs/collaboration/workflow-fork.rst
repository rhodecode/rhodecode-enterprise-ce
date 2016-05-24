.. _fork-flow:

Forking Workflow
================

The forking workflow means that everyone on a team has permission to fork a
|repo| and once they have completed their work, open a pull request to have it
accepted into the main |repo|.

In a forking workflow, not everyone will have write access to the main |repo|.
This means that only those with write access can merge |prs| once they have
been approved. Usually, the forking workflow is used with |hg|, and branching
with |git|.

Forking Overview
----------------

.. image:: ../images/fork-flow.png
   :align: center


Setting Up a Forking Workflow
-----------------------------

Setting up a forking workflow in |RCE| would look something like this.

1. Create a user group with write access.
2. Create a user group with read access.
3. Assign team members to the appropriate groups.
4. Users with contributions should open a pull request to
   the main |repo| and set a user with write access as the reviewer.
5. Once the |pr| is approved, the write access user would merge it with the
   main |repo|.

For more information about setting up user groups, see the :ref:`user-admin-set`
section.

Using a Forking Workflow
------------------------

If you are on a team that uses a forking workflow, see the
:ref:`forks-branches-ref` section for how to fork a |repo|, and also the
:ref:`pull-requests-ref` section.
