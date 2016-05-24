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
notifications controller for RhodeCode
"""

import logging
import traceback

from pylons import request
from pylons import tmpl_context as c, url
from pylons.controllers.util import redirect, abort
import webhelpers.paginate
from webob.exc import HTTPBadRequest

from rhodecode.lib import auth
from rhodecode.lib.auth import LoginRequired, NotAnonymous
from rhodecode.lib.base import BaseController, render
from rhodecode.lib import helpers as h
from rhodecode.lib.helpers import Page
from rhodecode.lib.utils2 import safe_int
from rhodecode.model.db import Notification
from rhodecode.model.notification import NotificationModel
from rhodecode.model.meta import Session


log = logging.getLogger(__name__)


class NotificationsController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('notification', 'notifications', controller='_admin/notifications',
    #         path_prefix='/_admin', name_prefix='_admin_')

    @LoginRequired()
    @NotAnonymous()
    def __before__(self):
        super(NotificationsController, self).__before__()

    def index(self):
        """GET /_admin/notifications: All items in the collection"""
        # url('notifications')
        c.user = c.rhodecode_user
        notif = NotificationModel().get_for_user(c.rhodecode_user.user_id,
                                            filter_=request.GET.getall('type'))

        p = safe_int(request.GET.get('page', 1), 1)
        notifications_url = webhelpers.paginate.PageURL(
            url('notifications'), request.GET)
        c.notifications = Page(notif, page=p, items_per_page=10,
                               url=notifications_url)
        c.pull_request_type = Notification.TYPE_PULL_REQUEST
        c.comment_type = [Notification.TYPE_CHANGESET_COMMENT,
                          Notification.TYPE_PULL_REQUEST_COMMENT]

        _current_filter = request.GET.getall('type')
        c.current_filter = 'all'
        if _current_filter == [c.pull_request_type]:
            c.current_filter = 'pull_request'
        elif _current_filter == c.comment_type:
            c.current_filter = 'comment'

        if request.is_xhr:
            return render('admin/notifications/notifications_data.html')

        return render('admin/notifications/notifications.html')

    @auth.CSRFRequired()
    def mark_all_read(self):
        if request.is_xhr:
            nm = NotificationModel()
            # mark all read
            nm.mark_all_read_for_user(c.rhodecode_user.user_id,
                                      filter_=request.GET.getall('type'))
            Session().commit()
            c.user = c.rhodecode_user
            notif = nm.get_for_user(c.rhodecode_user.user_id,
                                    filter_=request.GET.getall('type'))
            notifications_url = webhelpers.paginate.PageURL(
                url('notifications'), request.GET)
            c.notifications = Page(notif, page=1, items_per_page=10,
                                   url=notifications_url)
            return render('admin/notifications/notifications_data.html')

    def _has_permissions(self, notification):
        def is_owner():
            user_id = c.rhodecode_user.user_id
            for user_notification in notification.notifications_to_users:
                if user_notification.user.user_id == user_id:
                    return True
            return False
        return h.HasPermissionAny('hg.admin')() or is_owner()

    @auth.CSRFRequired()
    def update(self, notification_id):
        """PUT /_admin/notifications/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('notification', notification_id=ID),
        #           method='put')
        # url('notification', notification_id=ID)
        try:
            no = Notification.get(notification_id)
            if self._has_permissions(no):
                # deletes only notification2user
                NotificationModel().mark_read(c.rhodecode_user.user_id, no)
                Session().commit()
                return 'ok'
        except Exception:
            Session().rollback()
            log.exception("Exception updating a notification item")
        raise HTTPBadRequest()

    @auth.CSRFRequired()
    def delete(self, notification_id):
        """DELETE /_admin/notifications/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('notification', notification_id=ID),
        #           method='delete')
        # url('notification', notification_id=ID)
        try:
            no = Notification.get(notification_id)
            if self._has_permissions(no):
                # deletes only notification2user
                NotificationModel().delete(c.rhodecode_user.user_id, no)
                Session().commit()
                return 'ok'
        except Exception:
            Session().rollback()
            log.exception("Exception deleting a notification item")
        raise HTTPBadRequest()

    def show(self, notification_id):
        """GET /_admin/notifications/id: Show a specific item"""
        # url('notification', notification_id=ID)
        c.user = c.rhodecode_user
        no = Notification.get(notification_id)

        if no and self._has_permissions(no):
            unotification = NotificationModel()\
                            .get_user_notification(c.user.user_id, no)

            # if this association to user is not valid, we don't want to show
            # this message
            if unotification:
                if not unotification.read:
                    unotification.mark_as_read()
                    Session().commit()
                c.notification = no

                return render('admin/notifications/show_notification.html')

        return abort(403)
