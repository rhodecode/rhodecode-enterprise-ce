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
users model for RhodeCode
"""

import logging
import traceback

import datetime
from pylons.i18n.translation import _

import ipaddress
from sqlalchemy.exc import DatabaseError
from sqlalchemy.sql.expression import true, false

from rhodecode.events import UserPreCreate, UserPreUpdate
from rhodecode.lib.utils2 import (
    safe_unicode, get_current_rhodecode_user, action_logger_generic,
    AttributeDict)
from rhodecode.lib.caching_query import FromCache
from rhodecode.model import BaseModel
from rhodecode.model.auth_token import AuthTokenModel
from rhodecode.model.db import (
    User, UserToPerm, UserEmailMap, UserIpMap)
from rhodecode.lib.exceptions import (
    DefaultUserException, UserOwnsReposException, UserOwnsRepoGroupsException,
    UserOwnsUserGroupsException, NotAllowedToCreateUserError)
from rhodecode.model.meta import Session
from rhodecode.model.repo_group import RepoGroupModel


log = logging.getLogger(__name__)


class UserModel(BaseModel):
    cls = User

    def get(self, user_id, cache=False):
        user = self.sa.query(User)
        if cache:
            user = user.options(FromCache("sql_cache_short",
                                          "get_user_%s" % user_id))
        return user.get(user_id)

    def get_user(self, user):
        return self._get_user(user)

    def get_by_username(self, username, cache=False, case_insensitive=False):

        if case_insensitive:
            user = self.sa.query(User).filter(User.username.ilike(username))
        else:
            user = self.sa.query(User)\
                .filter(User.username == username)
        if cache:
            user = user.options(FromCache("sql_cache_short",
                                          "get_user_%s" % username))
        return user.scalar()

    def get_by_email(self, email, cache=False, case_insensitive=False):
        return User.get_by_email(email, case_insensitive, cache)

    def get_by_auth_token(self, auth_token, cache=False):
        return User.get_by_auth_token(auth_token, cache)

    def get_active_user_count(self, cache=False):
        return User.query().filter(
            User.active == True).filter(
                User.username != User.DEFAULT_USER).count()

    def create(self, form_data, cur_user=None):
        if not cur_user:
            cur_user = getattr(get_current_rhodecode_user(), 'username', None)

        user_data = {
            'username': form_data['username'],
            'password': form_data['password'],
            'email': form_data['email'],
            'firstname': form_data['firstname'],
            'lastname': form_data['lastname'],
            'active': form_data['active'],
            'extern_type': form_data['extern_type'],
            'extern_name': form_data['extern_name'],
            'admin': False,
            'cur_user': cur_user
        }

        try:
            if form_data.get('create_repo_group'):
                user_data['create_repo_group'] = True
            if form_data.get('password_change'):
                user_data['force_password_change'] = True

            return UserModel().create_or_update(**user_data)
        except Exception:
            log.error(traceback.format_exc())
            raise

    def update_user(self, user, skip_attrs=None, **kwargs):
        from rhodecode.lib.auth import get_crypt_password

        user = self._get_user(user)
        if user.username == User.DEFAULT_USER:
            raise DefaultUserException(
                _("You can't Edit this user since it's"
                  " crucial for entire application"))

        # first store only defaults
        user_attrs = {
            'updating_user_id': user.user_id,
            'username': user.username,
            'password': user.password,
            'email': user.email,
            'firstname': user.name,
            'lastname': user.lastname,
            'active': user.active,
            'admin': user.admin,
            'extern_name': user.extern_name,
            'extern_type': user.extern_type,
            'language': user.user_data.get('language')
        }

        # in case there's new_password, that comes from form, use it to
        # store password
        if kwargs.get('new_password'):
            kwargs['password'] = kwargs['new_password']

        # cleanups, my_account password change form
        kwargs.pop('current_password', None)
        kwargs.pop('new_password', None)
        kwargs.pop('new_password_confirmation', None)

        # cleanups, user edit password change form
        kwargs.pop('password_confirmation', None)
        kwargs.pop('password_change', None)

        # create repo group on user creation
        kwargs.pop('create_repo_group', None)

        # legacy forms send name, which is the firstname
        firstname = kwargs.pop('name', None)
        if firstname:
            kwargs['firstname'] = firstname

        for k, v in kwargs.items():
            # skip if we don't want to update this
            if skip_attrs and k in skip_attrs:
                continue

            user_attrs[k] = v

        try:
            return self.create_or_update(**user_attrs)
        except Exception:
            log.error(traceback.format_exc())
            raise

    def create_or_update(
            self, username, password, email, firstname='', lastname='',
            active=True, admin=False, extern_type=None, extern_name=None,
            cur_user=None, plugin=None, force_password_change=False,
            allow_to_create_user=True, create_repo_group=False,
            updating_user_id=None, language=None, strict_creation_check=True):
        """
        Creates a new instance if not found, or updates current one

        :param username:
        :param password:
        :param email:
        :param firstname:
        :param lastname:
        :param active:
        :param admin:
        :param extern_type:
        :param extern_name:
        :param cur_user:
        :param plugin: optional plugin this method was called from
        :param force_password_change: toggles new or existing user flag
            for password change
        :param allow_to_create_user: Defines if the method can actually create
            new users
        :param create_repo_group: Defines if the method should also
            create an repo group with user name, and owner
        :param updating_user_id: if we set it up this is the user we want to
            update this allows to editing username.
        :param language: language of user from interface.

        :returns: new User object with injected `is_new_user` attribute.
        """
        if not cur_user:
            cur_user = getattr(get_current_rhodecode_user(), 'username', None)

        from rhodecode.lib.auth import (
            get_crypt_password, check_password, generate_auth_token)
        from rhodecode.lib.hooks_base import (
            log_create_user, check_allowed_create_user)

        def _password_change(new_user, password):
            # empty password
            if not new_user.password:
                return False

            # password check is only needed for RhodeCode internal auth calls
            # in case it's a plugin we don't care
            if not plugin:

                # first check if we gave crypted password back, and if it matches
                # it's not password change
                if new_user.password == password:
                    return False

                password_match = check_password(password, new_user.password)
                if not password_match:
                    return True

            return False

        user_data = {
            'username': username,
            'password': password,
            'email': email,
            'firstname': firstname,
            'lastname': lastname,
            'active': active,
            'admin': admin
        }

        if updating_user_id:
            log.debug('Checking for existing account in RhodeCode '
                      'database with user_id `%s` ' % (updating_user_id,))
            user = User.get(updating_user_id)
        else:
            log.debug('Checking for existing account in RhodeCode '
                      'database with username `%s` ' % (username,))
            user = User.get_by_username(username, case_insensitive=True)

        if user is None:
            # we check internal flag if this method is actually allowed to
            # create new user
            if not allow_to_create_user:
                msg = ('Method wants to create new user, but it is not '
                       'allowed to do so')
                log.warning(msg)
                raise NotAllowedToCreateUserError(msg)

            log.debug('Creating new user %s', username)

            # only if we create user that is active
            new_active_user = active
            if new_active_user and strict_creation_check:
                # raises UserCreationError if it's not allowed for any reason to
                # create new active user, this also executes pre-create hooks
                check_allowed_create_user(user_data, cur_user, strict_check=True)
            self.send_event(UserPreCreate(user_data))
            new_user = User()
            edit = False
        else:
            log.debug('updating user %s', username)
            self.send_event(UserPreUpdate(user, user_data))
            new_user = user
            edit = True

            # we're not allowed to edit default user
            if user.username == User.DEFAULT_USER:
                raise DefaultUserException(
                    _("You can't edit this user (`%(username)s`) since it's "
                      "crucial for entire application") % {'username': user.username})

        # inject special attribute that will tell us if User is new or old
        new_user.is_new_user = not edit
        # for users that didn's specify auth type, we use RhodeCode built in
        from rhodecode.authentication.plugins import auth_rhodecode
        extern_name = extern_name or auth_rhodecode.RhodeCodeAuthPlugin.name
        extern_type = extern_type or auth_rhodecode.RhodeCodeAuthPlugin.name

        try:
            new_user.username = username
            new_user.admin = admin
            new_user.email = email
            new_user.active = active
            new_user.extern_name = safe_unicode(extern_name)
            new_user.extern_type = safe_unicode(extern_type)
            new_user.name = firstname
            new_user.lastname = lastname

            if not edit:
                new_user.api_key = generate_auth_token(username)

            # set password only if creating an user or password is changed
            if not edit or _password_change(new_user, password):
                reason = 'new password' if edit else 'new user'
                log.debug('Updating password reason=>%s', reason)
                new_user.password = get_crypt_password(password) if password else None

            if force_password_change:
                new_user.update_userdata(force_password_change=True)
            if language:
                new_user.update_userdata(language=language)

            self.sa.add(new_user)

            if not edit and create_repo_group:
                # create new group same as username, and make this user an owner
                desc = RepoGroupModel.PERSONAL_GROUP_DESC % {'username': username}
                RepoGroupModel().create(group_name=username,
                                        group_description=desc,
                                        owner=username, commit_early=False)
            if not edit:
                # add the RSS token
                AuthTokenModel().create(username,
                                        description='Generated feed token',
                                        role=AuthTokenModel.cls.ROLE_FEED)
                log_create_user(created_by=cur_user, **new_user.get_dict())
            return new_user
        except (DatabaseError,):
            log.error(traceback.format_exc())
            raise

    def create_registration(self, form_data):
        from rhodecode.model.notification import NotificationModel
        from rhodecode.model.notification import EmailNotificationModel

        try:
            form_data['admin'] = False
            form_data['extern_name'] = 'rhodecode'
            form_data['extern_type'] = 'rhodecode'
            new_user = self.create(form_data)

            self.sa.add(new_user)
            self.sa.flush()

            user_data = new_user.get_dict()
            kwargs = {
                # use SQLALCHEMY safe dump of user data
                'user': AttributeDict(user_data),
                'date': datetime.datetime.now()
            }
            notification_type = EmailNotificationModel.TYPE_REGISTRATION
            # pre-generate the subject for notification itself
            (subject,
             _h, _e,  # we don't care about those
             body_plaintext) = EmailNotificationModel().render_email(
                notification_type, **kwargs)

            # create notification objects, and emails
            NotificationModel().create(
                created_by=new_user,
                notification_subject=subject,
                notification_body=body_plaintext,
                notification_type=notification_type,
                recipients=None,  # all admins
                email_kwargs=kwargs,
            )

            return new_user
        except Exception:
            log.error(traceback.format_exc())
            raise

    def _handle_user_repos(self, username, repositories, handle_mode=None):
        _superadmin = self.cls.get_first_admin()
        left_overs = True

        from rhodecode.model.repo import RepoModel

        if handle_mode == 'detach':
            for obj in repositories:
                obj.user = _superadmin
                # set description we know why we super admin now owns
                # additional repositories that were orphaned !
                obj.description += '  \n::detached repository from deleted user: %s' % (username,)
                self.sa.add(obj)
            left_overs = False
        elif handle_mode == 'delete':
            for obj in repositories:
                RepoModel().delete(obj, forks='detach')
            left_overs = False

        # if nothing is done we have left overs left
        return left_overs

    def _handle_user_repo_groups(self, username, repository_groups,
                                 handle_mode=None):
        _superadmin = self.cls.get_first_admin()
        left_overs = True

        from rhodecode.model.repo_group import RepoGroupModel

        if handle_mode == 'detach':
            for r in repository_groups:
                r.user = _superadmin
                # set description we know why we super admin now owns
                # additional repositories that were orphaned !
                r.group_description += '  \n::detached repository group from deleted user: %s' % (username,)
                self.sa.add(r)
            left_overs = False
        elif handle_mode == 'delete':
            for r in repository_groups:
                RepoGroupModel().delete(r)
            left_overs = False

        # if nothing is done we have left overs left
        return left_overs

    def _handle_user_user_groups(self, username, user_groups, handle_mode=None):
        _superadmin = self.cls.get_first_admin()
        left_overs = True

        from rhodecode.model.user_group import UserGroupModel

        if handle_mode == 'detach':
            for r in user_groups:
                for user_user_group_to_perm in r.user_user_group_to_perm:
                    if user_user_group_to_perm.user.username == username:
                        user_user_group_to_perm.user = _superadmin
                r.user = _superadmin
                # set description we know why we super admin now owns
                # additional repositories that were orphaned !
                r.user_group_description += '  \n::detached user group from deleted user: %s' % (username,)
                self.sa.add(r)
            left_overs = False
        elif handle_mode == 'delete':
            for r in user_groups:
                UserGroupModel().delete(r)
            left_overs = False

        # if nothing is done we have left overs left
        return left_overs

    def delete(self, user, cur_user=None, handle_repos=None,
               handle_repo_groups=None, handle_user_groups=None):
        if not cur_user:
            cur_user = getattr(get_current_rhodecode_user(), 'username', None)
        user = self._get_user(user)

        try:
            if user.username == User.DEFAULT_USER:
                raise DefaultUserException(
                    _(u"You can't remove this user since it's"
                      u" crucial for entire application"))

            left_overs = self._handle_user_repos(
                user.username, user.repositories, handle_repos)
            if left_overs and user.repositories:
                repos = [x.repo_name for x in user.repositories]
                raise UserOwnsReposException(
                    _(u'user "%s" still owns %s repositories and cannot be '
                      u'removed. Switch owners or remove those repositories:%s')
                    % (user.username, len(repos), ', '.join(repos)))

            left_overs = self._handle_user_repo_groups(
                user.username, user.repository_groups, handle_repo_groups)
            if left_overs and user.repository_groups:
                repo_groups = [x.group_name for x in user.repository_groups]
                raise UserOwnsRepoGroupsException(
                    _(u'user "%s" still owns %s repository groups and cannot be '
                      u'removed. Switch owners or remove those repository groups:%s')
                    % (user.username, len(repo_groups), ', '.join(repo_groups)))

            left_overs = self._handle_user_user_groups(
                user.username, user.user_groups, handle_user_groups)
            if left_overs and user.user_groups:
                user_groups = [x.users_group_name for x in user.user_groups]
                raise UserOwnsUserGroupsException(
                    _(u'user "%s" still owns %s user groups and cannot be '
                      u'removed. Switch owners or remove those user groups:%s')
                    % (user.username, len(user_groups), ', '.join(user_groups)))

            # we might change the user data with detach/delete, make sure
            # the object is marked as expired before actually deleting !
            self.sa.expire(user)
            self.sa.delete(user)
            from rhodecode.lib.hooks_base import log_delete_user
            log_delete_user(deleted_by=cur_user, **user.get_dict())
        except Exception:
            log.error(traceback.format_exc())
            raise

    def reset_password_link(self, data, pwd_reset_url):
        from rhodecode.lib.celerylib import tasks, run_task
        from rhodecode.model.notification import EmailNotificationModel
        user_email = data['email']
        try:
            user = User.get_by_email(user_email)
            if user:
                log.debug('password reset user found %s', user)

                email_kwargs = {
                    'password_reset_url': pwd_reset_url,
                    'user': user,
                    'email': user_email,
                    'date': datetime.datetime.now()
                }

                (subject, headers, email_body,
                 email_body_plaintext) = EmailNotificationModel().render_email(
                    EmailNotificationModel.TYPE_PASSWORD_RESET, **email_kwargs)

                recipients = [user_email]

                action_logger_generic(
                    'sending password reset email to user: {}'.format(
                        user), namespace='security.password_reset')

                run_task(tasks.send_email, recipients, subject,
                         email_body_plaintext, email_body)

            else:
                log.debug("password reset email %s not found", user_email)
        except Exception:
            log.error(traceback.format_exc())
            return False

        return True

    def reset_password(self, data):
        from rhodecode.lib.celerylib import tasks, run_task
        from rhodecode.model.notification import EmailNotificationModel
        from rhodecode.lib import auth
        user_email = data['email']
        pre_db = True
        try:
            user = User.get_by_email(user_email)
            new_passwd = auth.PasswordGenerator().gen_password(
                12, auth.PasswordGenerator.ALPHABETS_BIG_SMALL)
            if user:
                user.password = auth.get_crypt_password(new_passwd)
                # also force this user to reset his password !
                user.update_userdata(force_password_change=True)

                Session().add(user)
                Session().commit()
                log.info('change password for %s', user_email)
            if new_passwd is None:
                raise Exception('unable to generate new password')

            pre_db = False

            email_kwargs = {
                'new_password': new_passwd,
                'user': user,
                'email': user_email,
                'date': datetime.datetime.now()
            }

            (subject, headers, email_body,
             email_body_plaintext) = EmailNotificationModel().render_email(
                EmailNotificationModel.TYPE_PASSWORD_RESET_CONFIRMATION, **email_kwargs)

            recipients = [user_email]

            action_logger_generic(
                'sent new password to user: {} with email: {}'.format(
                    user, user_email), namespace='security.password_reset')

            run_task(tasks.send_email, recipients, subject,
                     email_body_plaintext, email_body)

        except Exception:
            log.error('Failed to update user password')
            log.error(traceback.format_exc())
            if pre_db:
                # we rollback only if local db stuff fails. If it goes into
                # run_task, we're pass rollback state this wouldn't work then
                Session().rollback()

        return True

    def fill_data(self, auth_user, user_id=None, api_key=None, username=None):
        """
        Fetches auth_user by user_id,or api_key if present.
        Fills auth_user attributes with those taken from database.
        Additionally set's is_authenitated if lookup fails
        present in database

        :param auth_user: instance of user to set attributes
        :param user_id: user id to fetch by
        :param api_key: api key to fetch by
        :param username: username to fetch by
        """
        if user_id is None and api_key is None and username is None:
            raise Exception('You need to pass user_id, api_key or username')

        log.debug(
            'doing fill data based on: user_id:%s api_key:%s username:%s',
            user_id, api_key, username)
        try:
            dbuser = None
            if user_id:
                dbuser = self.get(user_id)
            elif api_key:
                dbuser = self.get_by_auth_token(api_key)
            elif username:
                dbuser = self.get_by_username(username)

            if not dbuser:
                log.warning(
                    'Unable to lookup user by id:%s api_key:%s username:%s',
                    user_id, api_key, username)
                return False
            if not dbuser.active:
                log.debug('User `%s` is inactive, skipping fill data', username)
                return False

            log.debug('filling user:%s data', dbuser)

            # TODO: johbo: Think about this and find a clean solution
            user_data = dbuser.get_dict()
            user_data.update(dbuser.get_api_data(include_secrets=True))

            for k, v in user_data.iteritems():
                # properties of auth user we dont update
                if k not in ['auth_tokens', 'permissions']:
                    setattr(auth_user, k, v)

            # few extras
            setattr(auth_user, 'feed_token', dbuser.feed_token)
        except Exception:
            log.error(traceback.format_exc())
            auth_user.is_authenticated = False
            return False

        return True

    def has_perm(self, user, perm):
        perm = self._get_perm(perm)
        user = self._get_user(user)

        return UserToPerm.query().filter(UserToPerm.user == user)\
            .filter(UserToPerm.permission == perm).scalar() is not None

    def grant_perm(self, user, perm):
        """
        Grant user global permissions

        :param user:
        :param perm:
        """
        user = self._get_user(user)
        perm = self._get_perm(perm)
        # if this permission is already granted skip it
        _perm = UserToPerm.query()\
            .filter(UserToPerm.user == user)\
            .filter(UserToPerm.permission == perm)\
            .scalar()
        if _perm:
            return
        new = UserToPerm()
        new.user = user
        new.permission = perm
        self.sa.add(new)
        return new

    def revoke_perm(self, user, perm):
        """
        Revoke users global permissions

        :param user:
        :param perm:
        """
        user = self._get_user(user)
        perm = self._get_perm(perm)

        obj = UserToPerm.query()\
                .filter(UserToPerm.user == user)\
                .filter(UserToPerm.permission == perm)\
                .scalar()
        if obj:
            self.sa.delete(obj)

    def add_extra_email(self, user, email):
        """
        Adds email address to UserEmailMap

        :param user:
        :param email:
        """
        from rhodecode.model import forms
        form = forms.UserExtraEmailForm()()
        data = form.to_python({'email': email})
        user = self._get_user(user)

        obj = UserEmailMap()
        obj.user = user
        obj.email = data['email']
        self.sa.add(obj)
        return obj

    def delete_extra_email(self, user, email_id):
        """
        Removes email address from UserEmailMap

        :param user:
        :param email_id:
        """
        user = self._get_user(user)
        obj = UserEmailMap.query().get(email_id)
        if obj:
            self.sa.delete(obj)

    def parse_ip_range(self, ip_range):
        ip_list = []
        def make_unique(value):
            seen = []
            return [c for c in value if not (c in seen or seen.append(c))]

        # firsts split by commas
        for ip_range in ip_range.split(','):
            if not ip_range:
                continue
            ip_range = ip_range.strip()
            if '-' in ip_range:
                start_ip, end_ip = ip_range.split('-', 1)
                start_ip = ipaddress.ip_address(start_ip.strip())
                end_ip = ipaddress.ip_address(end_ip.strip())
                parsed_ip_range = []

                for index in xrange(int(start_ip), int(end_ip) + 1):
                    new_ip = ipaddress.ip_address(index)
                    parsed_ip_range.append(str(new_ip))
                ip_list.extend(parsed_ip_range)
            else:
                ip_list.append(ip_range)

        return make_unique(ip_list)

    def add_extra_ip(self, user, ip, description=None):
        """
        Adds ip address to UserIpMap

        :param user:
        :param ip:
        """
        from rhodecode.model import forms
        form = forms.UserExtraIpForm()()
        data = form.to_python({'ip': ip})
        user = self._get_user(user)

        obj = UserIpMap()
        obj.user = user
        obj.ip_addr = data['ip']
        obj.description = description
        self.sa.add(obj)
        return obj

    def delete_extra_ip(self, user, ip_id):
        """
        Removes ip address from UserIpMap

        :param user:
        :param ip_id:
        """
        user = self._get_user(user)
        obj = UserIpMap.query().get(ip_id)
        if obj:
            self.sa.delete(obj)

    def get_accounts_in_creation_order(self, current_user=None):
        """
        Get accounts in order of creation for deactivation for license limits

        pick currently logged in user, and append to the list in position 0
        pick all super-admins in order of creation date and add it to the list
        pick all other accounts in order of creation and add it to the list.

        Based on that list, the last accounts can be disabled as they are
        created at the end and don't include any of the super admins as well
        as the current user.

        :param current_user: optionally current user running this operation
        """

        if not current_user:
            current_user = get_current_rhodecode_user()
        active_super_admins = [
            x.user_id for x in User.query()
            .filter(User.user_id != current_user.user_id)
            .filter(User.active == true())
            .filter(User.admin == true())
            .order_by(User.created_on.asc())]

        active_regular_users = [
            x.user_id for x in User.query()
            .filter(User.user_id != current_user.user_id)
            .filter(User.active == true())
            .filter(User.admin == false())
            .order_by(User.created_on.asc())]

        list_of_accounts = [current_user.user_id]
        list_of_accounts += active_super_admins
        list_of_accounts += active_regular_users

        return list_of_accounts

    def deactivate_last_users(self, expected_users):
        """
        Deactivate accounts that are over the license limits.
        Algorithm of which accounts to disabled is based on the formula:

        Get current user, then super admins in creation order, then regular
        active users in creation order.

        Using that list we mark all accounts from the end of it as inactive.
        This way we block only latest created accounts.

        :param expected_users: list of users in special order, we deactivate
            the end N ammoun of users from that list
        """

        list_of_accounts = self.get_accounts_in_creation_order()

        for acc_id in list_of_accounts[expected_users + 1:]:
            user = User.get(acc_id)
            log.info('Deactivating account %s for license unlock', user)
            user.active = False
            Session().add(user)
            Session().commit()

        return
