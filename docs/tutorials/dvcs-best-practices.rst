.. _vcs-bps:

Collaboration Best Practices
============================

This section outlines some of the best practices when working with
Distributed Version Control Systems (DVCS). These best practices will help
you get the most out |git| and |hg| when working with others.

Test Locally
------------

As most test suites are also included in the |repo|, it is good practice to
ensure your changes are passing locally before opening a pull request and
having the CI server run the tests for you. The two main benefits here are:

* Not clogging up the test machine with untested and thus more likely to fail
  test runs.
* Only opening |prs| that are passing locally increases the quality of
  feedback at the peer review stage as reviewers can focus on high
  quality feedback.

Agree on Workflow
-----------------

When working with others, one of the first things to agree upon is a workflow.
This agreement means that everyone knows what is happening at a particular
stage of the collaboration cycle and that they can deliver in accordance with
the expectations.

Keep Commits To One Task
------------------------

When committing it is good practice to keep each commit to a specific task.
This allows the |repo| admin to easily cherry pick or graft work between
branches should there be a need to do so for particular release processes. It
also makes it easy for colleagues to understand the changes going into a
|repo|.

Use Descriptive Commit Messages
-------------------------------

When writing commit messages, it is good practice to contextualise the
message by prepending a label which will give the reader a clue about what
area the changes apply to, and to then write a brief but descriptive message
that explains in more detail.

.. code-block:: bash

    o  10739:0fdd6cd2b97a [default] - public
    |  2 days ago by Johannes Bornhold | B:,T:
    |  ac-tests: Change browser.click to be only locator based

Master Your Tools
-----------------

The best way to get good at something it to break it and fix it. One
advantage of DVCS is how cheap forking and branching is. One tip is to create
your own fork and master branching, rebasing, cherry picking, merging, or any
other skill you currently find challenging. Once you have mastered it on the
disposable branch or fork you can carry out tasks on your main |repos| with
confidence.
