import logging
import datetime

from sqlalchemy import *
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import relation, backref, class_mapper, joinedload
from sqlalchemy.orm.session import Session
from sqlalchemy.ext.declarative import declarative_base

from rhodecode.lib.dbmigrate.migrate import *
from rhodecode.lib.dbmigrate.migrate.changeset import *

from rhodecode.model.meta import Base
from rhodecode.model import meta
from rhodecode.lib.dbmigrate.versions import _reset_base

log = logging.getLogger(__name__)


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_1_5_0
    #==========================================================================
    # USER LOGS
    #==========================================================================

    tbl = db_1_5_0.UserLog.__table__
    username = Column("username", String(255, convert_unicode=False),
                      nullable=True, unique=None, default=None)
    # create username column
    username.create(table=tbl)

    _Session = meta.Session()
    ## after adding that column fix all usernames
    users_log = _Session.query(db_1_5_0.UserLog)\
            .options(joinedload(db_1_5_0.UserLog.user))\
            .options(joinedload(db_1_5_0.UserLog.repository)).all()

    for entry in users_log:
        entry.username = entry.user.username
        _Session.add(entry)
    _Session.commit()

    #alter username to not null
    tbl_name = db_1_5_0.UserLog.__tablename__
    tbl = Table(tbl_name,
                MetaData(bind=migrate_engine), autoload=True,
                autoload_with=migrate_engine)
    col = tbl.columns.username

    # remove nullability from revision field
    col.alter(nullable=False)

    # issue fixups
    fixups(db_1_5_0, meta.Session)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine


def get_by_key(cls, key):
    return cls.query().filter(cls.permission_name == key).scalar()


def get_by_name(cls, key):
    return cls.query().filter(cls.app_settings_name == key).scalar()


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

    # ** populate default permissions ** #
    #=====================================

    user = models.User.query().filter(models.User.username == 'default').scalar()

    def _make_perm(perm):
        new_perm = models.UserToPerm()
        new_perm.user = user
        new_perm.permission = get_by_key(models.Permission, perm)
        return new_perm

    def _get_group(perm_name):
        return '.'.join(perm_name.split('.')[:1])

    perms = models.UserToPerm.query().filter(models.UserToPerm.user == user).all()
    defined_perms_groups = map(
        _get_group, (x.permission.permission_name for x in perms))
    log.debug('GOT ALREADY DEFINED:%s' % perms)
    DEFAULT_PERMS = models.Permission.DEFAULT_USER_PERMISSIONS

    # for every default permission that needs to be created, we check if
    # it's group is already defined, if it's not we create default perm
    for perm_name in DEFAULT_PERMS:
        gr = _get_group(perm_name)
        if gr not in defined_perms_groups:
            log.debug('GR:%s not found, creating permission %s'
                      % (gr, perm_name))
            new_perm = _make_perm(perm_name)
            _SESSION().add(new_perm)
    _SESSION().commit()

    # ** create default options ** #
    #===============================
    skip_existing = True
    for k, v in [
        ('default_repo_enable_locking',  False),
        ('default_repo_enable_downloads', False),
        ('default_repo_enable_statistics', False),
        ('default_repo_private', False),
        ('default_repo_type', 'hg')]:

        if skip_existing and get_by_name(models.RhodeCodeSetting, k) is not None:
            log.debug('Skipping option %s' % k)
            continue
        setting = models.RhodeCodeSetting(k, v)
        _SESSION().add(setting)

    _SESSION().commit()
