
.. _test-unit-and-functional:

===========================
 Unit and Functional Tests
===========================



py.test based test suite
========================


The test suite is in the folder :file:`rhodecode/tests/` and should be run with
the test runner `py.test` inside of your `nix-shell` environment::

   # In case you need the cythonized version
   CYTHONIZE=1 python setup.py develop --prefix=$tmp_path

   py.test rhodecode



py.test integration
-------------------

The integration with the test runner is based on the following three parts:

- `pytest_pylons` is a py.test plugin which does the integration with the
  Pylons web framework. It sets up the Pylons environment based on the given ini
  file.

  Tests which depend on the Pylons environment to be set up must request the
  fixture `pylonsapp`.

- :file:`rhodecode/tests/plugin.py` contains the integration of py.test with
  RhodeCode Enterprise itself.

- :file:`conftest.py` plugins are used to provide a special integration for
  certain groups of tests based on the directory location.



VCS backend selection
---------------------

The py.test integration provides a parameter `--backends`. It will skip all
tests which are marked for other backends.

To run only Subversion tests::

   py.test rhodecode --backends=svn



Frontend / Styling support
==========================

All relevant style components have an example inside of the "Style" section
within the application. Enable the setting `debug_style` to make this section
visible in your local instance of the application.
