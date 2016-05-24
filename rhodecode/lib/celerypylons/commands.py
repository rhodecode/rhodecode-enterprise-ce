# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016  RhodeCode GmbH
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

import rhodecode
from rhodecode.lib.utils import BasePasterCommand, Command, load_rcextensions
from celery.app import app_or_default
from celery.bin import camqadm, celerybeat, celeryd, celeryev

from rhodecode.lib.utils2 import str2bool

__all__ = ['CeleryDaemonCommand', 'CeleryBeatCommand',
           'CAMQPAdminCommand', 'CeleryEventCommand']


class CeleryCommand(BasePasterCommand):
    """Abstract class implements run methods needed for celery

    Starts the celery worker that uses a paste.deploy configuration
    file.
    """

    def update_parser(self):
        """
        Abstract method.  Allows for the class's parser to be updated
        before the superclass's `run` method is called.  Necessary to
        allow options/arguments to be passed through to the underlying
        celery command.
        """

        cmd = self.celery_command(app_or_default())
        for x in cmd.get_options():
            self.parser.add_option(x)

    def command(self):
        from pylons import config
        try:
            CELERY_ENABLED = str2bool(config['app_conf'].get('use_celery'))
        except KeyError:
            CELERY_ENABLED = False

        if not CELERY_ENABLED:
            raise Exception('Please set use_celery = true in .ini config '
                            'file before running celeryd')
        rhodecode.CELERY_ENABLED = CELERY_ENABLED
        load_rcextensions(config['here'])
        cmd = self.celery_command(app_or_default())
        return cmd.run(**vars(self.options))


class CeleryDaemonCommand(CeleryCommand):
    """Start the celery worker

    Starts the celery worker that uses a paste.deploy configuration
    file.
    """
    usage = 'CONFIG_FILE [celeryd options...]'
    summary = __doc__.splitlines()[0]
    description = "".join(__doc__.splitlines()[2:])

    parser = Command.standard_parser(quiet=True)
    celery_command = celeryd.WorkerCommand


class CeleryBeatCommand(CeleryCommand):
    """Start the celery beat server

    Starts the celery beat server using a paste.deploy configuration
    file.
    """
    usage = 'CONFIG_FILE [celerybeat options...]'
    summary = __doc__.splitlines()[0]
    description = "".join(__doc__.splitlines()[2:])

    parser = Command.standard_parser(quiet=True)
    celery_command = celerybeat.BeatCommand


class CAMQPAdminCommand(CeleryCommand):
    """CAMQP Admin

    CAMQP celery admin tool.
    """
    usage = 'CONFIG_FILE [camqadm options...]'
    summary = __doc__.splitlines()[0]
    description = "".join(__doc__.splitlines()[2:])

    parser = Command.standard_parser(quiet=True)
    celery_command = camqadm.AMQPAdminCommand


class CeleryEventCommand(CeleryCommand):
    """Celery event command.

    Capture celery events.
    """
    usage = 'CONFIG_FILE [celeryev options...]'
    summary = __doc__.splitlines()[0]
    description = "".join(__doc__.splitlines()[2:])

    parser = Command.standard_parser(quiet=True)
    celery_command = celeryev.EvCommand
