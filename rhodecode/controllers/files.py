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
Files controller for RhodeCode Enterprise
"""

import itertools
import logging
import os
import shutil
import tempfile

from pylons import request, response, tmpl_context as c, url
from pylons.i18n.translation import _
from pylons.controllers.util import redirect
from webob.exc import HTTPNotFound, HTTPBadRequest

from rhodecode.controllers.utils import parse_path_ref
from rhodecode.lib import diffs, helpers as h, caches
from rhodecode.lib.compat import OrderedDict
from rhodecode.lib.utils import jsonify, action_logger
from rhodecode.lib.utils2 import (
    convert_line_endings, detect_mode, safe_str, str2bool)
from rhodecode.lib.auth import (
    LoginRequired, HasRepoPermissionAnyDecorator, CSRFRequired, XHRRequired)
from rhodecode.lib.base import BaseRepoController, render
from rhodecode.lib.vcs import path as vcspath
from rhodecode.lib.vcs.backends.base import EmptyCommit
from rhodecode.lib.vcs.conf import settings
from rhodecode.lib.vcs.exceptions import (
    RepositoryError, CommitDoesNotExistError, EmptyRepositoryError,
    ImproperArchiveTypeError, VCSError, NodeAlreadyExistsError,
    NodeDoesNotExistError, CommitError, NodeError)
from rhodecode.lib.vcs.nodes import FileNode

from rhodecode.model.repo import RepoModel
from rhodecode.model.scm import ScmModel
from rhodecode.model.db import Repository

from rhodecode.controllers.changeset import (
    _ignorews_url, _context_url, get_line_ctx, get_ignore_ws)
from rhodecode.lib.exceptions import NonRelativePathError

log = logging.getLogger(__name__)


class FilesController(BaseRepoController):

    def __before__(self):
        super(FilesController, self).__before__()
        c.cut_off_limit = self.cut_off_limit_file

    def _get_default_encoding(self):
        enc_list = getattr(c, 'default_encodings', [])
        return enc_list[0] if enc_list else 'UTF-8'

    def __get_commit_or_redirect(self, commit_id, repo_name,
                                 redirect_after=True):
        """
        This is a safe way to get commit. If an error occurs it redirects to
        tip with proper message

        :param commit_id: id of commit to fetch
        :param repo_name: repo name to redirect after
        :param redirect_after: toggle redirection
        """
        try:
            return c.rhodecode_repo.get_commit(commit_id)
        except EmptyRepositoryError:
            if not redirect_after:
                return None
            url_ = url('files_add_home',
                       repo_name=c.repo_name,
                       revision=0, f_path='', anchor='edit')
            if h.HasRepoPermissionAny(
                    'repository.write', 'repository.admin')(c.repo_name):
                add_new = h.link_to(
                    _('Click here to add a new file.'),
                    url_, class_="alert-link")
            else:
                add_new = ""
            h.flash(h.literal(
                _('There are no files yet. %s') % add_new), category='warning')
            redirect(h.url('summary_home', repo_name=repo_name))
        except (CommitDoesNotExistError, LookupError):
            msg = _('No such commit exists for this repository')
            h.flash(msg, category='error')
            raise HTTPNotFound()
        except RepositoryError as e:
            h.flash(safe_str(e), category='error')
            raise HTTPNotFound()

    def __get_filenode_or_redirect(self, repo_name, commit, path):
        """
        Returns file_node, if error occurs or given path is directory,
        it'll redirect to top level path

        :param repo_name: repo_name
        :param commit: given commit
        :param path: path to lookup
        """
        try:
            file_node = commit.get_node(path)
            if file_node.is_dir():
                raise RepositoryError('The given path is a directory')
        except CommitDoesNotExistError:
            msg = _('No such commit exists for this repository')
            log.exception(msg)
            h.flash(msg, category='error')
            raise HTTPNotFound()
        except RepositoryError as e:
            h.flash(safe_str(e), category='error')
            raise HTTPNotFound()

        return file_node

    def __get_tree_cache_manager(self, repo_name, namespace_type):
        _namespace = caches.get_repo_namespace_key(namespace_type, repo_name)
        return caches.get_cache_manager('repo_cache_long', _namespace)

    def _get_tree_at_commit(self, repo_name, commit_id, f_path,
                            full_load=False, force=False):
        def _cached_tree():
            log.debug('Generating cached file tree for %s, %s, %s',
                      repo_name, commit_id, f_path)
            c.full_load = full_load
            return render('files/files_browser_tree.html')

        cache_manager = self.__get_tree_cache_manager(
            repo_name, caches.FILE_TREE)

        cache_key = caches.compute_key_from_params(
            repo_name, commit_id, f_path)

        if force:
            # we want to force recompute of caches
            cache_manager.remove_value(cache_key)

        return cache_manager.get(cache_key, createfunc=_cached_tree)

    def _get_nodelist_at_commit(self, repo_name, commit_id, f_path):
        def _cached_nodes():
            log.debug('Generating cached nodelist for %s, %s, %s',
                      repo_name, commit_id, f_path)
            _d, _f = ScmModel().get_nodes(
                repo_name, commit_id, f_path, flat=False)
            return _d + _f

        cache_manager = self.__get_tree_cache_manager(
            repo_name, caches.FILE_SEARCH_TREE_META)

        cache_key = caches.compute_key_from_params(
            repo_name, commit_id, f_path)
        return cache_manager.get(cache_key, createfunc=_cached_nodes)

    @LoginRequired()
    @HasRepoPermissionAnyDecorator(
        'repository.read', 'repository.write', 'repository.admin')
    def index(
            self, repo_name, revision, f_path, annotate=False, rendered=False):
        commit_id = revision

        # redirect to given commit_id from form if given
        get_commit_id = request.GET.get('at_rev', None)
        if get_commit_id:
            self.__get_commit_or_redirect(get_commit_id, repo_name)

        c.commit = self.__get_commit_or_redirect(commit_id, repo_name)
        c.branch = request.GET.get('branch', None)
        c.f_path = f_path
        c.annotate = annotate
        # default is false, but .rst/.md files later are autorendered, we can
        # overwrite autorendering by setting this GET flag
        c.renderer = rendered or not request.GET.get('no-render', False)

        # prev link
        try:
            prev_commit = c.commit.prev(c.branch)
            c.prev_commit = prev_commit
            c.url_prev = url('files_home', repo_name=c.repo_name,
                             revision=prev_commit.raw_id, f_path=f_path)
            if c.branch:
                c.url_prev += '?branch=%s' % c.branch
        except (CommitDoesNotExistError, VCSError):
            c.url_prev = '#'
            c.prev_commit = EmptyCommit()

        # next link
        try:
            next_commit = c.commit.next(c.branch)
            c.next_commit = next_commit
            c.url_next = url('files_home', repo_name=c.repo_name,
                             revision=next_commit.raw_id, f_path=f_path)
            if c.branch:
                c.url_next += '?branch=%s' % c.branch
        except (CommitDoesNotExistError, VCSError):
            c.url_next = '#'
            c.next_commit = EmptyCommit()

        # files or dirs
        try:
            c.file = c.commit.get_node(f_path)
            c.file_author = True
            c.file_tree = ''
            if c.file.is_file():
                c.renderer = (
                    c.renderer and h.renderer_from_filename(c.file.path))
                c.file_last_commit = c.file.last_commit

                c.on_branch_head = self._is_valid_head(
                    commit_id, c.rhodecode_repo)
                c.branch_or_raw_id = c.commit.branch or c.commit.raw_id

                author = c.file_last_commit.author
                c.authors = [(h.email(author),
                              h.person(author, 'username_or_name_or_email'))]
            else:
                c.authors = []
                c.file_tree = self._get_tree_at_commit(
                    repo_name, c.commit.raw_id, f_path)

        except RepositoryError as e:
            h.flash(safe_str(e), category='error')
            raise HTTPNotFound()

        if request.environ.get('HTTP_X_PJAX'):
            return render('files/files_pjax.html')

        return render('files/files.html')

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    @jsonify
    def history(self, repo_name, revision, f_path):
        commit = self.__get_commit_or_redirect(revision, repo_name)
        f_path = f_path
        _file = commit.get_node(f_path)
        if _file.is_file():
            file_history, _hist = self._get_node_history(commit, f_path)

            res = []
            for obj in file_history:
                res.append({
                    'text': obj[1],
                    'children': [{'id': o[0], 'text': o[1]} for o in obj[0]]
                })

            data = {
                'more': False,
                'results': res
            }
            return data

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def authors(self, repo_name, revision, f_path):
        commit = self.__get_commit_or_redirect(revision, repo_name)
        file_node = commit.get_node(f_path)
        if file_node.is_file():
            c.file_last_commit = file_node.last_commit
            if request.GET.get('annotate') == '1':
                # use _hist from annotation if annotation mode is on
                commit_ids = set(x[1] for x in file_node.annotate)
                _hist = (
                    c.rhodecode_repo.get_commit(commit_id)
                    for commit_id in commit_ids)
            else:
                _f_history, _hist = self._get_node_history(commit, f_path)
            c.file_author = False
            c.authors = []
            for author in set(commit.author for commit in _hist):
                c.authors.append((
                    h.email(author),
                    h.person(author, 'username_or_name_or_email')))
            return render('files/file_authors_box.html')

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def rawfile(self, repo_name, revision, f_path):
        """
        Action for download as raw
        """
        commit = self.__get_commit_or_redirect(revision, repo_name)
        file_node = self.__get_filenode_or_redirect(repo_name, commit, f_path)

        response.content_disposition = 'attachment; filename=%s' % \
            safe_str(f_path.split(Repository.NAME_SEP)[-1])

        response.content_type = file_node.mimetype
        charset = self._get_default_encoding()
        if charset:
            response.charset = charset

        return file_node.content

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def raw(self, repo_name, revision, f_path):
        """
        Action for show as raw, some mimetypes are "rendered",
        those include images, icons.
        """
        commit = self.__get_commit_or_redirect(revision, repo_name)
        file_node = self.__get_filenode_or_redirect(repo_name, commit, f_path)

        raw_mimetype_mapping = {
            # map original mimetype to a mimetype used for "show as raw"
            # you can also provide a content-disposition to override the
            # default "attachment" disposition.
            # orig_type: (new_type, new_dispo)

            # show images inline:
            # Do not re-add SVG: it is unsafe and permits XSS attacks. One can
            # for example render an SVG with javascript inside or even render
            # HTML.
            'image/x-icon': ('image/x-icon', 'inline'),
            'image/png': ('image/png', 'inline'),
            'image/gif': ('image/gif', 'inline'),
            'image/jpeg': ('image/jpeg', 'inline'),
        }

        mimetype = file_node.mimetype
        try:
            mimetype, dispo = raw_mimetype_mapping[mimetype]
        except KeyError:
            # we don't know anything special about this, handle it safely
            if file_node.is_binary:
                # do same as download raw for binary files
                mimetype, dispo = 'application/octet-stream', 'attachment'
            else:
                # do not just use the original mimetype, but force text/plain,
                # otherwise it would serve text/html and that might be unsafe.
                # Note: underlying vcs library fakes text/plain mimetype if the
                # mimetype can not be determined and it thinks it is not
                # binary.This might lead to erroneous text display in some
                # cases, but helps in other cases, like with text files
                # without extension.
                mimetype, dispo = 'text/plain', 'inline'

        if dispo == 'attachment':
            dispo = 'attachment; filename=%s' % safe_str(
                f_path.split(os.sep)[-1])

        response.content_disposition = dispo
        response.content_type = mimetype
        charset = self._get_default_encoding()
        if charset:
            response.charset = charset
        return file_node.content

    @CSRFRequired()
    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.write', 'repository.admin')
    def delete(self, repo_name, revision, f_path):
        commit_id = revision

        repo = c.rhodecode_db_repo
        if repo.enable_locking and repo.locked[0]:
            h.flash(_('This repository has been locked by %s on %s')
                    % (h.person_by_id(repo.locked[0]),
                    h.format_date(h.time_to_datetime(repo.locked[1]))),
                    'warning')
            return redirect(h.url('files_home',
                                  repo_name=repo_name, revision='tip'))

        if not self._is_valid_head(commit_id, repo.scm_instance()):
            h.flash(_('You can only delete files with revision '
                      'being a valid branch '), category='warning')
            return redirect(h.url('files_home',
                                  repo_name=repo_name, revision='tip',
                                  f_path=f_path))

        c.commit = self.__get_commit_or_redirect(commit_id, repo_name)
        c.file = self.__get_filenode_or_redirect(repo_name, c.commit, f_path)

        c.default_message = _(
            'Deleted file %s via RhodeCode Enterprise') % (f_path)
        c.f_path = f_path
        node_path = f_path
        author = c.rhodecode_user.full_contact
        message = request.POST.get('message') or c.default_message
        try:
            nodes = {
                node_path: {
                    'content': ''
                }
            }
            self.scm_model.delete_nodes(
                user=c.rhodecode_user.user_id, repo=c.rhodecode_db_repo,
                message=message,
                nodes=nodes,
                parent_commit=c.commit,
                author=author,
            )

            h.flash(_('Successfully deleted file %s') % f_path,
                    category='success')
        except Exception:
            msg = _('Error occurred during commit')
            log.exception(msg)
            h.flash(msg, category='error')
        return redirect(url('changeset_home',
                            repo_name=c.repo_name, revision='tip'))

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.write', 'repository.admin')
    def delete_home(self, repo_name, revision, f_path):
        commit_id = revision

        repo = c.rhodecode_db_repo
        if repo.enable_locking and repo.locked[0]:
            h.flash(_('This repository has been locked by %s on %s')
                    % (h.person_by_id(repo.locked[0]),
                    h.format_date(h.time_to_datetime(repo.locked[1]))),
                    'warning')
            return redirect(h.url('files_home',
                                  repo_name=repo_name, revision='tip'))

        if not self._is_valid_head(commit_id, repo.scm_instance()):
            h.flash(_('You can only delete files with revision '
                      'being a valid branch '), category='warning')
            return redirect(h.url('files_home',
                                  repo_name=repo_name, revision='tip',
                                  f_path=f_path))

        c.commit = self.__get_commit_or_redirect(commit_id, repo_name)
        c.file = self.__get_filenode_or_redirect(repo_name, c.commit, f_path)

        c.default_message = _(
            'Deleted file %s via RhodeCode Enterprise') % (f_path)
        c.f_path = f_path

        return render('files/files_delete.html')

    @CSRFRequired()
    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.write', 'repository.admin')
    def edit(self, repo_name, revision, f_path):
        commit_id = revision

        repo = c.rhodecode_db_repo
        if repo.enable_locking and repo.locked[0]:
            h.flash(_('This repository has been locked by %s on %s')
                    % (h.person_by_id(repo.locked[0]),
                    h.format_date(h.time_to_datetime(repo.locked[1]))),
                    'warning')
            return redirect(h.url('files_home',
                                  repo_name=repo_name, revision='tip'))

        if not self._is_valid_head(commit_id, repo.scm_instance()):
            h.flash(_('You can only edit files with revision '
                      'being a valid branch '), category='warning')
            return redirect(h.url('files_home',
                                  repo_name=repo_name, revision='tip',
                                  f_path=f_path))

        c.commit = self.__get_commit_or_redirect(commit_id, repo_name)
        c.file = self.__get_filenode_or_redirect(repo_name, c.commit, f_path)

        if c.file.is_binary:
            return redirect(url('files_home', repo_name=c.repo_name,
                            revision=c.commit.raw_id, f_path=f_path))
        c.default_message = _(
            'Edited file %s via RhodeCode Enterprise') % (f_path)
        c.f_path = f_path
        old_content = c.file.content
        sl = old_content.splitlines(1)
        first_line = sl[0] if sl else ''

        # modes:  0 - Unix, 1 - Mac, 2 - DOS
        mode = detect_mode(first_line, 0)
        content = convert_line_endings(request.POST.get('content', ''), mode)

        message = request.POST.get('message') or c.default_message
        org_f_path = c.file.unicode_path
        filename = request.POST['filename']
        org_filename = c.file.name

        if content == old_content and filename == org_filename:
            h.flash(_('No changes'), category='warning')
            return redirect(url('changeset_home', repo_name=c.repo_name,
                                revision='tip'))
        try:
            mapping = {
                org_f_path: {
                    'org_filename': org_f_path,
                    'filename': os.path.join(c.file.dir_path, filename),
                    'content': content,
                    'lexer': '',
                    'op': 'mod',
                }
            }

            ScmModel().update_nodes(
                user=c.rhodecode_user.user_id,
                repo=c.rhodecode_db_repo,
                message=message,
                nodes=mapping,
                parent_commit=c.commit,
            )

            h.flash(_('Successfully committed to %s') % f_path,
                    category='success')
        except Exception:
            msg = _('Error occurred during commit')
            log.exception(msg)
            h.flash(msg, category='error')
        return redirect(url('changeset_home',
                            repo_name=c.repo_name, revision='tip'))

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.write', 'repository.admin')
    def edit_home(self, repo_name, revision, f_path):
        commit_id = revision

        repo = c.rhodecode_db_repo
        if repo.enable_locking and repo.locked[0]:
            h.flash(_('This repository has been locked by %s on %s')
                    % (h.person_by_id(repo.locked[0]),
                    h.format_date(h.time_to_datetime(repo.locked[1]))),
                    'warning')
            return redirect(h.url('files_home',
                                  repo_name=repo_name, revision='tip'))

        if not self._is_valid_head(commit_id, repo.scm_instance()):
            h.flash(_('You can only edit files with revision '
                      'being a valid branch '), category='warning')
            return redirect(h.url('files_home',
                                  repo_name=repo_name, revision='tip',
                                  f_path=f_path))

        c.commit = self.__get_commit_or_redirect(commit_id, repo_name)
        c.file = self.__get_filenode_or_redirect(repo_name, c.commit, f_path)

        if c.file.is_binary:
            return redirect(url('files_home', repo_name=c.repo_name,
                            revision=c.commit.raw_id, f_path=f_path))
        c.default_message = _(
            'Edited file %s via RhodeCode Enterprise') % (f_path)
        c.f_path = f_path

        return render('files/files_edit.html')

    def _is_valid_head(self, commit_id, repo):
        # check if commit is a branch identifier- basically we cannot
        # create multiple heads via file editing
        valid_heads = repo.branches.keys() + repo.branches.values()

        if h.is_svn(repo) and not repo.is_empty():
            # Note: Subversion only has one head, we add it here in case there
            # is no branch matched.
            valid_heads.append(repo.get_commit(commit_idx=-1).raw_id)

        # check if commit is a branch name or branch hash
        return commit_id in valid_heads

    @CSRFRequired()
    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.write', 'repository.admin')
    def add(self, repo_name, revision, f_path):
        repo = Repository.get_by_repo_name(repo_name)
        if repo.enable_locking and repo.locked[0]:
            h.flash(_('This repository has been locked by %s on %s')
                    % (h.person_by_id(repo.locked[0]),
                    h.format_date(h.time_to_datetime(repo.locked[1]))),
                    'warning')
            return redirect(h.url('files_home',
                                  repo_name=repo_name, revision='tip'))

        r_post = request.POST

        c.commit = self.__get_commit_or_redirect(
            revision, repo_name, redirect_after=False)
        if c.commit is None:
            c.commit = EmptyCommit(alias=c.rhodecode_repo.alias)
        c.default_message = (_('Added file via RhodeCode Enterprise'))
        c.f_path = f_path
        unix_mode = 0
        content = convert_line_endings(r_post.get('content', ''), unix_mode)

        message = r_post.get('message') or c.default_message
        filename = r_post.get('filename')
        location = r_post.get('location', '')  # dir location
        file_obj = r_post.get('upload_file', None)

        if file_obj is not None and hasattr(file_obj, 'filename'):
            filename = file_obj.filename
            content = file_obj.file

            if hasattr(content, 'file'):
                # non posix systems store real file under file attr
                content = content.file

        # If there's no commit, redirect to repo summary
        if type(c.commit) is EmptyCommit:
            redirect_url = "summary_home"
        else:
            redirect_url = "changeset_home"

        if not filename:
            h.flash(_('No filename'), category='warning')
            return redirect(url(redirect_url, repo_name=c.repo_name,
                                revision='tip'))

        # extract the location from filename,
        # allows using foo/bar.txt syntax to create subdirectories
        subdir_loc = filename.rsplit('/', 1)
        if len(subdir_loc) == 2:
            location = os.path.join(location, subdir_loc[0])

        # strip all crap out of file, just leave the basename
        filename = os.path.basename(filename)
        node_path = os.path.join(location, filename)
        author = c.rhodecode_user.full_contact

        try:
            nodes = {
                node_path: {
                    'content': content
                }
            }
            self.scm_model.create_nodes(
                user=c.rhodecode_user.user_id,
                repo=c.rhodecode_db_repo,
                message=message,
                nodes=nodes,
                parent_commit=c.commit,
                author=author,
            )

            h.flash(_('Successfully committed to %s') % node_path,
                    category='success')
        except NonRelativePathError as e:
            h.flash(_(
                'The location specified must be a relative path and must not '
                'contain .. in the path'), category='warning')
            return redirect(url('changeset_home', repo_name=c.repo_name,
                                revision='tip'))
        except (NodeError, NodeAlreadyExistsError) as e:
            h.flash(_(e), category='error')
        except Exception:
            msg = _('Error occurred during commit')
            log.exception(msg)
            h.flash(msg, category='error')
        return redirect(url('changeset_home',
                            repo_name=c.repo_name, revision='tip'))

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.write', 'repository.admin')
    def add_home(self, repo_name, revision, f_path):

        repo = Repository.get_by_repo_name(repo_name)
        if repo.enable_locking and repo.locked[0]:
            h.flash(_('This repository has been locked by %s on %s')
                    % (h.person_by_id(repo.locked[0]),
                    h.format_date(h.time_to_datetime(repo.locked[1]))),
                    'warning')
            return redirect(h.url('files_home',
                                  repo_name=repo_name, revision='tip'))

        c.commit = self.__get_commit_or_redirect(
            revision, repo_name, redirect_after=False)
        if c.commit is None:
            c.commit = EmptyCommit(alias=c.rhodecode_repo.alias)
        c.default_message = (_('Added file via RhodeCode Enterprise'))
        c.f_path = f_path

        return render('files/files_add.html')

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def archivefile(self, repo_name, fname):
        fileformat = None
        commit_id = None
        ext = None
        subrepos = request.GET.get('subrepos') == 'true'

        for a_type, ext_data in settings.ARCHIVE_SPECS.items():
            archive_spec = fname.split(ext_data[1])
            if len(archive_spec) == 2 and archive_spec[1] == '':
                fileformat = a_type or ext_data[1]
                commit_id = archive_spec[0]
                ext = ext_data[1]

        dbrepo = RepoModel().get_by_repo_name(repo_name)
        if not dbrepo.enable_downloads:
            return _('Downloads disabled')

        try:
            commit = c.rhodecode_repo.get_commit(commit_id)
            content_type = settings.ARCHIVE_SPECS[fileformat][0]
        except CommitDoesNotExistError:
            return _('Unknown revision %s') % commit_id
        except EmptyRepositoryError:
            return _('Empty repository')
        except KeyError:
            return _('Unknown archive type')

        # archive cache
        from rhodecode import CONFIG

        archive_name = '%s-%s%s%s' % (
            safe_str(repo_name.replace('/', '_')),
            '-sub' if subrepos else '',
            safe_str(commit.short_id), ext)

        use_cached_archive = False
        archive_cache_enabled = CONFIG.get(
            'archive_cache_dir') and not request.GET.get('no_cache')

        if archive_cache_enabled:
            # check if we it's ok to write
            if not os.path.isdir(CONFIG['archive_cache_dir']):
                os.makedirs(CONFIG['archive_cache_dir'])
            cached_archive_path = os.path.join(
                CONFIG['archive_cache_dir'], archive_name)
            if os.path.isfile(cached_archive_path):
                log.debug('Found cached archive in %s', cached_archive_path)
                fd, archive = None, cached_archive_path
                use_cached_archive = True
            else:
                log.debug('Archive %s is not yet cached', archive_name)

        if not use_cached_archive:
            # generate new archive
            fd, archive = tempfile.mkstemp()
            log.debug('Creating new temp archive in %s' % (archive,))
            try:
                commit.archive_repo(archive, kind=fileformat, subrepos=subrepos)
            except ImproperArchiveTypeError:
                return _('Unknown archive type')
            if archive_cache_enabled:
                # if we generated the archive and we have cache enabled
                # let's use this for future
                log.debug('Storing new archive in %s' % (cached_archive_path,))
                shutil.move(archive, cached_archive_path)
                archive = cached_archive_path

        def get_chunked_archive(archive):
            with open(archive, 'rb') as stream:
                while True:
                    data = stream.read(16 * 1024)
                    if not data:
                        if fd:  # fd means we used temporary file
                            os.close(fd)
                        if not archive_cache_enabled:
                            log.debug('Destroying temp archive %s', archive)
                            os.remove(archive)
                        break
                    yield data

        # store download action
        action_logger(user=c.rhodecode_user,
                      action='user_downloaded_archive:%s' % archive_name,
                      repo=repo_name, ipaddr=self.ip_addr, commit=True)
        response.content_disposition = str(
            'attachment; filename=%s' % archive_name)
        response.content_type = str(content_type)

        return get_chunked_archive(archive)

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def diff(self, repo_name, f_path):
        ignore_whitespace = request.GET.get('ignorews') == '1'
        line_context = request.GET.get('context', 3)
        diff1 = request.GET.get('diff1', '')

        path1, diff1 = parse_path_ref(diff1, default_path=f_path)

        diff2 = request.GET.get('diff2', '')
        c.action = request.GET.get('diff')
        c.no_changes = diff1 == diff2
        c.f_path = f_path
        c.big_diff = False
        c.ignorews_url = _ignorews_url
        c.context_url = _context_url
        c.changes = OrderedDict()
        c.changes[diff2] = []

        if not any((diff1, diff2)):
            h.flash(
                'Need query parameter "diff1" or "diff2" to generate a diff.',
                category='error')
            raise HTTPBadRequest()

        # special case if we want a show commit_id only, it's impl here
        # to reduce JS and callbacks

        if request.GET.get('show_rev') and diff1:
            if str2bool(request.GET.get('annotate', 'False')):
                _url = url('files_annotate_home', repo_name=c.repo_name,
                           revision=diff1, f_path=path1)
            else:
                _url = url('files_home', repo_name=c.repo_name,
                           revision=diff1, f_path=path1)

            return redirect(_url)

        try:
            node1 = self._get_file_node(diff1, path1)
            node2 = self._get_file_node(diff2, f_path)
        except (RepositoryError, NodeError):
            log.exception("Exception while trying to get node from repository")
            return redirect(url(
                'files_home', repo_name=c.repo_name, f_path=f_path))

        if all(isinstance(node.commit, EmptyCommit)
               for node in (node1, node2)):
            raise HTTPNotFound

        c.commit_1 = node1.commit
        c.commit_2 = node2.commit

        if c.action == 'download':
            _diff = diffs.get_gitdiff(node1, node2,
                                      ignore_whitespace=ignore_whitespace,
                                      context=line_context)
            diff = diffs.DiffProcessor(_diff, format='gitdiff')

            diff_name = '%s_vs_%s.diff' % (diff1, diff2)
            response.content_type = 'text/plain'
            response.content_disposition = (
                'attachment; filename=%s' % (diff_name,)
            )
            charset = self._get_default_encoding()
            if charset:
                response.charset = charset
            return diff.as_raw()

        elif c.action == 'raw':
            _diff = diffs.get_gitdiff(node1, node2,
                                      ignore_whitespace=ignore_whitespace,
                                      context=line_context)
            diff = diffs.DiffProcessor(_diff, format='gitdiff')
            response.content_type = 'text/plain'
            charset = self._get_default_encoding()
            if charset:
                response.charset = charset
            return diff.as_raw()

        else:
            fid = h.FID(diff2, node2.path)
            line_context_lcl = get_line_ctx(fid, request.GET)
            ign_whitespace_lcl = get_ignore_ws(fid, request.GET)

            __, commit1, commit2, diff, st, data = diffs.wrapped_diff(
                filenode_old=node1,
                filenode_new=node2,
                diff_limit=self.cut_off_limit_diff,
                file_limit=self.cut_off_limit_file,
                show_full_diff=request.GET.get('fulldiff'),
                ignore_whitespace=ign_whitespace_lcl,
                line_context=line_context_lcl,)

            c.lines_added = data['stats']['added'] if data else 0
            c.lines_deleted = data['stats']['deleted'] if data else 0
            c.files = [data]
            c.commit_ranges = [c.commit_1, c.commit_2]
            c.ancestor = None
            c.statuses = []
            c.target_repo = c.rhodecode_db_repo
            c.filename1 = node1.path
            c.filename = node2.path
            c.binary_file = node1.is_binary or node2.is_binary
            operation = data['operation'] if data else ''

            commit_changes = {
                # TODO: it's passing the old file to the diff to keep the
                # standard but this is not being used for this template,
                # but might need both files in the future or a more standard
                # way to work with that
                'fid': [commit1, commit2, operation,
                        c.filename, diff, st, data]
            }

            c.changes = commit_changes

        return render('files/file_diff.html')

    @LoginRequired()
    @HasRepoPermissionAnyDecorator('repository.read', 'repository.write',
                                   'repository.admin')
    def diff_2way(self, repo_name, f_path):
        diff1 = request.GET.get('diff1', '')
        diff2 = request.GET.get('diff2', '')

        nodes = []
        unknown_commits = []
        for commit in [diff1, diff2]:
            try:
                nodes.append(self._get_file_node(commit, f_path))
            except (RepositoryError, NodeError):
                log.exception('%(commit)s does not exist' % {'commit': commit})
                unknown_commits.append(commit)
                h.flash(h.literal(
                    _('Commit %(commit)s does not exist.') % {'commit': commit}
                    ), category='error')

        if unknown_commits:
            return redirect(url('files_home', repo_name=c.repo_name,
                                f_path=f_path))

        if all(isinstance(node.commit, EmptyCommit) for node in nodes):
            raise HTTPNotFound

        node1, node2 = nodes

        f_gitdiff = diffs.get_gitdiff(node1, node2, ignore_whitespace=False)
        diff_processor = diffs.DiffProcessor(f_gitdiff, format='gitdiff')
        diff_data = diff_processor.prepare()

        if not diff_data or diff_data[0]['raw_diff'] == '':
            h.flash(h.literal(_('%(file_path)s has not changed '
                                'between %(commit_1)s and %(commit_2)s.') % {
                                    'file_path': f_path,
                                    'commit_1': node1.commit.id,
                                    'commit_2': node2.commit.id
                                }), category='error')
            return redirect(url('files_home', repo_name=c.repo_name,
                                f_path=f_path))

        c.diff_data = diff_data[0]
        c.FID = h.FID(diff2, node2.path)
        # cleanup some unneeded data
        del c.diff_data['raw_diff']
        del c.diff_data['chunks']

        c.node1 = node1
        c.commit_1 = node1.commit
        c.node2 = node2
        c.commit_2 = node2.commit

        return render('files/diff_2way.html')

    def _get_file_node(self, commit_id, f_path):
        if commit_id not in ['', None, 'None', '0' * 12, '0' * 40]:
            commit = c.rhodecode_repo.get_commit(commit_id=commit_id)
            try:
                node = commit.get_node(f_path)
                if node.is_dir():
                    raise NodeError('%s path is a %s not a file'
                                    % (node, type(node)))
            except NodeDoesNotExistError:
                commit = EmptyCommit(
                    commit_id=commit_id,
                    idx=commit.idx,
                    repo=commit.repository,
                    alias=commit.repository.alias,
                    message=commit.message,
                    author=commit.author,
                    date=commit.date)
                node = FileNode(f_path, '', commit=commit)
        else:
            commit = EmptyCommit(
                repo=c.rhodecode_repo,
                alias=c.rhodecode_repo.alias)
            node = FileNode(f_path, '', commit=commit)
        return node

    def _get_node_history(self, commit, f_path, commits=None):
        """
        get commit history for given node

        :param commit: commit to calculate history
        :param f_path: path for node to calculate history for
        :param commits: if passed don't calculate history and take
            commits defined in this list
        """
        # calculate history based on tip
        tip = c.rhodecode_repo.get_commit()
        if commits is None:
            pre_load = ["author", "branch"]
            try:
                commits = tip.get_file_history(f_path, pre_load=pre_load)
            except (NodeDoesNotExistError, CommitError):
                # this node is not present at tip!
                commits = commit.get_file_history(f_path, pre_load=pre_load)

        history = []
        commits_group = ([], _("Changesets"))
        for commit in commits:
            branch = ' (%s)' % commit.branch if commit.branch else ''
            n_desc = 'r%s:%s%s' % (commit.idx, commit.short_id, branch)
            commits_group[0].append((commit.raw_id, n_desc,))
        history.append(commits_group)

        symbolic_reference = self._symbolic_reference

        if c.rhodecode_repo.alias == 'svn':
            adjusted_f_path = self._adjust_file_path_for_svn(
                f_path, c.rhodecode_repo)
            if adjusted_f_path != f_path:
                log.debug(
                    'Recognized svn tag or branch in file "%s", using svn '
                    'specific symbolic references', f_path)
                f_path = adjusted_f_path
                symbolic_reference = self._symbolic_reference_svn

        branches = self._create_references(
            c.rhodecode_repo.branches, symbolic_reference, f_path)
        branches_group = (branches, _("Branches"))

        tags = self._create_references(
            c.rhodecode_repo.tags, symbolic_reference, f_path)
        tags_group = (tags, _("Tags"))

        history.append(branches_group)
        history.append(tags_group)

        return history, commits

    def _adjust_file_path_for_svn(self, f_path, repo):
        """
        Computes the relative path of `f_path`.

        This is mainly based on prefix matching of the recognized tags and
        branches in the underlying repository.
        """
        tags_and_branches = itertools.chain(
            repo.branches.iterkeys(),
            repo.tags.iterkeys())
        tags_and_branches = sorted(tags_and_branches, key=len, reverse=True)

        for name in tags_and_branches:
            if f_path.startswith(name + '/'):
                f_path = vcspath.relpath(f_path, name)
                break
        return f_path

    def _create_references(
            self, branches_or_tags, symbolic_reference, f_path):
        items = []
        for name, commit_id in branches_or_tags.items():
            sym_ref = symbolic_reference(commit_id, name, f_path)
            items.append((sym_ref, name))
        return items

    def _symbolic_reference(self, commit_id, name, f_path):
        return commit_id

    def _symbolic_reference_svn(self, commit_id, name, f_path):
        new_f_path = vcspath.join(name, f_path)
        return u'%s@%s' % (new_f_path, commit_id)

    @LoginRequired()
    @XHRRequired()
    @HasRepoPermissionAnyDecorator(
        'repository.read', 'repository.write', 'repository.admin')
    @jsonify
    def nodelist(self, repo_name, revision, f_path):
        commit = self.__get_commit_or_redirect(revision, repo_name)

        metadata = self._get_nodelist_at_commit(
            repo_name, commit.raw_id, f_path)
        return {'nodes': metadata}

    @LoginRequired()
    @XHRRequired()
    @HasRepoPermissionAnyDecorator(
        'repository.read', 'repository.write', 'repository.admin')
    def nodetree_full(self, repo_name, commit_id, f_path):
        """
        Returns rendered html of file tree that contains commit date,
        author, revision for the specified combination of
        repo, commit_id and file path

        :param repo_name: name of the repository
        :param commit_id: commit_id of file tree
        :param f_path: file path of the requested directory
        """

        commit = self.__get_commit_or_redirect(commit_id, repo_name)
        try:
            dir_node = commit.get_node(f_path)
        except RepositoryError as e:
            return 'error {}'.format(safe_str(e))

        if dir_node.is_file():
            return ''

        c.file = dir_node
        c.commit = commit

        # using force=True here, make a little trick. We flush the cache and
        # compute it using the same key as without full_load, so the fully
        # loaded cached tree is now returned instead of partial
        return self._get_tree_at_commit(
            repo_name, commit.raw_id, dir_node.path, full_load=True,
            force=True)
