import logging

from sqlalchemy import MetaData

from rhodecode.model import meta
from rhodecode.lib.dbmigrate.versions import _reset_base


log = logging.getLogger(__name__)


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_3_5_0_0

    ui_table = db_3_5_0_0.RepoRhodeCodeUi.__table__
    settings_table = db_3_5_0_0.RepoRhodeCodeSetting.__table__
    ui_table.create()
    settings_table.create()


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine


