# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, version 3
# (only), as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is dual-licensed. If you wish to learn more about the
# RhodeCode Enterprise Edition, including its added features, Support services,
# and proprietary license terms, please see https://rhodecode.com/licenses/

"""
The application's model objects

:example:

    .. code-block:: python

       from paste.deploy import appconfig
       from pylons import config
       from sqlalchemy import engine_from_config
       from rhodecode.config.environment import load_environment

       conf = appconfig('config:development.ini', relative_to = './../../')
       load_environment(conf.global_conf, conf.local_conf)

       engine = engine_from_config(config, 'sqlalchemy.')
       init_model(engine)
       # RUN YOUR CODE HERE

"""


import logging

from pylons import config
from pyramid.threadlocal import get_current_registry

from rhodecode.model import meta, db
from rhodecode.lib.utils2 import obfuscate_url_pw

log = logging.getLogger(__name__)


def init_model(engine, encryption_key=None):
    """
    Initializes db session, bind the engine with the metadata,
    Call this before using any of the tables or classes in the model,
    preferably once in application start

    :param engine: engine to bind to
    """
    engine_str = obfuscate_url_pw(str(engine.url))
    log.info("initializing db for %s", engine_str)
    meta.Base.metadata.bind = engine
    db.ENCRYPTION_KEY = encryption_key


def init_model_encryption(migration_models):
    migration_models.ENCRYPTION_KEY = config['beaker.session.secret']
    db.ENCRYPTION_KEY = config['beaker.session.secret']


class BaseModel(object):
    """
    Base Model for all RhodeCode models, it adds sql alchemy session
    into instance of model

    :param sa: If passed it reuses this session instead of creating a new one
    """

    cls = None  # override in child class

    def __init__(self, sa=None):
        if sa is not None:
            self.sa = sa
        else:
            self.sa = meta.Session()

    def _get_instance(self, cls, instance, callback=None):
        """
        Gets instance of given cls using some simple lookup mechanism.

        :param cls: class to fetch
        :param instance: int or Instance
        :param callback: callback to call if all lookups failed
        """

        if isinstance(instance, cls):
            return instance
        elif isinstance(instance, (int, long)):
            return cls.get(instance)
        else:
            if instance:
                if callback is None:
                    raise Exception(
                        'given object must be int, long or Instance of %s '
                        'got %s, no callback provided' % (cls, type(instance))
                    )
                else:
                    return callback(instance)

    def _get_user(self, user):
        """
        Helper method to get user by ID, or username fallback

        :param user: UserID, username, or User instance
        """
        return self._get_instance(
            db.User, user, callback=db.User.get_by_username)

    def _get_user_group(self, user_group):
        """
        Helper method to get user by ID, or username fallback

        :param user_group: UserGroupID, user_group_name, or UserGroup instance
        """
        return self._get_instance(
            db.UserGroup, user_group, callback=db.UserGroup.get_by_group_name)

    def _get_repo(self, repository):
        """
        Helper method to get repository by ID, or repository name

        :param repository: RepoID, repository name or Repository Instance
        """
        return self._get_instance(
            db.Repository, repository, callback=db.Repository.get_by_repo_name)

    def _get_perm(self, permission):
        """
        Helper method to get permission by ID, or permission name

        :param permission: PermissionID, permission_name or Permission instance
        """
        return self._get_instance(
            db.Permission, permission, callback=db.Permission.get_by_key)

    def send_event(self, event):
        """
        Helper method to send an event. This wraps the pyramid logic to send an
        event.
        """
        # For the first step we are using pyramids thread locals here. If the
        # event mechanism works out as a good solution we should think about
        # passing the registry into the constructor to get rid of it.
        registry = get_current_registry()
        registry.notify(event)

    @classmethod
    def get_all(cls):
        """
        Returns all instances of what is defined in `cls` class variable
        """
        return cls.cls.getAll()
