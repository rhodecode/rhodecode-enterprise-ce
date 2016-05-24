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
SQLAlchemy Metadata and Session object
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from beaker import cache

from rhodecode.lib import caching_query


# Beaker CacheManager.  A home base for cache configurations.
cache_manager = cache.CacheManager()

__all__ = ['Base', 'Session']
#
# SQLAlchemy session manager. Updated by model.init_model()
#
Session = scoped_session(
                sessionmaker(
                    query_cls=caching_query.query_callable(cache_manager),
                    expire_on_commit=True,
                )
          )

# The declarative Base
Base = declarative_base()

#to use cache use this in query
#.options(FromCache("sqlalchemy_cache_type", "cachekey"))
