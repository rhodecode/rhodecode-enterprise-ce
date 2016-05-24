# -*- coding: utf-8 -*-

import hashlib
import logging

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import Text, String, Column
from sqlalchemy.engine import reflection
from sqlalchemy.sql import text

from rhodecode.lib.dbmigrate.versions import _reset_base
from rhodecode.lib.utils2 import safe_str
from rhodecode.model import meta, init_model_encryption


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

    repository = db_3_7_0_0.Repository.__table__
    repo_name_column = repository.columns.repo_name
    clone_uri_column = repository.columns.clone_uri

    indexes = _get_indexes_list(migrate_engine, repository.name)
    repo_name_indexes = [
        i['name'] for i in indexes if 'repo_name' in i['column_names']]
    constraints = _get_unique_constraint_list(migrate_engine, repository.name)
    repo_name_constraints = [
        c['name'] for c in constraints if 'repo_name' in c['column_names']]

    with op.batch_alter_table(repository.name) as batch_op:
        repo_name_idx = 'r_repo_name_idx'
        if repo_name_idx in repo_name_indexes:
            batch_op.drop_index(repo_name_idx)
        for name in repo_name_constraints:
            batch_op.drop_constraint(name, type_='unique')

        batch_op.alter_column(repo_name_column.name, type_=Text)
        batch_op.alter_column(clone_uri_column.name, type_=Text)
        batch_op.create_index(
            'r_repo_name_idx', ['repo_name'], mysql_length=255)
        batch_op.add_column(Column('repo_name_hash', String(40), unique=False))

    _generate_repo_name_hashes(db_3_7_0_0, op, meta.Session)

    with op.batch_alter_table(repository.name) as batch_op:
        batch_op.create_unique_constraint(
            'uq_repo_name_hash', ['repo_name_hash'])


def downgrade(migrate_engine):
    pass


def _generate_repo_name_hashes(models, op, session):
    repositories = models.Repository.get_all()
    for repository in repositories:
        hash_ = hashlib.sha1(safe_str(repository.repo_name)).hexdigest()
        params = {'hash': hash_, 'id': repository.repo_id}
        query = text(
            'UPDATE repositories SET repo_name_hash = :hash'
            ' WHERE repo_id = :id').bindparams(**params)
        op.execute(query)
    session().commit()


def _get_unique_constraint_list(migrate_engine, table_name):
    inspector = reflection.Inspector.from_engine(migrate_engine)
    return inspector.get_unique_constraints(table_name)


def _get_indexes_list(migrate_engine, table_name):
    inspector = reflection.Inspector.from_engine(migrate_engine)
    return inspector.get_indexes(table_name)
