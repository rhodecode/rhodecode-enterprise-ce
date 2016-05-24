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
    return cls.query().filter(cls.ui_key == key).scalar()


def create_or_update_hook(cls, key, val, SESSION):
    new_ui = get_by_key(cls, key) or cls()
    new_ui.ui_section = 'hooks'
    new_ui.ui_active = True
    new_ui.ui_key = key
    new_ui.ui_value = val

    SESSION().add(new_ui)


def upgrade(migrate_engine):
    """
    Upgrade operations go here.
    Don't create your own engine; bind migrate_engine to your metadata
    """
    _reset_base(migrate_engine)
    from rhodecode.lib.dbmigrate.schema import db_3_0_0_0

    # issue fixups
    fixups(db_3_0_0_0, meta.Session)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine


def fixups(models, _SESSION):

    cleanup_if_present = (
        models.RhodeCodeUi.HOOK_REPO_SIZE,
        models.RhodeCodeUi.HOOK_PRE_PULL,
        models.RhodeCodeUi.HOOK_PRE_PUSH,
        models.RhodeCodeUi.HOOK_PUSH,
        models.RhodeCodeUi.HOOK_PULL,
        models.RhodeCodeUi.HOOK_PRE_PULL_GIT,
        models.RhodeCodeUi.HOOK_PULL_GIT,
        models.RhodeCodeUi.HOOK_PRE_PUSH_GIT,
        models.RhodeCodeUi.HOOK_PUSH_GIT)

    for hook in cleanup_if_present:
        ui_cfg = models.RhodeCodeUi.query().filter(
            models.RhodeCodeUi.ui_key == hook).scalar()
        if ui_cfg is not None:
            log.info('Removing RhodeCodeUI for hook "%s".', hook)
            _SESSION().delete(ui_cfg)

    to_add = [
        (models.RhodeCodeUi.HOOK_REPO_SIZE,
         'python:vcsserver.hooks.repo_size'),
        (models.RhodeCodeUi.HOOK_PRE_PULL,
         'python:vcsserver.hooks.pre_pull'),
        (models.RhodeCodeUi.HOOK_PRE_PUSH,
         'python:vcsserver.hooks.pre_push'),
        (models.RhodeCodeUi.HOOK_PULL,
         'python:vcsserver.hooks.log_pull_action'),
        (models.RhodeCodeUi.HOOK_PUSH,
         'python:vcsserver.hooks.log_push_action')]

    for hook, value in to_add:
        log.info('Adding RhodeCodeUI for hook "%s".', hook)
        create_or_update_hook(models.RhodeCodeUi, hook, value, _SESSION)

    _SESSION().commit()
