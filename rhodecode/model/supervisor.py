# -*- coding: utf-8 -*-

# Copyright (C) 2014-2016  RhodeCode GmbH
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


"""
Model for supervisor process manager
"""

import xmlrpclib
import logging
import traceback

import rhodecode
from rhodecode.model import BaseModel

log = logging.getLogger(__name__)


SUPERVISOR_MASTER = 'MASTER'  # special name for supervisor master process


class SupervisorModel(BaseModel):

    cls = None

    def __init__(self, sa=None):
        super(SupervisorModel, self).__init__(sa=sa)

    def _verify_connection(self, connection):
        if not isinstance(connection, xmlrpclib.ServerProxy):
            raise Exception('Invalid connection given, got %s, expected %s'
                            % (type(connection), xmlrpclib.ServerProxy))

    def get_connection(self, supervisor_uri):
        uri = supervisor_uri or 'http://'
        try:
            server_connection = xmlrpclib.ServerProxy(uri)
            return server_connection
        except Exception as e:
            log.error(traceback.format_exc())
            raise

    def get_master_log(self, connection, offset, length):
        self._verify_connection(connection)
        return connection.supervisor.readLog(offset, length)

    def get_master_state(self, connection):
        self._verify_connection(connection)
        _data = connection.supervisor.getState()
        _data.update({'pid': connection.supervisor.getPID()})
        _data.update({'id': connection.supervisor.getIdentification()})
        _data.update({'ver': connection.supervisor.getSupervisorVersion()})
        return _data

    def get_group_processes(self, connection, groupid):
        self._verify_connection(connection)
        res = []
        for data in connection.supervisor.getAllProcessInfo():
            if data['group'] == groupid:
               res.append(data)
        return res

    def get_process_info(self, connection, procid):
        self._verify_connection(connection)

        return connection.supervisor.getProcessInfo(procid)

    def read_process_log(self, connection, procid, offset, length):
        self._verify_connection(connection)
        if procid == SUPERVISOR_MASTER:
            log = self.get_master_log(connection, offset, length)
        else:
            log = connection.supervisor.readProcessLog(procid, offset, length)
        # make sure we just return whole lines not to confuse people
        return ''.join(log.splitlines(1)[1:])
