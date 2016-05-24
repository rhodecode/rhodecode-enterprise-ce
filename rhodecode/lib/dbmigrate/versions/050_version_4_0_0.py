# -*- coding: utf-8 -*-

import logging

from sqlalchemy.orm.attributes import flag_modified

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


def fixups(models, Session):
    for repo in models.Repository.get_all():
        if repo.clone_uri:
            print 'Encrypting clone uri in repo %s' % repo
            flag_modified(repo, 'clone_uri')
            Session().add(repo)

    Session().commit()


