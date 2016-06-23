README - Quickstart
===================

This folder contains the functional tests and automation of specification
examples. Details about testing can be found in
`/docs-internal/testing/index.rst`.


Setting up your Rhodecode Enterprise instance
---------------------------------------------

The tests will create users and repositories as needed, so you can start with a
new and empty instance.

Use the following example call for the database setup of Enterprise::

   paster setup-rhodecode \
     --user=admin \
     --email=admin@example.com \
     --password=secret \
     --api-key=9999999999999999999999999999999999999999 \
     your-enterprise-config.ini

This way the username, password, and auth token of the admin user will match the
defaults from the test run.


Usage
-----

1. Make sure your Rhodecode Enterprise instance is running at
   http://localhost:5000.

2. Enter `nix-shell` from the acceptance_tests folder::

     cd acceptance_tests
     nix-shell

   Make sure that `rcpkgs` and `rcnixpkgs` are available on the nix path.

3. Run the tests::

     py.test -c example.ini -vs

   The parameter ``-vs`` allows you to see debugging output during the test
   run. Check ``py.test --help`` and the documentation at http://pytest.org to
   learn all details about the test runner.
