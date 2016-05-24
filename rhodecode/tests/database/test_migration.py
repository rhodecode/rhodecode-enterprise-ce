# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, version 3
# (only), as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is dual-licensed. If you wish to learn more about the
# RhodeCode Enterprise Edition, including its added features, Support services,
# and proprietary license terms, please see https://rhodecode.com/licenses/

import pytest


@pytest.mark.dbs("postgres")
@pytest.mark.parametrize("dumpname", [
    '1.4.4.sql',
    '1.5.0.sql',
    '1.6.0.sql',
    '1.6.0_no_repo_name_index.sql',
])
def test_migrate_postgres_db(db_backend, dumpname):
    _run_migration_test(db_backend, dumpname)


@pytest.mark.dbs("sqlite")
@pytest.mark.parametrize("dumpname", [
    'rhodecode.1.4.4.sqlite',
    'rhodecode.1.4.4_with_groups.sqlite',
    'rhodecode.1.4.4_with_ldap_active.sqlite',
])
def test_migrate_sqlite_db(db_backend, dumpname):
    _run_migration_test(db_backend, dumpname)


@pytest.mark.dbs("mysql")
@pytest.mark.parametrize("dumpname", [
    '1.4.4.sql',
    '1.5.0.sql',
    '1.6.0.sql',
    '1.6.0_no_repo_name_index.sql',
])
def test_migrate_mysql_db(db_backend, dumpname):
    _run_migration_test(db_backend, dumpname)


def _run_migration_test(db_backend, dumpname):
    db_backend.teardown_db()
    db_backend.setup_db()
    db_backend.assert_returncode_success()

    db_backend.import_dump(dumpname)
    db_backend.upgrade_database()
    db_backend.assert_returncode_success()
