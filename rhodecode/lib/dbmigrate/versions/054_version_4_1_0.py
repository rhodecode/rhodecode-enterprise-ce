# -*- coding: utf-8 -*-

import logging
from collections import namedtuple

from rhodecode.lib.dbmigrate.versions import _reset_base
from rhodecode.model import init_model_encryption, meta

log = logging.getLogger(__name__)


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_3_7_0_0
    init_model_encryption(db_3_7_0_0)
    fixups(db_3_7_0_0, meta.Session)


def downgrade(migrate_engine):
    pass


AUTH_PLUGINS_SETTING = "auth_plugins"

EXTERN_TYPE_RENAME_MAP = {
    'container': 'headers',
}

# Only used for logging purposes.
RenameExternTypeOperation = namedtuple(
    'RenameExternTypeOperation', ['user', 'old', 'new'])


def fixups(models, Session):
    operations = []

    # Rename the extern_type attribute
    query = models.User.query().filter(
        models.User.extern_type.in_(EXTERN_TYPE_RENAME_MAP.keys()))
    for user in query:
        old = user.extern_type
        new = EXTERN_TYPE_RENAME_MAP[old]
        user.extern_type = new
        Session.add(user)
        operations.append(RenameExternTypeOperation(user, old, new))

    log.info("Migration of users 'extern_type' attribute.")
    for op in operations:
        log.info("%s", op)

    Session().commit()
