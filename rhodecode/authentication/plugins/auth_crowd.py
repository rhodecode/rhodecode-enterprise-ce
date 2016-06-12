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

"""
RhodeCode authentication plugin for Atlassian CROWD
"""


import colander
import base64
import logging
import urllib2

from pylons.i18n.translation import lazy_ugettext as _
from sqlalchemy.ext.hybrid import hybrid_property

from rhodecode.authentication.base import RhodeCodeExternalAuthPlugin
from rhodecode.authentication.schema import AuthnPluginSettingsSchemaBase
from rhodecode.authentication.routes import AuthnPluginResourceBase
from rhodecode.lib.colander_utils import strip_whitespace
from rhodecode.lib.ext_json import json, formatted_json
from rhodecode.model.db import User

log = logging.getLogger(__name__)


def plugin_factory(plugin_id, *args, **kwds):
    """
    Factory function that is called during plugin discovery.
    It returns the plugin instance.
    """
    plugin = RhodeCodeAuthPlugin(plugin_id)
    return plugin


class CrowdAuthnResource(AuthnPluginResourceBase):
    pass


class CrowdSettingsSchema(AuthnPluginSettingsSchemaBase):
    host = colander.SchemaNode(
        colander.String(),
        default='127.0.0.1',
        description=_('The FQDN or IP of the Atlassian CROWD Server'),
        preparer=strip_whitespace,
        title=_('Host'),
        widget='string')
    port = colander.SchemaNode(
        colander.Int(),
        default=8095,
        description=_('The Port in use by the Atlassian CROWD Server'),
        preparer=strip_whitespace,
        title=_('Port'),
        validator=colander.Range(min=0, max=65536),
        widget='int')
    app_name = colander.SchemaNode(
        colander.String(),
        default='',
        description=_('The Application Name to authenticate to CROWD'),
        preparer=strip_whitespace,
        title=_('Application Name'),
        widget='string')
    app_password = colander.SchemaNode(
        colander.String(),
        default='',
        description=_('The password to authenticate to CROWD'),
        preparer=strip_whitespace,
        title=_('Application Password'),
        widget='password')
    admin_groups = colander.SchemaNode(
        colander.String(),
        default='',
        description=_('A comma separated list of group names that identify '
                      'users as RhodeCode Administrators'),
        missing='',
        preparer=strip_whitespace,
        title=_('Admin Groups'),
        widget='string')


class CrowdServer(object):
    def __init__(self, *args, **kwargs):
        """
        Create a new CrowdServer object that points to IP/Address 'host',
        on the given port, and using the given method (https/http). user and
        passwd can be set here or with set_credentials. If unspecified,
        "version" defaults to "latest".

        example::

            cserver = CrowdServer(host="127.0.0.1",
                                  port="8095",
                                  user="some_app",
                                  passwd="some_passwd",
                                  version="1")
        """
        if not "port" in kwargs:
            kwargs["port"] = "8095"
        self._logger = kwargs.get("logger", logging.getLogger(__name__))
        self._uri = "%s://%s:%s/crowd" % (kwargs.get("method", "http"),
                                    kwargs.get("host", "127.0.0.1"),
                                    kwargs.get("port", "8095"))
        self.set_credentials(kwargs.get("user", ""),
                             kwargs.get("passwd", ""))
        self._version = kwargs.get("version", "latest")
        self._url_list = None
        self._appname = "crowd"

    def set_credentials(self, user, passwd):
        self.user = user
        self.passwd = passwd
        self._make_opener()

    def _make_opener(self):
        mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        mgr.add_password(None, self._uri, self.user, self.passwd)
        handler = urllib2.HTTPBasicAuthHandler(mgr)
        self.opener = urllib2.build_opener(handler)

    def _request(self, url, body=None, headers=None,
                 method=None, noformat=False,
                 empty_response_ok=False):
        _headers = {"Content-type": "application/json",
                    "Accept": "application/json"}
        if self.user and self.passwd:
            authstring = base64.b64encode("%s:%s" % (self.user, self.passwd))
            _headers["Authorization"] = "Basic %s" % authstring
        if headers:
            _headers.update(headers)
        log.debug("Sent crowd: \n%s"
                  % (formatted_json({"url": url, "body": body,
                                           "headers": _headers})))
        request = urllib2.Request(url, body, _headers)
        if method:
            request.get_method = lambda: method

        global msg
        msg = ""
        try:
            rdoc = self.opener.open(request)
            msg = "".join(rdoc.readlines())
            if not msg and empty_response_ok:
                rval = {}
                rval["status"] = True
                rval["error"] = "Response body was empty"
            elif not noformat:
                rval = json.loads(msg)
                rval["status"] = True
            else:
                rval = "".join(rdoc.readlines())
        except Exception as e:
            if not noformat:
                rval = {"status": False,
                        "body": body,
                        "error": str(e) + "\n" + msg}
            else:
                rval = None
        return rval

    def user_auth(self, username, password):
        """Authenticate a user against crowd. Returns brief information about
        the user."""
        url = ("%s/rest/usermanagement/%s/authentication?username=%s"
               % (self._uri, self._version, username))
        body = json.dumps({"value": password})
        return self._request(url, body)

    def user_groups(self, username):
        """Retrieve a list of groups to which this user belongs."""
        url = ("%s/rest/usermanagement/%s/user/group/nested?username=%s"
               % (self._uri, self._version, username))
        return self._request(url)


