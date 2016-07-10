# -*- coding: utf-8 -*-

import logging
import sqlalchemy as sa

from alembic.migration import MigrationContext
from alembic.operations import Operations

from rhodecode.lib.dbmigrate.versions import _reset_base

log = logging.getLogger(__name__)


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_4_3_0_0

    integrations_table = db_4_3_0_0.Integration.__table__
    integrations_table.create()


def downgrade(migrate_engine):
    pass
