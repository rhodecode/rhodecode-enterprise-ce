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

from subprocess import Popen, PIPE
import os
import shutil
import sys
import tempfile

import pytest
from sqlalchemy.engine import url

from rhodecode.tests.fixture import TestINI


def _get_dbs_from_metafunc(metafunc):
    if hasattr(metafunc.function, 'dbs'):
        # Supported backends by this test function, created from
        # pytest.mark.dbs
        backends = metafunc.function.dbs.args
    else:
        backends = metafunc.config.getoption('--dbs')
    return backends


def pytest_generate_tests(metafunc):
    # Support test generation based on --dbs parameter
    if 'db_backend' in metafunc.fixturenames:
        requested_backends = set(metafunc.config.getoption('--dbs'))
        backends = _get_dbs_from_metafunc(metafunc)
        backends = requested_backends.intersection(backends)
        # TODO: johbo: Disabling a backend did not work out with
        # parametrization, find better way to achieve this.
        if not backends:
            metafunc.function._skip = True
        metafunc.parametrize('db_backend_name', backends)


def pytest_collection_modifyitems(session, config, items):
    remaining = [
        i for i in items if not getattr(i.obj, '_skip', False)]
    items[:] = remaining


@pytest.fixture
def db_backend(
        request, db_backend_name, pylons_config, tmpdir_factory):
    basetemp = tmpdir_factory.getbasetemp().strpath
    klass = _get_backend(db_backend_name)

    option_name = '--{}-connection-string'.format(db_backend_name)
    connection_string = request.config.getoption(option_name) or None

    return klass(
        config_file=pylons_config, basetemp=basetemp,
        connection_string=connection_string)


def _get_backend(backend_type):
    return {
        'sqlite': SQLiteDBBackend,
        'postgres': PostgresDBBackend,
        'mysql': MySQLDBBackend,
        '': EmptyDBBackend
    }[backend_type]


class DBBackend(object):
    _store = os.path.dirname(os.path.abspath(__file__))
    _type = None
    _base_ini_config = [{'app:main': {'vcs.start_server': 'false'}}]
    _db_url = [{'app:main': {'sqlalchemy.db1.url': ''}}]
    _base_db_name = 'rhodecode_test_db_backend'

    def __init__(
            self, config_file, db_name=None, basetemp=None,
            connection_string=None):
        self.fixture_store = os.path.join(self._store, self._type)
        self.db_name = db_name or self._base_db_name
        self._base_ini_file = config_file
        self.stderr = ''
        self.stdout = ''
        self._basetemp = basetemp or tempfile.gettempdir()
        self._repos_location = os.path.join(self._basetemp, 'rc_test_repos')
        self.connection_string = connection_string

    @property
    def connection_string(self):
        return self._connection_string

    @connection_string.setter
    def connection_string(self, new_connection_string):
        if not new_connection_string:
            new_connection_string = self.get_default_connection_string()
        else:
            new_connection_string = new_connection_string.format(
                db_name=self.db_name)
        url_parts = url.make_url(new_connection_string)
        self._connection_string = new_connection_string
        self.user = url_parts.username
        self.password = url_parts.password
        self.host = url_parts.host

    def get_default_connection_string(self):
        raise NotImplementedError('default connection_string is required.')

    def execute(self, cmd, env=None, *args):
        """
        Runs command on the system with given ``args``.
        """

        command = cmd + ' ' + ' '.join(args)
        sys.stdout.write(command)

        # Tell Python to use UTF-8 encoding out stdout
        _env = os.environ.copy()
        _env['PYTHONIOENCODING'] = 'UTF-8'
        if env:
            _env.update(env)
        self.p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, env=_env)
        self.stdout, self.stderr = self.p.communicate()
        sys.stdout.write('COMMAND:'+command+'\n')
        sys.stdout.write(self.stdout)
        return self.stdout, self.stderr

    def assert_returncode_success(self):
        assert self.p.returncode == 0, self.stderr

    def setup_rhodecode_db(self, ini_params=None, env=None):
        if not ini_params:
            ini_params = self._base_ini_config

        ini_params.extend(self._db_url)
        with TestINI(self._base_ini_file, ini_params,
                     self._type, destroy=True) as _ini_file:
            if not os.path.isdir(self._repos_location):
                os.makedirs(self._repos_location)
            self.execute(
                "paster setup-rhodecode {0} --user=marcink "
                "--email=marcin@rhodeocode.com --password={1} "
                "--repos={2} --force-yes".format(
                    _ini_file, 'qweqwe', self._repos_location), env=env)

    def upgrade_database(self, ini_params=None):
        if not ini_params:
            ini_params = self._base_ini_config
        ini_params.extend(self._db_url)

        test_ini = TestINI(
            self._base_ini_file, ini_params, self._type, destroy=True)
        with test_ini as ini_file:
            if not os.path.isdir(self._repos_location):
                os.makedirs(self._repos_location)
            self.execute(
                "paster upgrade-db {} --force-yes".format(ini_file))

    def setup_db(self):
        raise NotImplementedError

    def teardown_db(self):
        raise NotImplementedError

    def import_dump(self, dumpname):
        raise NotImplementedError