class RhodeCodeAuthPlugin(RhodeCodeExternalAuthPlugin):

    def includeme(self, config):
        config.add_authn_plugin(self)
        config.add_authn_resource(self.get_id(), CrowdAuthnResource(self))
        config.add_view(
            'rhodecode.authentication.views.AuthnPluginViewBase',
            attr='settings_get',
            renderer='rhodecode:templates/admin/auth/plugin_settings.html',
            request_method='GET',
            route_name='auth_home',
            context=CrowdAuthnResource)
        config.add_view(
            'rhodecode.authentication.views.AuthnPluginViewBase',
            attr='settings_post',
            renderer='rhodecode:templates/admin/auth/plugin_settings.html',
            request_method='POST',
            route_name='auth_home',
            context=CrowdAuthnResource)

    def get_settings_schema(self):
        return CrowdSettingsSchema()

    def get_display_name(self):
        return _('CROWD')

    @hybrid_property
    def name(self):
        return "crowd"

    def use_fake_password(self):
        return True

    def user_activation_state(self):
        def_user_perms = User.get_default_user().AuthUser.permissions['global']
        return 'hg.extern_activate.auto' in def_user_perms

    def auth(self, userobj, username, password, settings, **kwargs):
        """
        Given a user object (which may be null), username, a plaintext password,
        and a settings object (containing all the keys needed as listed in settings()),
        authenticate this user's login attempt.

        Return None on failure. On success, return a dictionary of the form:

            see: RhodeCodeAuthPluginBase.auth_func_attrs
        This is later validated for correctness
        """
        if not username or not password:
            log.debug('Empty username or password skipping...')
            return None

        log.debug("Crowd settings: \n%s" % (formatted_json(settings)))
        server = CrowdServer(**settings)
        server.set_credentials(settings["app_name"], settings["app_password"])
        crowd_user = server.user_auth(username, password)
        log.debug("Crowd returned: \n%s" % (formatted_json(crowd_user)))
        if not crowd_user["status"]:
            return None

        res = server.user_groups(crowd_user["name"])
        log.debug("Crowd groups: \n%s" % (formatted_json(res)))
        crowd_user["groups"] = [x["name"] for x in res["groups"]]

        # old attrs fetched from RhodeCode database
        admin = getattr(userobj, 'admin', False)
        active = getattr(userobj, 'active', True)
        email = getattr(userobj, 'email', '')
        username = getattr(userobj, 'username', username)
        firstname = getattr(userobj, 'firstname', '')
        lastname = getattr(userobj, 'lastname', '')
        extern_type = getattr(userobj, 'extern_type', '')

        user_attrs = {
            'username': username,
            'firstname': crowd_user["first-name"] or firstname,
            'lastname': crowd_user["last-name"] or lastname,
            'groups': crowd_user["groups"],
            'email': crowd_user["email"] or email,
            'admin': admin,
            'active': active,
            'active_from_extern': crowd_user.get('active'),
            'extern_name': crowd_user["name"],
            'extern_type': extern_type,
        }

        # set an admin if we're in admin_groups of crowd
        for group in settings["admin_groups"]:
            if group in user_attrs["groups"]:
                user_attrs["admin"] = True
        log.debug("Final crowd user object: \n%s" % (formatted_json(user_attrs)))
        log.info('user %s authenticated correctly' % user_attrs['username'])
        return user_attrs
