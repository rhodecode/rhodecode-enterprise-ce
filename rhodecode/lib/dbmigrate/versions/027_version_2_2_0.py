import logging
import datetime

from sqlalchemy import *
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import relation, backref, class_mapper, joinedload
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base

from rhodecode.lib.dbmigrate.migrate import *
from rhodecode.lib.dbmigrate.migrate.changeset import *
from rhodecode.lib.utils2 import str2bool

from rhodecode.model.meta import Base
from rhodecode.model import meta
from rhodecode.lib.dbmigrate.versions import _reset_base, notify

log = logging.getLogger(__name__)


def get_by_key(cls, key):
    return cls.query().filter(cls.permission_name == key).scalar()


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_2_2_0

    # issue fixups
    fixups(db_2_2_0, meta.Session)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine


def fixups(models, _SESSION):
    # ** create default permissions ** #
    #=====================================
    for p in models.Permission.PERMS:
        if not get_by_key(models.Permission, p[0]):
            new_perm = models.Permission()
            new_perm.permission_name = p[0]
            new_perm.permission_longname = p[0]  #translation err with p[1]
            print 'Creating new permission %s' % p[0]
            _SESSION().add(new_perm)

    _SESSION().commit()

    # ** set default create_on_write to active
    user = models.User.query().filter(
        models.User.username == 'default').scalar()

    _def = 'hg.create.write_on_repogroup.true'
    new = models.UserToPerm()
    new.user = user
    new.permission = get_by_key(models.Permission, _def)
    print 'Setting default to %s' % _def
    _SESSION().add(new)
    _SESSION().commit()
