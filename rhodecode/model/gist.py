# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016  RhodeCode GmbH
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
gist model for RhodeCode
"""

import os
import time
import logging
import traceback
import shutil

from rhodecode.lib.utils2 import (
    safe_unicode, unique_id, safe_int, time_to_datetime, AttributeDict)
from rhodecode.lib.ext_json import json
from rhodecode.model import BaseModel
from rhodecode.model.db import Gist
from rhodecode.model.repo import RepoModel
from rhodecode.model.scm import ScmModel

log = logging.getLogger(__name__)

GIST_STORE_LOC = '.rc_gist_store'
GIST_METADATA_FILE = '.rc_gist_metadata'


class GistModel(BaseModel):
    cls = Gist

    def _get_gist(self, gist):
        """
        Helper method to get gist by ID, or gist_access_id as a fallback

        :param gist: GistID, gist_access_id, or Gist instance
        """
        return self._get_instance(Gist, gist, callback=Gist.get_by_access_id)

    def __delete_gist(self, gist):
        """
        removes gist from filesystem

        :param gist: gist object
        """
        root_path = RepoModel().repos_path
        rm_path = os.path.join(root_path, GIST_STORE_LOC, gist.gist_access_id)
        log.info("Removing %s", rm_path)
        shutil.rmtree(rm_path)

    def _store_metadata(self, repo, gist_id, gist_access_id, user_id, username,
                        gist_type, gist_expires, gist_acl_level):
        """
        store metadata inside the gist repo, this can be later used for imports
        or gist identification. Currently we use this inside RhodeCode tools
        to do cleanup of gists that are in storage but not in database.
        """
        metadata = {
            'metadata_version': '2',
            'gist_db_id': gist_id,
            'gist_access_id': gist_access_id,
            'gist_owner_id': user_id,
            'gist_owner_username': username,
            'gist_type': gist_type,
            'gist_expires': gist_expires,
            'gist_updated': time.time(),
            'gist_acl_level': gist_acl_level,
        }
        metadata_file = os.path.join(repo.path, '.hg', GIST_METADATA_FILE)
        with open(metadata_file, 'wb') as f:
            f.write(json.dumps(metadata))

    def get_gist(self, gist):
        return self._get_gist(gist)

    def get_gist_files(self, gist_access_id, revision=None):
        """
        Get files for given gist

        :param gist_access_id:
        """
        repo = Gist.get_by_access_id(gist_access_id)
        commit = repo.scm_instance().get_commit(commit_id=revision)
        return commit, [n for n in commit.get_node('/')]

    def create(self, description, owner, gist_mapping,
               gist_type=Gist.GIST_PUBLIC, lifetime=-1, gist_id=None,
               gist_acl_level=Gist.ACL_LEVEL_PRIVATE):
        """
        Create a gist

        :param description: description of the gist
        :param owner: user who created this gist
        :param gist_mapping: mapping {filename:{'content':content},...}
        :param gist_type: type of gist private/public
        :param lifetime: in minutes, -1 == forever
        :param gist_acl_level: acl level for this gist
        """
        owner = self._get_user(owner)
        gist_id = safe_unicode(gist_id or unique_id(20))
        lifetime = safe_int(lifetime, -1)
        gist_expires = time.time() + (lifetime * 60) if lifetime != -1 else -1
        expiration = (time_to_datetime(gist_expires)
                      if gist_expires != -1 else 'forever')
        log.debug('set GIST expiration date to: %s', expiration)
        # create the Database version
        gist = Gist()
        gist.gist_description = description
        gist.gist_access_id = gist_id
        gist.gist_owner = owner.user_id
        gist.gist_expires = gist_expires
        gist.gist_type = safe_unicode(gist_type)
        gist.acl_level = gist_acl_level
        self.sa.add(gist)
        self.sa.flush()
        if gist_type == Gist.GIST_PUBLIC:
            # use DB ID for easy to use GIST ID
            gist_id = safe_unicode(gist.gist_id)
            gist.gist_access_id = gist_id
            self.sa.add(gist)

        gist_repo_path = os.path.join(GIST_STORE_LOC, gist_id)
        log.debug('Creating new %s GIST repo in %s', gist_type, gist_repo_path)
        repo = RepoModel()._create_filesystem_repo(
            repo_name=gist_id, repo_type='hg', repo_group=GIST_STORE_LOC,
            use_global_config=True)

        processed_mapping = {}
        for filename in gist_mapping:
            if filename != os.path.basename(filename):
                raise Exception('Filename cannot be inside a directory')

            content = gist_mapping[filename]['content']
            # TODO: expand support for setting explicit lexers
#             if lexer is None:
#                 try:
#                     guess_lexer = pygments.lexers.guess_lexer_for_filename
#                     lexer = guess_lexer(filename,content)
#                 except pygments.util.ClassNotFound:
#                     lexer = 'text'
            processed_mapping[filename] = {'content': content}

        # now create single multifile commit
        message = 'added file'
        message += 's: ' if len(processed_mapping) > 1 else ': '
        message += ', '.join([x for x in processed_mapping])

        # fake RhodeCode Repository object
        fake_repo = AttributeDict({
            'repo_name': gist_repo_path,
            'scm_instance': lambda *args, **kwargs: repo,
        })

        ScmModel().create_nodes(
            user=owner.user_id, repo=fake_repo,
            message=message,
            nodes=processed_mapping,
            trigger_push_hook=False
        )

        self._store_metadata(repo, gist.gist_id, gist.gist_access_id,
                             owner.user_id, owner.username, gist.gist_type,
                             gist.gist_expires, gist_acl_level)
        return gist

    def delete(self, gist, fs_remove=True):
        gist = self._get_gist(gist)
        try:
            self.sa.delete(gist)
            if fs_remove:
                self.__delete_gist(gist)
            else:
                log.debug('skipping removal from filesystem')
        except Exception:
            log.error(traceback.format_exc())
            raise

    def update(self, gist, description, owner, gist_mapping, gist_type,
               lifetime, gist_acl_level):
        gist = self._get_gist(gist)
        gist_repo = gist.scm_instance()

        lifetime = safe_int(lifetime, -1)
        if lifetime == 0:  # preserve old value
            gist_expires = gist.gist_expires
        else:
            gist_expires = (
                time.time() + (lifetime * 60) if lifetime != -1 else -1)

        # calculate operation type based on given data
        gist_mapping_op = {}
        for k, v in gist_mapping.items():
            # add, mod, del
            if not v['org_filename'] and v['filename']:
                op = 'add'
            elif v['org_filename'] and not v['filename']:
                op = 'del'
            else:
                op = 'mod'

            v['op'] = op
            gist_mapping_op[k] = v

        gist.gist_description = description
        gist.gist_expires = gist_expires
        gist.owner = owner
        gist.gist_type = gist_type
        gist.acl_level = gist_acl_level
        self.sa.add(gist)
        self.sa.flush()

        message = 'updated file'
        message += 's: ' if len(gist_mapping) > 1 else ': '
        message += ', '.join([x for x in gist_mapping])

        # fake RhodeCode Repository object
        fake_repo = AttributeDict({
            'repo_name': gist_repo.path,
            'scm_instance': lambda *args, **kwargs: gist_repo,
        })

        self._store_metadata(gist_repo, gist.gist_id, gist.gist_access_id,
                             owner.user_id, owner.username, gist.gist_type,
                             gist.gist_expires, gist_acl_level)

        # this can throw NodeNotChangedError, if changes we're trying to commit
        # are not actually changes...
        ScmModel().update_nodes(
            user=owner.user_id,
            repo=fake_repo,
            message=message,
            nodes=gist_mapping_op,
            trigger_push_hook=False
        )

        return gist