class EmptyDBBackend(DBBackend):
    _type = ''

    def setup_db(self):
        pass

    def teardown_db(self):
        pass

    def import_dump(self, dumpname):
        pass

    def assert_returncode_success(self):
        assert True


class SQLiteDBBackend(DBBackend):
    _type = 'sqlite'

    def get_default_connection_string(self):
        return 'sqlite:///{}/{}.sqlite'.format(self._basetemp, self.db_name)

    def setup_db(self):
        # dump schema for tests
        # cp -v $TEST_DB_NAME
        self._db_url = [{'app:main': {
            'sqlalchemy.db1.url': self.connection_string}}]

    def import_dump(self, dumpname):
        dump = os.path.join(self.fixture_store, dumpname)
        shutil.copy(
            dump,
            os.path.join(self._basetemp, '{0.db_name}.sqlite'.format(self)))

    def teardown_db(self):
        self.execute("rm -rf {}.sqlite".format(
            os.path.join(self._basetemp, self.db_name)))


class MySQLDBBackend(DBBackend):
    _type = 'mysql'

    def get_default_connection_string(self):
        return 'mysql://root:qweqwe@127.0.0.1/{}'.format(self.db_name)

    def setup_db(self):
        # dump schema for tests
        # mysqldump -uroot -pqweqwe $TEST_DB_NAME
        self._db_url = [{'app:main': {
            'sqlalchemy.db1.url': self.connection_string}}]
        self.execute("mysql -v -u{} -p{} -e 'create database '{}';'".format(
            self.user, self.password, self.db_name))

    def import_dump(self, dumpname):
        dump = os.path.join(self.fixture_store, dumpname)
        self.execute("mysql -u{} -p{} {} < {}".format(
            self.user, self.password, self.db_name, dump))

    def teardown_db(self):
        self.execute("mysql -v -u{} -p{} -e 'drop database '{}';'".format(
            self.user, self.password, self.db_name))


class PostgresDBBackend(DBBackend):
    _type = 'postgres'

    def get_default_connection_string(self):
        return 'postgresql://postgres:qweqwe@localhost/{}'.format(self.db_name)

    def setup_db(self):
        # dump schema for tests
        # pg_dump -U postgres -h localhost $TEST_DB_NAME
        self._db_url = [{'app:main': {
            'sqlalchemy.db1.url':
                self.connection_string}}]
        self.execute("PGPASSWORD={} psql -U {} -h localhost "
                     "-c 'create database '{}';'".format(
                         self.password, self.user, self.db_name))

    def teardown_db(self):
        self.execute("PGPASSWORD={} psql -U {} -h localhost "
                     "-c 'drop database if exists '{}';'".format(
                         self.password, self.user, self.db_name))

    def import_dump(self, dumpname):
        dump = os.path.join(self.fixture_store, dumpname)
        self.execute(
            "PGPASSWORD={} psql -U {} -h localhost -d {} -1 "
            "-f {}".format(
                self.password, self.user, self.db_name, dump))
