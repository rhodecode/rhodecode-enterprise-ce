# -*- coding: utf-8 -*-

# Copyright (C) 2016-2016  RhodeCode GmbH
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

import pytest

from mock import patch

from rhodecode.lib.vcs.backends.base import Reference


class TestMercurialRemoteRepoInvalidation(object):
    ref_stub = Reference('branch', 'default', None)

    @pytest.mark.parametrize('method_name', [
        'bookmark',
        'commit',
        'pull',
        'pull_cmd',
        'push',
        'rebase',
        'strip',
        'strip',
    ])
    def test_method_invokes_invalidate_on_remote_repo(
            self, method_name, backend_hg):
        """
        Check that the listed methods call invalidate_vcs_cache on their remote
        repo instance.
        """
        from rhodecode.lib.vcs import client_http
        repo = backend_hg.repo.scm_instance()
        remote = repo._remote
        with patch.object(remote, 'invalidate_vcs_cache') as invalidate_cache:
            with patch.object(client_http, '_remote_call'):
                method = getattr(remote, method_name)
                method()
                assert invalidate_cache.called

    def _prepare_shadow_repo(self, pull_request):
        """
        Helper that creates a shadow repo that can be used to reproduce the
        CommitDoesNotExistError when pulling in from target and source
        references.
        """
        from rhodecode.model.pull_request import PullRequestModel

        target_vcs = pull_request.target_repo.scm_instance()
        target_ref = pull_request.target_ref_parts
        source_ref = pull_request.source_ref_parts

        # Create shadow repository.
        pr = PullRequestModel()
        workspace_id = pr._workspace_id(pull_request)
        shadow_repository_path = target_vcs._maybe_prepare_merge_workspace(
            workspace_id, target_ref)
        shadow_repo = target_vcs._get_shadow_instance(shadow_repository_path)

        # This will populate the cache of the mercurial repository object
        # inside of the VCSServer.
        shadow_repo.get_commit()

        return shadow_repo, source_ref, target_ref

    @pytest.mark.backends('hg')
    def test_commit_does_not_exist_error_happens(self, pr_util):
        from rhodecode.lib.vcs.exceptions import CommitDoesNotExistError

        pull_request = pr_util.create_pull_request()
        target_vcs = pull_request.target_repo.scm_instance()
        source_vcs = pull_request.source_repo.scm_instance()
        shadow_repo, source_ref, target_ref = self._prepare_shadow_repo(
            pull_request)

        # Pull from target and source references but without invalidation of
        # RemoteRepo objects and without VCSServer caching of mercurial
        # repository objects.
        with patch.object(shadow_repo._remote, 'invalidate_vcs_cache'):
            # NOTE: Do not use patch.dict() to disable the cache because it
            # restores the WHOLE dict and not only the patched keys.
            shadow_repo._remote._wire['cache'] = False
            shadow_repo._local_pull(target_vcs.path, target_ref)
            shadow_repo._local_pull(source_vcs.path, source_ref)
            shadow_repo._remote._wire.pop('cache')

        # Try to lookup the target_ref in shadow repo. This should work because
        # the shadow repo is a clone of the target and always contains all off
        # it's commits in the initial cache.
        shadow_repo.get_commit(target_ref.commit_id)

        # If we try to lookup the source_ref it should fail because the shadow
        # repo commit cache doesn't get invalidated. (Due to patched
        # invalidation and caching above).
        with pytest.raises(CommitDoesNotExistError):
            shadow_repo.get_commit(source_ref.commit_id)

    @pytest.mark.backends('hg')
    def test_commit_does_not_exist_error_does_not_happen(self, pr_util):
        pull_request = pr_util.create_pull_request()
        target_vcs = pull_request.target_repo.scm_instance()
        source_vcs = pull_request.source_repo.scm_instance()
        shadow_repo, source_ref, target_ref = self._prepare_shadow_repo(
            pull_request)

        # Pull from target and source references without without VCSServer
        # caching of mercurial repository objects but with active invalidation
        # of RemoteRepo objects.
        # NOTE: Do not use patch.dict() to disable the cache because it
        # restores the WHOLE dict and not only the patched keys.
        shadow_repo._remote._wire['cache'] = False
        shadow_repo._local_pull(target_vcs.path, target_ref)
        shadow_repo._local_pull(source_vcs.path, source_ref)
        shadow_repo._remote._wire.pop('cache')

        # Try to lookup the target and source references in shadow repo. This
        # should work because the RemoteRepo object gets invalidated during the
        # above pull operations.
        shadow_repo.get_commit(target_ref.commit_id)
        shadow_repo.get_commit(source_ref.commit_id)
