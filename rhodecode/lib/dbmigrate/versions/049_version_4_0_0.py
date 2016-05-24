# -*- coding: utf-8 -*-

import logging
import sqlalchemy as sa

from alembic.migration import MigrationContext
from alembic.operations import Operations

from rhodecode.lib.dbmigrate.versions import _reset_base

from rhodecode.model import init_model_encryption

log = logging.getLogger(__name__)


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_3_7_0_0

    init_model_encryption(db_3_7_0_0)

    context = MigrationContext.configure(migrate_engine.connect())
    op = Operations(context)

    op.create_table(
        'external_identities',
        sa.Column('provider_name', sa.Unicode(255), primary_key=True),
        sa.Column('local_user_id', sa.Integer(),
                  sa.ForeignKey('users.user_id'), primary_key=True),

        sa.Column('external_id', sa.Unicode(255), primary_key=True),
        sa.Column('external_username', sa.Unicode(1024), default=u''),

        sa.Column('access_token', sa.String(1024), default=u''),
        sa.Column('alt_token', sa.String(1024), default=u''),
        sa.Column('token_secret', sa.String(1024), default=u'')
    )
    op.create_index('local_user_id_idx', 'external_identities',
                    ['local_user_id'])
    op.create_index('external_id_idx', 'external_identities',
                    ['external_id'])


def downgrade(migrate_engine):
    pass
