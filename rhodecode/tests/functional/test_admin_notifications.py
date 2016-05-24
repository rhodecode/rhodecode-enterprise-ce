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

import pytest

from rhodecode.tests import *
from rhodecode.tests.fixture import Fixture

from rhodecode.model.db import Notification, User
from rhodecode.model.user import UserModel
from rhodecode.model.notification import NotificationModel
from rhodecode.model.meta import Session

fixture = Fixture()


class TestNotificationsController(TestController):
    destroy_users = set()

    @classmethod
    def teardown_class(cls):
        fixture.destroy_users(cls.destroy_users)

    def teardown_method(self, method):
        for n in Notification.query().all():
            inst = Notification.get(n.notification_id)
            Session().delete(inst)
        Session().commit()

    def test_index(self):
        u1 = UserModel().create_or_update(
            username='u1', password='qweqwe', email='u1@rhodecode.org',
            firstname='u1', lastname='u1')
        u1 = u1.user_id
        self.destroy_users.add('u1')

        self.log_user('u1', 'qweqwe')

        response = self.app.get(url('notifications'))
        response.mustcontain(
            '<div class="table">No notifications here yet</div>')

        cur_user = self._get_logged_user()
        notif = NotificationModel().create(
            created_by=u1, notification_subject=u'test_notification_1',
            notification_body=u'notification_1', recipients=[cur_user])
        Session().commit()
        response = self.app.get(url('notifications'))
        response.mustcontain('id="notification_%s"' % notif.notification_id)

    @pytest.mark.parametrize('user,password', [
        (TEST_USER_ADMIN_LOGIN, TEST_USER_ADMIN_PASS),
        (TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS),
    ])
    def test_delete(self, user, password):
        self.log_user(user, password)
        cur_user = self._get_logged_user()

        u1 = UserModel().create_or_update(
            username='u1', password='qweqwe',
            email='u1@rhodecode.org', firstname='u1', lastname='u1')
        u2 = UserModel().create_or_update(
            username='u2', password='qweqwe', email='u2@rhodecode.org',
            firstname='u2', lastname='u2')
        self.destroy_users.add('u1')
        self.destroy_users.add('u2')

        # make notifications
        notification = NotificationModel().create(
            created_by=cur_user, notification_subject=u'test',
            notification_body=u'hi there', recipients=[cur_user, u1, u2])
        Session().commit()
        u1 = User.get(u1.user_id)
        u2 = User.get(u2.user_id)

        # check DB
        get_notif = lambda un: [x.notification for x in un]
        assert get_notif(cur_user.notifications) == [notification]
        assert get_notif(u1.notifications) == [notification]
        assert get_notif(u2.notifications) == [notification]
        cur_usr_id = cur_user.user_id

        response = self.app.post(
            url('notification', notification_id=notification.notification_id),
            params={'_method': 'delete', 'csrf_token': self.csrf_token})
        assert response.body == 'ok'

        cur_user = User.get(cur_usr_id)
        assert cur_user.notifications == []

    @pytest.mark.parametrize('user,password', [
        (TEST_USER_ADMIN_LOGIN, TEST_USER_ADMIN_PASS),
        (TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS),
    ])
    def test_show(self, user, password):
        self.log_user(user, password)
        cur_user = self._get_logged_user()
        u1 = UserModel().create_or_update(username='u1', password='qweqwe',
                                          email='u1@rhodecode.org',
                                          firstname='u1', lastname='u1')
        u2 = UserModel().create_or_update(username='u2', password='qweqwe',
                                          email='u2@rhodecode.org',
                                          firstname='u2', lastname='u2')
        self.destroy_users.add('u1')
        self.destroy_users.add('u2')

        subject = u'test'
        notif_body = u'hi there'
        notification = NotificationModel().create(
            created_by=cur_user, notification_subject=subject,
            notification_body=notif_body, recipients=[cur_user, u1, u2])

        response = self.app.get(url(
            'notification', notification_id=notification.notification_id))

        response.mustcontain(subject)
        response.mustcontain(notif_body)

    @pytest.mark.parametrize('user,password', [
        (TEST_USER_ADMIN_LOGIN, TEST_USER_ADMIN_PASS),
        (TEST_USER_REGULAR_LOGIN, TEST_USER_REGULAR_PASS),
    ])
    def test_update(self, user, password):
        self.log_user(user, password)
        cur_user = self._get_logged_user()

        u1 = UserModel().create_or_update(username='u1', password='qweqwe',
                                          email='u1@rhodecode.org',
                                          firstname='u1', lastname='u1')
        u2 = UserModel().create_or_update(username='u2', password='qweqwe',
                                          email='u2@rhodecode.org',
                                          firstname='u2', lastname='u2')
        self.destroy_users.add('u1')
        self.destroy_users.add('u2')

        # make notifications
        recipients = [cur_user, u1, u2]
        notification = NotificationModel().create(
            created_by=cur_user, notification_subject=u'test',
            notification_body=u'hi there', recipients=recipients)
        Session().commit()

        for u_obj in recipients:
            # if it's current user, he has his message already read
            read = u_obj.username == user
            assert len(u_obj.notifications) == 1
            assert u_obj.notifications[0].read == read

        response = self.app.post(
            url('notification', notification_id=notification.notification_id),
            params={'_method': 'put', 'csrf_token': self.csrf_token})
        assert response.body == 'ok'

        cur_user = self._get_logged_user()
        assert True == cur_user.notifications[0].read
