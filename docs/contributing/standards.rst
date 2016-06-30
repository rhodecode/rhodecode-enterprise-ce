
======================
Contribution Standards
======================

Standards help to improve the quality of our product and its development. Herein
we define our standards for processes and development to maintain consistency
and function well as a community. It is a work in progress; modifications to this
document should be discussed and agreed upon by the community.


--------------------------------------------------------------------------------

Code
====

This provides an outline for standards we use in our codebase to keep our code
easy to read and easy to maintain. Much of our code guidelines are based on the
book `Clean Code <http://www.pearsonhighered.com/educator/product/Clean-Code-A-Handbook-of-Agile-Software-Craftsmanship/9780132350884.page>`_
by Robert Martin.

We maintain a Tech Glossary to provide consistency in terms and symbolic names
used for items and concepts within the application. This is found in the CE
project in /docs-internal/glossary.rst


Refactoring
-----------
Make it better than you found it!

Our codebase can always use improvement and often benefits from refactoring.
New code should be refactored as it is being written, and old code should be
treated with the same care as if it was new. Before doing any refactoring,
ensure that there is test coverage on the affected code; this will help
minimize issues.


Python
------
For Python, we use `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_.
We adjust lines of code to under 80 characters and use 4 spaces for indentation.


JavaScript
----------
This currently remains undefined. Suggestions welcome!


HTML
----
Unfortunately, we currently have no strict HTML standards, but there are a few
guidelines we do follow. Templates must work in all modern browsers. HTML should
be clean and easy to read, and additionally should be free of inline CSS or
JavaScript. It is recommended to use data attributes for JS actions where
possible in order to separate it from styling and prevent unintentional changes.


LESS/CSS
--------
We use LESS for our CSS; see :doc:`frontend` for structure and formatting
guidelines.


Linters
-------
Currently, we have a linter for pull requests which checks code against PEP8.
We intend to add more in the future as we clarify standards.


--------------------------------------------------------------------------------

Naming Conventions
==================

These still need to be defined for naming everything from Python variables to
HTML classes to files and folders.


--------------------------------------------------------------------------------

Testing
=======

Testing is a very important aspect of our process, especially as we are our own
quality control team. While it is of course unrealistic to hit every potential
combination, our goal is to cover every line of Python code with a test. 

The following is a brief introduction to our test suite. Our tests are primarily
written using `py.test <http://pytest.org/>`_


Acceptance Tests
----------------
Also known as "ac tests", these test from the user and business perspective to
check if the requirements of a feature are met. Scenarios are created at a
feature's inception and help to define its value.

py.test is used for ac tests; they are located in a folder separate from the
other tests which follow. Each feature has a .feature file which contains a
brief description and the scenarios to be tested.


Functional Tests
----------------
These test specific functionality in the application which checks through the
entire stack. Typically these are user actions or permissions which go through
the web browser. They are located in rhodecode/tests.


Unit Tests
----------
These test isolated, individual modules to ensure that they function correctly.
They are located in rhodecode/tests.


Integration Tests
-----------------
These are used for testing performance of larger systems than the unit tests.
They are located in rhodecode/tests.


JavaScript Testing
------------------
Currently, we have not defined how to test our JavaScript code.


--------------------------------------------------------------------------------

Pull Requests
=============

Pull requests should generally contain only one thing: a single feature, one bug
fix, etc.. The commit history should be concise and clean, and the pull request
should contain the ticket number (also a good idea for the commits themselves)
to provide context for the reviewer.

See also: :doc:`checklist-pull-request`


Reviewers
---------
Each pull request must be approved by at least one member of the RhodeCode
team. Assignments may be based on expertise or familiarity with a particular
area of code, or simply availability. Switching up or adding extra community
members for different pull requests helps to share knowledge as well as provide
other perspectives.


Responsibility
--------------
The community is responsible for maintaining features and this must be taken
into consideration. External contributions must be held to the same standards
as internal contributions.


Feature Switch
--------------
Experimental and work-in-progress features can be hidden behind one of two
switches:

* A setting can be added to the Labs page in the Admin section which may allow
  customers to access and toggle additional features.
* For work-in-progress or other features where customer access is not desired,
  use a custom setting in the .ini file as a trigger.


--------------------------------------------------------------------------------

Tickets
=======

Redmine tickets are a crucial part of our development process. Any code added or
changed in our codebase should have a corresponding ticket to document it. With
this in mind, it is important that tickets be as clear and concise as possible,
including what the expected outcome is.

See also: :doc:`checklist-tickets`
