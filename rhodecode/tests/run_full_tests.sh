#!/bin/sh
set -e

## MIGRATIONS AND DB TESTS ##
echo "DATABASE CREATION TESTS"
rhodecode/tests/database/test_creation.sh

echo "DATABASE MIGRATIONS TESTS"
rhodecode/tests/database/test_migration.sh

## TEST VCS OPERATIONS ##
echo "VCS FUNCTIONAL TESTS"
rhodecode/tests/test_vcs_operations.sh

## TOX TESTS ##
echo "TOX TESTS"
tox -r --develop
