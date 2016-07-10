# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016  RhodeCode GmbH
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

import colander
import logging
import pylons

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.renderers import render
from pyramid.response import Response

from rhodecode.lib import auth
from rhodecode.lib.auth import LoginRequired, HasPermissionAllDecorator
from rhodecode.model.db import Repository, Session, Integration
from rhodecode.model.scm import ScmModel
from rhodecode.model.integration import IntegrationModel
from rhodecode.admin.navigation import navigation_list
from rhodecode.translation import _
from rhodecode.integrations import integration_type_registry

log = logging.getLogger(__name__)


class IntegrationSettingsViewBase(object):
    """ Base Integration settings view used by both repo / global settings """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._load_general_context()

        if not self.perm_check(request.user):
            raise HTTPForbidden()

    def _load_general_context(self):
        """
        This avoids boilerplate for repo/global+list/edit+views/templates
        by doing all possible contexts at the same time however it should
        be split up into separate functions once more "contexts" exist
        """

        self.IntegrationType = None
        self.repo = None
        self.integration = None
        self.integrations = {}

        request = self.request

        if 'repo_name' in request.matchdict:  # we're in a repo context
            repo_name = request.matchdict['repo_name']
            self.repo = Repository.get_by_repo_name(repo_name)

        if 'integration' in request.matchdict:  # we're in integration context
            integration_type = request.matchdict['integration']
            self.IntegrationType = integration_type_registry[integration_type]

        if 'integration_id' in request.matchdict:  # single integration context
            integration_id = request.matchdict['integration_id']
            self.integration = Integration.get(integration_id)
        else:                                      # list integrations context
            for integration in IntegrationModel().get_integrations(self.repo):
                self.integrations.setdefault(integration.integration_type, []
                    ).append(integration)

        self.settings = self.integration and self.integration.settings or {}

    def _template_c_context(self):
        # TODO: dan: this is a stopgap in order to inherit from current pylons
        # based admin/repo settings templates - this should be removed entirely
        # after port to pyramid

        c = pylons.tmpl_context
        c.active = 'integrations'
        c.rhodecode_user = self.request.user
        c.repo = self.repo
        c.repo_name = self.repo and self.repo.repo_name or None
        if self.repo:
            c.repo_info = self.repo
            c.rhodecode_db_repo = self.repo
            c.repository_pull_requests = ScmModel().get_pull_requests(self.repo)
        else:
            c.navlist = navigation_list(self.request)

        return c

    def _form_schema(self):
        return self.IntegrationType.settings_schema()

    def settings_get(self, defaults=None, errors=None):
        """
        View that displays the plugin settings as a form.
        """
        defaults = defaults or {}
        errors = errors or {}

        schema = self._form_schema()

        if not defaults:
            if self.integration:
                defaults['enabled'] = self.integration.enabled
                defaults['name'] = self.integration.name
            else:
                if self.repo:
                    scope = self.repo.repo_name
                else:
                    scope = _('Global')

                defaults['name'] = '{} {} integration'.format(scope,
                    self.IntegrationType.display_name)
                defaults['enabled'] = True

        for node in schema:
            setting = self.settings.get(node.name)
            if setting is not None:
                defaults.setdefault(node.name, setting)
            else:
                if node.default:
                    defaults.setdefault(node.name, node.default)

        template_context = {
            'defaults': defaults,
            'errors': errors,
            'schema': schema,
            'current_IntegrationType': self.IntegrationType,
            'integration': self.integration,
            'settings': self.settings,
            'resource': self.context,
            'c': self._template_c_context(),
        }

        return template_context

    @auth.CSRFRequired()
    def settings_post(self):
        """
        View that validates and stores the plugin settings.
        """
        if self.request.params.get('delete'):
            Session().delete(self.integration)
            Session().commit()
            self.request.session.flash(
                _('Integration {integration_name} deleted successfully.').format(
                    integration_name=self.integration.name),
                queue='success')
            if self.repo:
                redirect_to = self.request.route_url(
                    'repo_integrations_home', repo_name=self.repo.repo_name)
            else:
                redirect_to = self.request.route_url('global_integrations_home')
            raise HTTPFound(redirect_to)

        schema = self._form_schema()

        params = {}
        for node in schema.children:
            if type(node.typ) in (colander.Set, colander.List):
                val = self.request.params.getall(node.name)
            else:
                val = self.request.params.get(node.name)
            if val:
                params[node.name] = val

        try:
            valid_data = schema.deserialize(params)
        except colander.Invalid, e:
            # Display error message and display form again.
            self.request.session.flash(
                _('Errors exist when saving plugin settings. '
                  'Please check the form inputs.'),
                queue='error')
            return self.settings_get(errors=e.asdict(), defaults=params)

        if not self.integration:
            self.integration = Integration(
                integration_type=self.IntegrationType.key)
            if self.repo:
                self.integration.repo = self.repo
            Session.add(self.integration)

        self.integration.enabled = valid_data.pop('enabled', False)
        self.integration.name = valid_data.pop('name')
        self.integration.settings = valid_data

        Session.commit()

        # Display success message and redirect.
        self.request.session.flash(
            _('Integration {integration_name} updated successfully.').format(
                integration_name=self.IntegrationType.display_name,
                queue='success'))
        if self.repo:
            redirect_to = self.request.route_url(
                'repo_integrations_edit', repo_name=self.repo.repo_name,
                integration=self.integration.integration_type,
                integration_id=self.integration.integration_id)
        else:
            redirect_to = self.request.route_url(
                'global_integrations_edit',
                integration=self.integration.integration_type,
                integration_id=self.integration.integration_id)

        return HTTPFound(redirect_to)

    def index(self):
        current_integrations = self.integrations
        if self.IntegrationType:
            current_integrations = {
                self.IntegrationType.key: self.integrations.get(
                    self.IntegrationType.key, [])
            }

        template_context = {
            'current_IntegrationType': self.IntegrationType,
            'current_integrations': current_integrations,
            'current_integration': 'none',
            'available_integrations': integration_type_registry,
            'c': self._template_c_context()
        }

        if self.repo:
            html = render('rhodecode:templates/admin/integrations/list.html',
                          template_context,
                          request=self.request)
        else:
            html = render('rhodecode:templates/admin/integrations/list.html',
                          template_context,
                          request=self.request)

        return Response(html)


class GlobalIntegrationsView(IntegrationSettingsViewBase):
    def perm_check(self, user):
        return auth.HasPermissionAll('hg.admin').check_permissions(user=user)


class RepoIntegrationsView(IntegrationSettingsViewBase):
    def perm_check(self, user):
        return auth.HasRepoPermissionAll('repository.admin'
            )(repo_name=self.repo.repo_name, user=user)
