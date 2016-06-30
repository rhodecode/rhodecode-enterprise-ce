
.. _test-spec-by-example:

==========================
 Specification by Example
==========================


.. Avoid duplicating the quickstart instructions by importing the README
   file.

.. include:: ../../../acceptance_tests/README.rst



Choices of technology and tools
===============================


`nix` as runtime environment
----------------------------

We settled to use the `nix` tools to provide us the needed environment for
running the tests.



`Gherkins` as specification language
------------------------------------

To specify by example, we settled on Gherkins as the semi-formal specification
language.


`py.test` as a runner
---------------------

After experimenting with `behave` and `py.test` our choice was `pytest-bdd`
because it allows us to use our existing knowledge about `py.test` and avoids
that we have to learn another tool.



Concepts
========

The logic is structured around the design pattern of "page objects". The
documentation of `python-selemium` contains a few more details about this
pattern.



Page Objects
------------

We introduce an abstraction class for every page which we have to interact with
in order to validate the specifications.

The implementation for the page objects is inside of the module
:mod:`page_objects`. The class :class:`page_objects.base.BasePage` should be
used as a base for all page object implementations.



Locators
--------

The specific information how to locate an element inside of the DOM tree of a
page is kept in a separate class. This class serves mainly as a data container;
it shall not contain any logic.

The reason for keeping the locators separate is that we expect a frequent need
for change whenever we work on our templates. In such a case, it is more
efficient to have all of thelocators together and update them there instead of
having to find every locator inside of the logic of a page object.
