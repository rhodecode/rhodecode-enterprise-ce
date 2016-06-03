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
Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/

IMPORTANT: if you change any routing here, make sure to take a look at lib/base.py
and _route_name variable which uses some of stored naming here to do redirects.
"""
import os
import re
from routes import Mapper

from rhodecode.config import routing_links

# prefix for non repository related links needs to be prefixed with `/`
ADMIN_PREFIX = '/_admin'

# Default requirements for URL parts
URL_NAME_REQUIREMENTS = {
    # group name can have a slash in them, but they must not end with a slash
    'group_name': r'.*?[^/]',
    # repo names can have a slash in them, but they must not end with a slash
    'repo_name': r'.*?[^/]',
    # file path eats up everything at the end
    'f_path': r'.*',
    # reference types
    'source_ref_type': '(branch|book|tag|rev|\%\(source_ref_type\)s)',
    'target_ref_type': '(branch|book|tag|rev|\%\(target_ref_type\)s)',
}


class JSRoutesMapper(Mapper):
    """
    Wrapper for routes.Mapper to make pyroutes compatible url definitions
    """
    _named_route_regex = re.compile(r'^[a-z-_0-9A-Z]+$')
    _argument_prog = re.compile('\{(.*?)\}|:\((.*)\)')
    def __init__(self, *args, **kw):
        super(JSRoutesMapper, self).__init__(*args, **kw)
        self._jsroutes = []

    def connect(self, *args, **kw):
        """
        Wrapper for connect to take an extra argument jsroute=True

        :param jsroute: boolean, if True will add the route to the pyroutes list
        """
        if kw.pop('jsroute', False):
            if not self._named_route_regex.match(args[0]):
                # import pdb;pdb.set_trace()
                raise Exception('only named routes can be added to pyroutes')
            self._jsroutes.append(args[0])

        super(JSRoutesMapper, self).connect(*args, **kw)

    def _extract_route_information(self, route):
        """
        Convert a route into tuple(name, path, args), eg:
            ('user_profile', '/profile/%(username)s', ['username'])
        """
        routepath = route.routepath
        def replace(matchobj):
            if matchobj.group(1):
                return "%%(%s)s" % matchobj.group(1).split(':')[0]
            else:
                return "%%(%s)s" % matchobj.group(2)

        routepath = self._argument_prog.sub(replace, routepath)
        return (
            route.name,
            routepath,
            [(arg[0].split(':')[0] if arg[0] != '' else arg[1])
              for arg in self._argument_prog.findall(route.routepath)]
        )

    def jsroutes(self):
        """
        Return a list of pyroutes.js compatible routes
        """
        for route_name in self._jsroutes:
            yield self._extract_route_information(self._routenames[route_name])


def make_map(config):
    """Create, configure and return the routes Mapper"""
    rmap = JSRoutesMapper(directory=config['pylons.paths']['controllers'],
                  always_scan=config['debug'])
    rmap.minimization = False
    rmap.explicit = False

    from rhodecode.lib.utils2 import str2bool
    from rhodecode.model import repo, repo_group

    def check_repo(environ, match_dict):
        """
        check for valid repository for proper 404 handling

        :param environ:
        :param match_dict:
        """
        repo_name = match_dict.get('repo_name')

        if match_dict.get('f_path'):
            # fix for multiple initial slashes that causes errors
            match_dict['f_path'] = match_dict['f_path'].lstrip('/')
        repo_model = repo.RepoModel()
        by_name_match = repo_model.get_by_repo_name(repo_name)
        # if we match quickly from database, short circuit the operation,
        # and validate repo based on the type.
        if by_name_match:
            return True

        by_id_match = repo_model.get_repo_by_id(repo_name)
        if by_id_match:
            repo_name = by_id_match.repo_name
            match_dict['repo_name'] = repo_name
            return True

        return False

    def check_group(environ, match_dict):
        """
        check for valid repository group path for proper 404 handling

        :param environ:
        :param match_dict:
        """
        repo_group_name = match_dict.get('group_name')
        repo_group_model = repo_group.RepoGroupModel()
        by_name_match = repo_group_model.get_by_group_name(repo_group_name)
        if by_name_match:
            return True

        return False

    def check_user_group(environ, match_dict):
        """
        check for valid user group for proper 404 handling

        :param environ:
        :param match_dict:
        """
        return True

    def check_int(environ, match_dict):
        return match_dict.get('id').isdigit()

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    rmap.connect('/error/{action}', controller='error')
    rmap.connect('/error/{action}/{id}', controller='error')

    #==========================================================================
    # CUSTOM ROUTES HERE
    #==========================================================================

    # MAIN PAGE
    rmap.connect('home', '/', controller='home', action='index', jsroute=True)
    rmap.connect('goto_switcher_data', '/_goto_data', controller='home',
                 action='goto_switcher_data')
    rmap.connect('repo_list_data', '/_repos', controller='home',
                 action='repo_list_data')

    rmap.connect('user_autocomplete_data', '/_users', controller='home',
                 action='user_autocomplete_data', jsroute=True)
    rmap.connect('user_group_autocomplete_data', '/_user_groups', controller='home',
                 action='user_group_autocomplete_data')

    rmap.connect(
        'user_profile', '/_profiles/{username}', controller='users',
        action='user_profile')

    # TODO: johbo: Static links, to be replaced by our redirection mechanism
    rmap.connect('rst_help',
                 'http://docutils.sourceforge.net/docs/user/rst/quickref.html',
                 _static=True)
    rmap.connect('markdown_help',
                 'http://daringfireball.net/projects/markdown/syntax',
                 _static=True)
    rmap.connect('rhodecode_official', 'https://rhodecode.com', _static=True)
    rmap.connect('rhodecode_support', 'https://rhodecode.com/help/', _static=True)
    rmap.connect('rhodecode_translations', 'https://rhodecode.com/translate/enterprise', _static=True)
    # TODO: anderson - making this a static link since redirect won't play
    # nice with POST requests
    rmap.connect('enterprise_license_convert_from_old',
                 'https://rhodecode.com/u/license-upgrade',
                 _static=True)

    routing_links.connect_redirection_links(rmap)

    rmap.connect('ping', '%s/ping' % (ADMIN_PREFIX,), controller='home', action='ping')
    rmap.connect('error_test', '%s/error_test' % (ADMIN_PREFIX,), controller='home', action='error_test')

    # ADMIN REPOSITORY ROUTES
    with rmap.submapper(path_prefix=ADMIN_PREFIX,
                        controller='admin/repos') as m:
        m.connect('repos', '/repos',
                  action='create', conditions={'method': ['POST']})
        m.connect('repos', '/repos',
                  action='index', conditions={'method': ['GET']})
        m.connect('new_repo', '/create_repository', jsroute=True,
                  action='create_repository', conditions={'method': ['GET']})
        m.connect('/repos/{repo_name}',
                  action='update', conditions={'method': ['PUT'],
                                               'function': check_repo},
                  requirements=URL_NAME_REQUIREMENTS)
        m.connect('delete_repo', '/repos/{repo_name}',
                  action='delete', conditions={'method': ['DELETE']},
                  requirements=URL_NAME_REQUIREMENTS)
        m.connect('repo', '/repos/{repo_name}',
                  action='show', conditions={'method': ['GET'],
                                             'function': check_repo},
                  requirements=URL_NAME_REQUIREMENTS)

    # ADMIN REPOSITORY GROUPS ROUTES
    with rmap.submapper(path_prefix=ADMIN_PREFIX,
                        controller='admin/repo_groups') as m:
        m.connect('repo_groups', '/repo_groups',
                  action='create', conditions={'method': ['POST']})
        m.connect('repo_groups', '/repo_groups',
                  action='index', conditions={'method': ['GET']})
        m.connect('new_repo_group', '/repo_groups/new',
                  action='new', conditions={'method': ['GET']})
        m.connect('update_repo_group', '/repo_groups/{group_name}',
                  action='update', conditions={'method': ['PUT'],
                                               'function': check_group},
                  requirements=URL_NAME_REQUIREMENTS)

        # EXTRAS REPO GROUP ROUTES
        m.connect('edit_repo_group', '/repo_groups/{group_name}/edit',
                  action='edit',
                  conditions={'method': ['GET'], 'function': check_group},
                  requirements=URL_NAME_REQUIREMENTS)
        m.connect('edit_repo_group', '/repo_groups/{group_name}/edit',
                  action='edit',
                  conditions={'method': ['PUT'], 'function': check_group},
                  requirements=URL_NAME_REQUIREMENTS)

        m.connect('edit_repo_group_advanced', '/repo_groups/{group_name}/edit/advanced',
                  action='edit_repo_group_advanced',
                  conditions={'method': ['GET'], 'function': check_group},
                  requirements=URL_NAME_REQUIREMENTS)
        m.connect('edit_repo_group_advanced', '/repo_groups/{group_name}/edit/advanced',
                  action='edit_repo_group_advanced',
                  conditions={'method': ['PUT'], 'function': check_group},
                  requirements=URL_NAME_REQUIREMENTS)

        m.connect('edit_repo_group_perms', '/repo_groups/{group_name}/edit/permissions',
                  action='edit_repo_group_perms',
                  conditions={'method': ['GET'], 'function': check_group},
                  requirements=URL_NAME_REQUIREMENTS)
        m.connect('edit_repo_group_perms', '/repo_groups/{group_name}/edit/permissions',
                  action='update_perms',
                  conditions={'method': ['PUT'], 'function': check_group},
                  requirements=URL_NAME_REQUIREMENTS)

        m.connect('delete_repo_group', '/repo_groups/{group_name}',
                  action='delete', conditions={'method': ['DELETE'],
                                               'function': check_group},
                  requirements=URL_NAME_REQUIREMENTS)

    # ADMIN USER ROUTES
    with rmap.submapper(path_prefix=ADMIN_PREFIX,
                        controller='admin/users') as m:
        m.connect('users', '/users',
                  action='create', conditions={'method': ['POST']})
        m.connect('users', '/users',
                  action='index', conditions={'method': ['GET']})
        m.connect('new_user', '/users/new',
                  action='new', conditions={'method': ['GET']})
        m.connect('update_user', '/users/{user_id}',
                  action='update', conditions={'method': ['PUT']})
        m.connect('delete_user', '/users/{user_id}',
                  action='delete', conditions={'method': ['DELETE']})
        m.connect('edit_user', '/users/{user_id}/edit',
                  action='edit', conditions={'method': ['GET']})
        m.connect('user', '/users/{user_id}',
                  action='show', conditions={'method': ['GET']})
        m.connect('force_password_reset_user', '/users/{user_id}/password_reset',
                  action='reset_password', conditions={'method': ['POST']})
        m.connect('create_personal_repo_group', '/users/{user_id}/create_repo_group',
                  action='create_personal_repo_group', conditions={'method': ['POST']})

        # EXTRAS USER ROUTES
        m.connect('edit_user_advanced', '/users/{user_id}/edit/advanced',
                  action='edit_advanced', conditions={'method': ['GET']})
        m.connect('edit_user_advanced', '/users/{user_id}/edit/advanced',
                  action='update_advanced', conditions={'method': ['PUT']})

        m.connect('edit_user_auth_tokens', '/users/{user_id}/edit/auth_tokens',
                  action='edit_auth_tokens', conditions={'method': ['GET']})
        m.connect('edit_user_auth_tokens', '/users/{user_id}/edit/auth_tokens',
                  action='add_auth_token', conditions={'method': ['PUT']})
        m.connect('edit_user_auth_tokens', '/users/{user_id}/edit/auth_tokens',
                  action='delete_auth_token', conditions={'method': ['DELETE']})

        m.connect('edit_user_global_perms', '/users/{user_id}/edit/global_permissions',
                  action='edit_global_perms', conditions={'method': ['GET']})
        m.connect('edit_user_global_perms', '/users/{user_id}/edit/global_permissions',
                  action='update_global_perms', conditions={'method': ['PUT']})

        m.connect('edit_user_perms_summary', '/users/{user_id}/edit/permissions_summary',
                  action='edit_perms_summary', conditions={'method': ['GET']})

        m.connect('edit_user_emails', '/users/{user_id}/edit/emails',
                  action='edit_emails', conditions={'method': ['GET']})
        m.connect('edit_user_emails', '/users/{user_id}/edit/emails',
                  action='add_email', conditions={'method': ['PUT']})
        m.connect('edit_user_emails', '/users/{user_id}/edit/emails',
                  action='delete_email', conditions={'method': ['DELETE']})

        m.connect('edit_user_ips', '/users/{user_id}/edit/ips',
                  action='edit_ips', conditions={'method': ['GET']})
        m.connect('edit_user_ips', '/users/{user_id}/edit/ips',
                  action='add_ip', conditions={'method': ['PUT']})
        m.connect('edit_user_ips', '/users/{user_id}/edit/ips',
                  action='delete_ip', conditions={'method': ['DELETE']})

    # ADMIN USER GROUPS REST ROUTES
    with rmap.submapper(path_prefix=ADMIN_PREFIX,
                        controller='admin/user_groups') as m:
        m.connect('users_groups', '/user_groups',
                  action='create', conditions={'method': ['POST']})
        m.connect('users_groups', '/user_groups',
                  action='index', conditions={'method': ['GET']})
        m.connect('new_users_group', '/user_groups/new',
                  action='new', conditions={'method': ['GET']})
        m.connect('update_users_group', '/user_groups/{user_group_id}',
                  action='update', conditions={'method': ['PUT']})
        m.connect('delete_users_group', '/user_groups/{user_group_id}',
                  action='delete', conditions={'method': ['DELETE']})
        m.connect('edit_users_group', '/user_groups/{user_group_id}/edit',
                  action='edit', conditions={'method': ['GET']},
                  function=check_user_group)

        # EXTRAS USER GROUP ROUTES
        m.connect('edit_user_group_global_perms',
                  '/user_groups/{user_group_id}/edit/global_permissions',
                  action='edit_global_perms', conditions={'method': ['GET']})
        m.connect('edit_user_group_global_perms',
                  '/user_groups/{user_group_id}/edit/global_permissions',
                  action='update_global_perms', conditions={'method': ['PUT']})
        m.connect('edit_user_group_perms_summary',
                  '/user_groups/{user_group_id}/edit/permissions_summary',
                  action='edit_perms_summary', conditions={'method': ['GET']})

        m.connect('edit_user_group_perms',
                  '/user_groups/{user_group_id}/edit/permissions',
                  action='edit_perms', conditions={'method': ['GET']})
        m.connect('edit_user_group_perms',
                  '/user_groups/{user_group_id}/edit/permissions',
                  action='update_perms', conditions={'method': ['PUT']})

        m.connect('edit_user_group_advanced',
                  '/user_groups/{user_group_id}/edit/advanced',
                  action='edit_advanced', conditions={'method': ['GET']})

        m.connect('edit_user_group_members',
                  '/user_groups/{user_group_id}/edit/members', jsroute=True,
                  action='edit_members', conditions={'method': ['GET']})

    # ADMIN PERMISSIONS ROUTES
    with rmap.submapper(path_prefix=ADMIN_PREFIX,
                        controller='admin/permissions') as m:
        m.connect('admin_permissions_application', '/permissions/application',
                  action='permission_application_update', conditions={'method': ['POST']})
        m.connect('admin_permissions_application', '/permissions/application',
                  action='permission_application', conditions={'method': ['GET']})

        m.connect('admin_permissions_global', '/permissions/global',
                  action='permission_global_update', conditions={'method': ['POST']})
        m.connect('admin_permissions_global', '/permissions/global',
                  action='permission_global', conditions={'method': ['GET']})

        m.connect('admin_permissions_object', '/permissions/object',
                  action='permission_objects_update', conditions={'method': ['POST']})
        m.connect('admin_permissions_object', '/permissions/object',
                  action='permission_objects', conditions={'method': ['GET']})

        m.connect('admin_permissions_ips', '/permissions/ips',
                  action='permission_ips', conditions={'method': ['POST']})
        m.connect('admin_permissions_ips', '/permissions/ips',
                  action='permission_ips', conditions={'method': ['GET']})

        m.connect('admin_permissions_overview', '/permissions/overview',
                  action='permission_perms', conditions={'method': ['GET']})

    # ADMIN DEFAULTS REST ROUTES
    with rmap.submapper(path_prefix=ADMIN_PREFIX,
                        controller='admin/defaults') as m:
        m.connect('admin_defaults_repositories', '/defaults/repositories',
                  action='update_repository_defaults', conditions={'method': ['POST']})
        m.connect('admin_defaults_repositories', '/defaults/repositories',
                  action='index', conditions={'method': ['GET']})

    # ADMIN DEBUG STYLE ROUTES
    if str2bool(config.get('debug_style')):
        with rmap.submapper(path_prefix=ADMIN_PREFIX + '/debug_style',
                            controller='debug_style') as m:
            m.connect('debug_style_home', '',
                      action='index', conditions={'method': ['GET']})
            m.connect('debug_style_template', '/t/{t_path}',
                      action='template', conditions={'method': ['GET']})

    # ADMIN SETTINGS ROUTES
    with rmap.submapper(path_prefix=ADMIN_PREFIX,
                        controller='admin/settings') as m:

        # default
        m.connect('admin_settings', '/settings',
                  action='settings_global_update',
                  conditions={'method': ['POST']})
        m.connect('admin_settings', '/settings',
                  action='settings_global', conditions={'method': ['GET']})

        m.connect('admin_settings_vcs', '/settings/vcs',
                  action='settings_vcs_update',
                  conditions={'method': ['POST']})
        m.connect('admin_settings_vcs', '/settings/vcs',
                  action='settings_vcs',
                  conditions={'method': ['GET']})
        m.connect('admin_settings_vcs', '/settings/vcs',
                  action='delete_svn_pattern',
                  conditions={'method': ['DELETE']})

        m.connect('admin_settings_mapping', '/settings/mapping',
                  action='settings_mapping_update',
                  conditions={'method': ['POST']})
        m.connect('admin_settings_mapping', '/settings/mapping',
                  action='settings_mapping', conditions={'method': ['GET']})

        m.connect('admin_settings_global', '/settings/global',
                  action='settings_global_update',
                  conditions={'method': ['POST']})
        m.connect('admin_settings_global', '/settings/global',
                  action='settings_global', conditions={'method': ['GET']})

        m.connect('admin_settings_visual', '/settings/visual',
                  action='settings_visual_update',
                  conditions={'method': ['POST']})
        m.connect('admin_settings_visual', '/settings/visual',
                  action='settings_visual', conditions={'method': ['GET']})

        m.connect('admin_settings_issuetracker',
                  '/settings/issue-tracker', action='settings_issuetracker',
                  conditions={'method': ['GET']})
        m.connect('admin_settings_issuetracker_save',
                  '/settings/issue-tracker/save',
                  action='settings_issuetracker_save',
                  conditions={'method': ['POST']})
        m.connect('admin_issuetracker_test', '/settings/issue-tracker/test',
                  action='settings_issuetracker_test',
                  conditions={'method': ['POST']})
        m.connect('admin_issuetracker_delete',
                  '/settings/issue-tracker/delete',
                  action='settings_issuetracker_delete',
                  conditions={'method': ['DELETE']})

        m.connect('admin_settings_email', '/settings/email',
                  action='settings_email_update',
                  conditions={'method': ['POST']})
        m.connect('admin_settings_email', '/settings/email',
                  action='settings_email', conditions={'method': ['GET']})

        m.connect('admin_settings_hooks', '/settings/hooks',
                  action='settings_hooks_update',
                  conditions={'method': ['POST', 'DELETE']})
        m.connect('admin_settings_hooks', '/settings/hooks',
                  action='settings_hooks', conditions={'method': ['GET']})

        m.connect('admin_settings_search', '/settings/search',
                  action='settings_search', conditions={'method': ['GET']})

        m.connect('admin_settings_system', '/settings/system',
                  action='settings_system', conditions={'method': ['GET']})

        m.connect('admin_settings_system_update', '/settings/system/updates',
                  action='settings_system_update', conditions={'method': ['GET']})

        m.connect('admin_settings_supervisor', '/settings/supervisor',
                  action='settings_supervisor', conditions={'method': ['GET']})
        m.connect('admin_settings_supervisor_log', '/settings/supervisor/{procid}/log',
                  action='settings_supervisor_log', conditions={'method': ['GET']})

        m.connect('admin_settings_labs', '/settings/labs',
                  action='settings_labs_update',
                  conditions={'method': ['POST']})
        m.connect('admin_settings_labs', '/settings/labs',
                  action='settings_labs', conditions={'method': ['GET']})

        m.connect('admin_settings_open_source', '/settings/open_source',
                  action='settings_open_source',
                  conditions={'method': ['GET']})

    # ADMIN MY ACCOUNT
    with rmap.submapper(path_prefix=ADMIN_PREFIX,
                        controller='admin/my_account') as m:

        m.connect('my_account', '/my_account',
                  action='my_account', conditions={'method': ['GET']})
        m.connect('my_account_edit', '/my_account/edit',
                  action='my_account_edit', conditions={'method': ['GET']})
        m.connect('my_account', '/my_account',
                  action='my_account_update', conditions={'method': ['POST']})

        m.connect('my_account_password', '/my_account/password',
                  action='my_account_password', conditions={'method': ['GET']})
        m.connect('my_account_password', '/my_account/password',
                  action='my_account_password_update', conditions={'method': ['POST']})

        m.connect('my_account_repos', '/my_account/repos',
                  action='my_account_repos', conditions={'method': ['GET']})

        m.connect('my_account_watched', '/my_account/watched',
                  action='my_account_watched', conditions={'method': ['GET']})

        m.connect('my_account_pullrequests', '/my_account/pull_requests',
                  action='my_account_pullrequests', conditions={'method': ['GET']})

        m.connect('my_account_perms', '/my_account/perms',
                  action='my_account_perms', conditions={'method': ['GET']})

        m.connect('my_account_emails', '/my_account/emails',
                  action='my_account_emails', conditions={'method': ['GET']})
        m.connect('my_account_emails', '/my_account/emails',
                  action='my_account_emails_add', conditions={'method': ['POST']})
        m.connect('my_account_emails', '/my_account/emails',
                  action='my_account_emails_delete', conditions={'method': ['DELETE']})

        m.connect('my_account_auth_tokens', '/my_account/auth_tokens',
                  action='my_account_auth_tokens', conditions={'method': ['GET']})
        m.connect('my_account_auth_tokens', '/my_account/auth_tokens',
                  action='my_account_auth_tokens_add', conditions={'method': ['POST']})
        m.connect('my_account_auth_tokens', '/my_account/auth_tokens',
                  action='my_account_auth_tokens_delete', conditions={'method': ['DELETE']})

    # NOTIFICATION REST ROUTES
    with rmap.submapper(path_prefix=ADMIN_PREFIX,
                        controller='admin/notifications') as m:
        m.connect('notifications', '/notifications',
                  action='index', conditions={'method': ['GET']})
        m.connect('notifications_mark_all_read', '/notifications/mark_all_read',
                  action='mark_all_read', conditions={'method': ['POST']})

        m.connect('/notifications/{notification_id}',
                  action='update', conditions={'method': ['PUT']})
        m.connect('/notifications/{notification_id}',
                  action='delete', conditions={'method': ['DELETE']})
        m.connect('notification', '/notifications/{notification_id}',
                  action='show', conditions={'method': ['GET']})

    # ADMIN GIST
    with rmap.submapper(path_prefix=ADMIN_PREFIX,
                        controller='admin/gists') as m:
        m.connect('gists', '/gists',
                  action='create', conditions={'method': ['POST']})
        m.connect('gists', '/gists', jsroute=True,
                  action='index', conditions={'method': ['GET']})
        m.connect('new_gist', '/gists/new', jsroute=True,
                  action='new', conditions={'method': ['GET']})

        m.connect('/gists/{gist_id}',
                  action='delete', conditions={'method': ['DELETE']})
        m.connect('edit_gist', '/gists/{gist_id}/edit',
                  action='edit_form', conditions={'method': ['GET']})
        m.connect('edit_gist', '/gists/{gist_id}/edit',
                  action='edit', conditions={'method': ['POST']})
        m.connect(
            'edit_gist_check_revision', '/gists/{gist_id}/edit/check_revision',
            action='check_revision', conditions={'method': ['GET']})

        m.connect('gist', '/gists/{gist_id}',
                  action='show', conditions={'method': ['GET']})
        m.connect('gist_rev', '/gists/{gist_id}/{revision}',
                  revision='tip',
                  action='show', conditions={'method': ['GET']})
        m.connect('formatted_gist', '/gists/{gist_id}/{revision}/{format}',
                  revision='tip',
                  action='show', conditions={'method': ['GET']})
        m.connect('formatted_gist_file', '/gists/{gist_id}/{revision}/{format}/{f_path}',
                  revision='tip',
                  action='show', conditions={'method': ['GET']},
                  requirements=URL_NAME_REQUIREMENTS)

    # ADMIN MAIN PAGES
    with rmap.submapper(path_prefix=ADMIN_PREFIX,
                        controller='admin/admin') as m:
        m.connect('admin_home', '', action='index')
        m.connect('admin_add_repo', '/add_repo/{new_repo:[a-z0-9\. _-]*}',
                  action='add_repo')
        m.connect(
            'pull_requests_global_0', '/pull_requests/{pull_request_id:[0-9]+}',
            action='pull_requests')
        m.connect(
            'pull_requests_global', '/pull-requests/{pull_request_id:[0-9]+}',
            action='pull_requests')


    # USER JOURNAL
    rmap.connect('journal', '%s/journal' % (ADMIN_PREFIX,),
                 controller='journal', action='index')
    rmap.connect('journal_rss', '%s/journal/rss' % (ADMIN_PREFIX,),
                 controller='journal', action='journal_rss')
    rmap.connect('journal_atom', '%s/journal/atom' % (ADMIN_PREFIX,),
                 controller='journal', action='journal_atom')

    rmap.connect('public_journal', '%s/public_journal' % (ADMIN_PREFIX,),
                 controller='journal', action='public_journal')

    rmap.connect('public_journal_rss', '%s/public_journal/rss' % (ADMIN_PREFIX,),
                 controller='journal', action='public_journal_rss')

    rmap.connect('public_journal_rss_old', '%s/public_journal_rss' % (ADMIN_PREFIX,),
                 controller='journal', action='public_journal_rss')

    rmap.connect('public_journal_atom',
                 '%s/public_journal/atom' % (ADMIN_PREFIX,), controller='journal',
                 action='public_journal_atom')

    rmap.connect('public_journal_atom_old',
                 '%s/public_journal_atom' % (ADMIN_PREFIX,), controller='journal',
                 action='public_journal_atom')

    rmap.connect('toggle_following', '%s/toggle_following' % (ADMIN_PREFIX,),
                 controller='journal', action='toggle_following', jsroute=True,
                 conditions={'method': ['POST']})

    # FULL TEXT SEARCH
    rmap.connect('search', '%s/search' % (ADMIN_PREFIX,),
                 controller='search')
    rmap.connect('search_repo_home', '/{repo_name}/search',
                 controller='search',
                 action='index',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    # FEEDS
    rmap.connect('rss_feed_home', '/{repo_name}/feed/rss',
                 controller='feed', action='rss',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('atom_feed_home', '/{repo_name}/feed/atom',
                 controller='feed', action='atom',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    #==========================================================================
    # REPOSITORY ROUTES
    #==========================================================================

    rmap.connect('repo_creating_home', '/{repo_name}/repo_creating',
                 controller='admin/repos', action='repo_creating',
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('repo_check_home', '/{repo_name}/crepo_check',
                 controller='admin/repos', action='repo_check',
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('repo_stats', '/{repo_name}/repo_stats/{commit_id}',
                 controller='summary', action='repo_stats',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('repo_refs_data', '/{repo_name}/refs-data',
                 controller='summary', action='repo_refs_data', jsroute=True,
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('repo_refs_changelog_data', '/{repo_name}/refs-data-changelog',
                 controller='summary', action='repo_refs_changelog_data',
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('changeset_home', '/{repo_name}/changeset/{revision}',
                 controller='changeset', revision='tip', jsroute=True,
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('changeset_children', '/{repo_name}/changeset_children/{revision}',
                 controller='changeset', revision='tip', action='changeset_children',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('changeset_parents', '/{repo_name}/changeset_parents/{revision}',
                 controller='changeset', revision='tip', action='changeset_parents',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    # repo edit options
    rmap.connect('edit_repo', '/{repo_name}/settings', jsroute=True,
                 controller='admin/repos', action='edit',
                 conditions={'method': ['GET'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('edit_repo_perms', '/{repo_name}/settings/permissions',
                 jsroute=True,
                 controller='admin/repos', action='edit_permissions',
                 conditions={'method': ['GET'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('edit_repo_perms_update', '/{repo_name}/settings/permissions',
                 controller='admin/repos', action='edit_permissions_update',
                 conditions={'method': ['PUT'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('edit_repo_fields', '/{repo_name}/settings/fields',
                 controller='admin/repos', action='edit_fields',
                 conditions={'method': ['GET'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('create_repo_fields', '/{repo_name}/settings/fields/new',
                 controller='admin/repos', action='create_repo_field',
                 conditions={'method': ['PUT'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('delete_repo_fields', '/{repo_name}/settings/fields/{field_id}',
                 controller='admin/repos', action='delete_repo_field',
                 conditions={'method': ['DELETE'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('edit_repo_advanced', '/{repo_name}/settings/advanced',
                 controller='admin/repos', action='edit_advanced',
                 conditions={'method': ['GET'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('edit_repo_advanced_locking', '/{repo_name}/settings/advanced/locking',
                 controller='admin/repos', action='edit_advanced_locking',
                 conditions={'method': ['PUT'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('toggle_locking', '/{repo_name}/settings/advanced/locking_toggle',
                 controller='admin/repos', action='toggle_locking',
                 conditions={'method': ['GET'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('edit_repo_advanced_journal', '/{repo_name}/settings/advanced/journal',
                 controller='admin/repos', action='edit_advanced_journal',
                 conditions={'method': ['PUT'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('edit_repo_advanced_fork', '/{repo_name}/settings/advanced/fork',
                 controller='admin/repos', action='edit_advanced_fork',
                 conditions={'method': ['PUT'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('edit_repo_caches', '/{repo_name}/settings/caches',
                 controller='admin/repos', action='edit_caches_form',
                 conditions={'method': ['GET'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('edit_repo_caches', '/{repo_name}/settings/caches',
                 controller='admin/repos', action='edit_caches',
                 conditions={'method': ['PUT'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('edit_repo_remote', '/{repo_name}/settings/remote',
                 controller='admin/repos', action='edit_remote_form',
                 conditions={'method': ['GET'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('edit_repo_remote', '/{repo_name}/settings/remote',
                 controller='admin/repos', action='edit_remote',
                 conditions={'method': ['PUT'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('edit_repo_statistics', '/{repo_name}/settings/statistics',
                 controller='admin/repos', action='edit_statistics_form',
                 conditions={'method': ['GET'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('edit_repo_statistics', '/{repo_name}/settings/statistics',
                 controller='admin/repos', action='edit_statistics',
                 conditions={'method': ['PUT'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('repo_settings_issuetracker',
                 '/{repo_name}/settings/issue-tracker',
                 controller='admin/repos', action='repo_issuetracker',
                 conditions={'method': ['GET'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('repo_issuetracker_test',
                 '/{repo_name}/settings/issue-tracker/test',
                 controller='admin/repos', action='repo_issuetracker_test',
                 conditions={'method': ['POST'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('repo_issuetracker_delete',
                 '/{repo_name}/settings/issue-tracker/delete',
                 controller='admin/repos', action='repo_issuetracker_delete',
                 conditions={'method': ['DELETE'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('repo_issuetracker_save',
                 '/{repo_name}/settings/issue-tracker/save',
                 controller='admin/repos', action='repo_issuetracker_save',
                 conditions={'method': ['POST'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('repo_vcs_settings', '/{repo_name}/settings/vcs',
                 controller='admin/repos', action='repo_settings_vcs_update',
                 conditions={'method': ['POST'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('repo_vcs_settings', '/{repo_name}/settings/vcs',
                 controller='admin/repos', action='repo_settings_vcs',
                 conditions={'method': ['GET'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)
    rmap.connect('repo_vcs_settings', '/{repo_name}/settings/vcs',
                 controller='admin/repos', action='repo_delete_svn_pattern',
                 conditions={'method': ['DELETE'], 'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    # still working url for backward compat.
    rmap.connect('raw_changeset_home_depraced',
                 '/{repo_name}/raw-changeset/{revision}',
                 controller='changeset', action='changeset_raw',
                 revision='tip', conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    # new URLs
    rmap.connect('changeset_raw_home',
                 '/{repo_name}/changeset-diff/{revision}',
                 controller='changeset', action='changeset_raw',
                 revision='tip', conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('changeset_patch_home',
                 '/{repo_name}/changeset-patch/{revision}',
                 controller='changeset', action='changeset_patch',
                 revision='tip', conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('changeset_download_home',
                 '/{repo_name}/changeset-download/{revision}',
                 controller='changeset', action='changeset_download',
                 revision='tip', conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('changeset_comment',
                 '/{repo_name}/changeset/{revision}/comment', jsroute=True,
                 controller='changeset', revision='tip', action='comment',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('changeset_comment_preview',
                 '/{repo_name}/changeset/comment/preview', jsroute=True,
                 controller='changeset', action='preview_comment',
                 conditions={'function': check_repo, 'method': ['POST']},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('changeset_comment_delete',
                 '/{repo_name}/changeset/comment/{comment_id}/delete',
                 controller='changeset', action='delete_comment',
                 conditions={'function': check_repo, 'method': ['DELETE']},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('changeset_info', '/changeset_info/{repo_name}/{revision}',
                 controller='changeset', action='changeset_info',
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('compare_home',
                 '/{repo_name}/compare',
                 controller='compare', action='index',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('compare_url',
                 '/{repo_name}/compare/{source_ref_type}@{source_ref:.*?}...{target_ref_type}@{target_ref:.*?}',
                 controller='compare', action='compare',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('pullrequest_home',
                 '/{repo_name}/pull-request/new', controller='pullrequests',
                 action='index', conditions={'function': check_repo,
                                             'method': ['GET']},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('pullrequest',
                 '/{repo_name}/pull-request/new', controller='pullrequests',
                 action='create', conditions={'function': check_repo,
                                              'method': ['POST']},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('pullrequest_repo_refs',
                 '/{repo_name}/pull-request/refs/{target_repo_name:.*?[^/]}',
                 controller='pullrequests',
                 action='get_repo_refs',
                 conditions={'function': check_repo, 'method': ['GET']},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('pullrequest_repo_destinations',
                 '/{repo_name}/pull-request/repo-destinations',
                 controller='pullrequests',
                 action='get_repo_destinations',
                 conditions={'function': check_repo, 'method': ['GET']},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('pullrequest_show',
                 '/{repo_name}/pull-request/{pull_request_id}',
                 controller='pullrequests',
                 action='show', conditions={'function': check_repo,
                                            'method': ['GET']},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('pullrequest_update',
                 '/{repo_name}/pull-request/{pull_request_id}',
                 controller='pullrequests',
                 action='update', conditions={'function': check_repo,
                                              'method': ['PUT']},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('pullrequest_merge',
                 '/{repo_name}/pull-request/{pull_request_id}',
                 controller='pullrequests',
                 action='merge', conditions={'function': check_repo,
                                             'method': ['POST']},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('pullrequest_delete',
                 '/{repo_name}/pull-request/{pull_request_id}',
                 controller='pullrequests',
                 action='delete', conditions={'function': check_repo,
                                              'method': ['DELETE']},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('pullrequest_show_all',
                 '/{repo_name}/pull-request',
                 controller='pullrequests',
                 action='show_all', conditions={'function': check_repo,
                                                'method': ['GET']},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('pullrequest_comment',
                 '/{repo_name}/pull-request-comment/{pull_request_id}',
                 controller='pullrequests',
                 action='comment', conditions={'function': check_repo,
                                               'method': ['POST']},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('pullrequest_comment_delete',
                 '/{repo_name}/pull-request-comment/{comment_id}/delete',
                 controller='pullrequests', action='delete_comment',
                 conditions={'function': check_repo, 'method': ['DELETE']},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('summary_home_explicit', '/{repo_name}/summary',
                 controller='summary', conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('branches_home', '/{repo_name}/branches',
                 controller='branches', conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('tags_home', '/{repo_name}/tags',
                 controller='tags', conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('bookmarks_home', '/{repo_name}/bookmarks',
                 controller='bookmarks', conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('changelog_home', '/{repo_name}/changelog', jsroute=True,
                 controller='changelog', conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('changelog_summary_home', '/{repo_name}/changelog_summary',
                 controller='changelog', action='changelog_summary',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('changelog_file_home',
                 '/{repo_name}/changelog/{revision}/{f_path}',
                 controller='changelog', f_path=None,
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('changelog_details', '/{repo_name}/changelog_details/{cs}',
                 controller='changelog', action='changelog_details',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_home',  '/{repo_name}/files/{revision}/{f_path}',
                 controller='files', revision='tip', f_path='',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('files_home_simple_catchrev',
                 '/{repo_name}/files/{revision}',
                 controller='files', revision='tip', f_path='',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_home_simple_catchall',
                 '/{repo_name}/files',
                 controller='files', revision='tip', f_path='',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_history_home',
                 '/{repo_name}/history/{revision}/{f_path}',
                 controller='files', action='history', revision='tip', f_path='',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('files_authors_home',
                 '/{repo_name}/authors/{revision}/{f_path}',
                 controller='files', action='authors', revision='tip', f_path='',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('files_diff_home', '/{repo_name}/diff/{f_path}',
                 controller='files', action='diff', f_path='',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_diff_2way_home',
                 '/{repo_name}/diff-2way/{f_path}',
                 controller='files', action='diff_2way', f_path='',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_rawfile_home',
                 '/{repo_name}/rawfile/{revision}/{f_path}',
                 controller='files', action='rawfile', revision='tip',
                 f_path='', conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_raw_home',
                 '/{repo_name}/raw/{revision}/{f_path}',
                 controller='files', action='raw', revision='tip', f_path='',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_render_home',
                 '/{repo_name}/render/{revision}/{f_path}',
                 controller='files', action='index', revision='tip', f_path='',
                 rendered=True, conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_annotate_home',
                 '/{repo_name}/annotate/{revision}/{f_path}',
                 controller='files', action='index', revision='tip',
                 f_path='', annotate=True, conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_edit',
                 '/{repo_name}/edit/{revision}/{f_path}',
                 controller='files', action='edit', revision='tip',
                 f_path='',
                 conditions={'function': check_repo, 'method': ['POST']},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_edit_home',
                 '/{repo_name}/edit/{revision}/{f_path}',
                 controller='files', action='edit_home', revision='tip',
                 f_path='', conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_add',
                 '/{repo_name}/add/{revision}/{f_path}',
                 controller='files', action='add', revision='tip',
                 f_path='',
                 conditions={'function': check_repo, 'method': ['POST']},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_add_home',
                 '/{repo_name}/add/{revision}/{f_path}',
                 controller='files', action='add_home', revision='tip',
                 f_path='', conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_delete',
                 '/{repo_name}/delete/{revision}/{f_path}',
                 controller='files', action='delete', revision='tip',
                 f_path='',
                 conditions={'function': check_repo, 'method': ['POST']},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_delete_home',
                 '/{repo_name}/delete/{revision}/{f_path}',
                 controller='files', action='delete_home', revision='tip',
                 f_path='', conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('files_archive_home', '/{repo_name}/archive/{fname}',
                 controller='files', action='archivefile',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('files_nodelist_home',
                 '/{repo_name}/nodelist/{revision}/{f_path}',
                 controller='files', action='nodelist',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('files_metadata_list_home',
                 '/{repo_name}/metadata_list/{revision}/{f_path}',
                 controller='files', action='metadata_list',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS, jsroute=True)

    rmap.connect('repo_fork_create_home', '/{repo_name}/fork',
                 controller='forks', action='fork_create',
                 conditions={'function': check_repo, 'method': ['POST']},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('repo_fork_home', '/{repo_name}/fork',
                 controller='forks', action='fork',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('repo_forks_home', '/{repo_name}/forks',
                 controller='forks', action='forks',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    rmap.connect('repo_followers_home', '/{repo_name}/followers',
                 controller='followers', action='followers',
                 conditions={'function': check_repo},
                 requirements=URL_NAME_REQUIREMENTS)

    # must be here for proper group/repo catching pattern
    _connect_with_slash(
        rmap, 'repo_group_home', '/{group_name}',
        controller='home', action='index_repo_group',
        conditions={'function': check_group},
        requirements=URL_NAME_REQUIREMENTS)

    # catch all, at the end
    _connect_with_slash(
        rmap, 'summary_home', '/{repo_name}', jsroute=True,
        controller='summary', action='index',
        conditions={'function': check_repo},
        requirements=URL_NAME_REQUIREMENTS)

    rmap.jsroutes()
    return rmap


def _connect_with_slash(mapper, name, path, *args, **kwargs):
    """
    Connect a route with an optional trailing slash in `path`.
    """
    mapper.connect(name + '_slash', path + '/', *args, **kwargs)
    mapper.connect(name, path, *args, **kwargs)
