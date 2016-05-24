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
    from rhodecode.lib.dbmigrate.schema import db_1_7_0

    #==========================================================================
    # UserUserGroupToPerm
    #==========================================================================
    tbl = db_1_7_0.UserUserGroupToPerm.__table__
    tbl.create()

    #==========================================================================
    # UserGroupUserGroupToPerm
    #==========================================================================
    tbl = db_1_7_0.UserGroupUserGroupToPerm.__table__
    tbl.create()

    #==========================================================================
    # Gist
    #==========================================================================
    tbl = db_1_7_0.Gist.__table__
    tbl.create()

    #==========================================================================
    # UserGroup
    #==========================================================================
    tbl = db_1_7_0.UserGroup.__table__
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'),
                     nullable=True, unique=False, default=None)
    # create username column
    user_id.create(table=tbl)

    #==========================================================================
    # RepoGroup
    #==========================================================================
    tbl = db_1_7_0.RepoGroup.__table__
    user_id = Column("user_id", Integer(), ForeignKey('users.user_id'),
                     nullable=True, unique=False, default=None)
    # create username column
    user_id.create(table=tbl)

    # issue fixups
    fixups(db_1_7_0, meta.Session)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine


def fixups(models, _SESSION):
    # ** create default permissions ** #
    #=====================================
    for p in models.Permission.PERMS:
        if not models.Permission.get_by_key(p[0]):
            new_perm = models.Permission()
            new_perm.permission_name = p[0]
            new_perm.permission_longname = p[0]  #translation err with p[1]
            _SESSION().add(new_perm)

    _SESSION().commit()

    # ** populate default permissions ** #
    #=====================================

    user = models.User.query().filter(models.User.username == 'default').scalar()

    def _make_perm(perm):
        new_perm = models.UserToPerm()
        new_perm.user = user
        new_perm.permission = models.Permission.get_by_key(perm)
        return new_perm

    def _get_group(perm_name):
        return '.'.join(perm_name.split('.')[:1])

    perms = models.UserToPerm.query().filter(models.UserToPerm.user == user).all()
    defined_perms_groups = map(_get_group,
                              (x.permission.permission_name for x in perms))
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

    #fix all usergroups

    def _create_default_perms(user_group):
        # create default permission
        default_perm = 'usergroup.read'
        def_user = models.User.get_default_user()
        for p in def_user.user_perms:
            if p.permission.permission_name.startswith('usergroup.'):
                default_perm = p.permission.permission_name
                break

        user_group_to_perm = models.UserUserGroupToPerm()
        user_group_to_perm.permission = models.Permission.get_by_key(default_perm)

        user_group_to_perm.user_group = user_group
        user_group_to_perm.user_id = def_user.user_id
        return user_group_to_perm

    for ug in models.UserGroup.get_all():
        perm_obj = _create_default_perms(ug)
        _SESSION().add(perm_obj)
    _SESSION().commit()

    adm = models.User.get_first_admin()
    # fix owners of UserGroup
    for ug in _SESSION().query(models.UserGroup).all():
        ug.user_id = adm.user_id
        _SESSION().add(ug)
    _SESSION().commit()

    # fix owners of RepoGroup
    for ug in _SESSION().query(models.RepoGroup).all():
        ug.user_id = adm.user_id
        _SESSION().add(ug)
    _SESSION().commit()
