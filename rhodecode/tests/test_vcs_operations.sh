#!/bin/sh
set -e

SQLITE_DB_PATH=/mnt/hgfs/marcink-shared/workspace-python/rhodecode
RC_LOG=/tmp/rc.log
INI_FILE=test.ini
TEST_DB_NAME=rhodecode_test


for databaseName in p m s; do
    # set the different DBs
    if [ "$databaseName" = "s" ]; then
      echo "sqlite"
      rhodecode-config  --filename=$INI_FILE --update '[app:main]sqlalchemy.db1.url=sqlite:///'$SQLITE_DB_PATH/$TEST_DB_NAME'.sqlite'
    elif [ "$databaseName" = "p" ]; then
      echo "postgres"
      rhodecode-config  --filename=$INI_FILE --update '[app:main]sqlalchemy.db1.url=postgresql://postgres:qweqwe@localhost/'$TEST_DB_NAME''
    elif [ "$databaseName" = "m" ]; then
      echo "mysql"
      rhodecode-config  --filename=$INI_FILE --update '[app:main]sqlalchemy.db1.url=mysql://root:qweqwe@localhost/'$TEST_DB_NAME''
    fi

    # running just VCS tests
    RC_NO_TMP_PATH=1 py.test \
        rhodecode/tests/other/test_vcs_operations.py

done
