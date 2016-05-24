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

from rhodecode.tests.fixture import Fixture

from rhodecode.model.db import User, Notification, UserNotification
from rhodecode.model.meta import Session
from rhodecode.model.notification import NotificationModel
from rhodecode.model.user import UserModel

fixture = Fixture()


class TestNotifications:
    destroy_users = set()

    @classmethod
    def teardown_class(cls):
        fixture.destroy_users(cls.destroy_users)

    @pytest.fixture(autouse=True)
    def create_users(self, request, pylonsapp):
        Session.remove()
        self.u1 = UserModel().create_or_update(
            username=u'u1', password=u'qweqwe',
            email=u'u1@rhodecode.org', firstname=u'u1', lastname=u'u1')
        Session().commit()
        self.u1 = self.u1.user_id

        self.u2 = UserModel().create_or_update(
            username=u'u2', password=u'qweqwe',
            email=u'u2@rhodecode.org', firstname=u'u2', lastname=u'u2')
        Session().commit()
        self.u2 = self.u2.user_id

        self.u3 = UserModel().create_or_update(
            username=u'u3', password=u'qweqwe',
            email=u'u3@rhodecode.org', firstname=u'u3', lastname=u'u3')
        Session().commit()
        self.u3 = self.u3.user_id
        self.destroy_users.add('u1')
        self.destroy_users.add('u2')
        self.destroy_users.add('u3')

    @pytest.fixture(autouse=True)
    def _clean_notifications(self, request, pylonsapp):
        for n in Notification.query().all():
            Session().delete(n)

        Session().commit()
        assert [] == Notification.query().all()
        assert [] == UserNotification.query().all()

    def test_create_notification(self):
        usrs = [self.u1, self.u2]
        notification = NotificationModel().create(
            created_by=self.u1, notification_subject=u'subj',
            notification_body=u'hi there', recipients=usrs)
        Session().commit()
        u1 = User.get(self.u1)
        u2 = User.get(self.u2)
        notifications = Notification.query().all()
        assert len(notifications) == 1

        assert notifications[0].recipients, [u1 == u2]
        assert notification.notification_id == notifications[0].notification_id

        unotification = UserNotification.query()\
            .filter(UserNotification.notification == notification).all()

        assert len(unotification) == len(usrs)
        assert set([x.user.user_id for x in unotification]) == set(usrs)

    def test_create_notification_fails_for_invalid_recipients(self):
        with pytest.raises(Exception):
            NotificationModel().create(
                created_by=self.u1, notification_subject=u'subj',
                notification_body=u'hi there', recipients=['bad_user_id'])

        with pytest.raises(Exception):
            NotificationModel().create(
                created_by=self.u1, notification_subject=u'subj',
                notification_body=u'hi there', recipients=[])

    def test_user_notifications(self):
        notification1 = NotificationModel().create(
            created_by=self.u1, notification_subject=u'subj',
            notification_body=u'hi there1', recipients=[self.u3])
        Session().commit()
        notification2 = NotificationModel().create(
            created_by=self.u1, notification_subject=u'subj',
            notification_body=u'hi there2', recipients=[self.u3])
        Session().commit()
        u3 = Session().query(User).get(self.u3)

        assert sorted([x.notification for x in u3.notifications]) ==\
            sorted([notification2, notification1])

    def test_delete_notifications(self):
        notification = NotificationModel().create(
            created_by=self.u1, notification_subject=u'title',
            notification_body=u'hi there3',
            recipients=[self.u3, self.u1, self.u2])
        Session().commit()
        notifications = Notification.query().all()
        assert notification in notifications

        Notification.delete(notification.notification_id)
        Session().commit()

        notifications = Notification.query().all()
        assert notification not in notifications

        un = UserNotification.query().filter(UserNotification.notification
                                             == notification).all()
        assert un == []

    def test_delete_association(self):
        notification = NotificationModel().create(
            created_by=self.u1, notification_subject=u'title',
            notification_body=u'hi there3',
            recipients=[self.u3, self.u1, self.u2])
        Session().commit()

        unotification = (
            UserNotification.query()
            .filter(UserNotification.notification == notification)
            .filter(UserNotification.user_id == self.u3)
            .scalar())

        assert unotification.user_id == self.u3

        NotificationModel().delete(self.u3,
                                   notification.notification_id)
        Session().commit()

        u3notification = (
            UserNotification.query()
            .filter(UserNotification.notification == notification)
            .filter(UserNotification.user_id == self.u3)
            .scalar())

        assert u3notification is None

        # notification object is still there
        assert Notification.query().all() == [notification]

        # u1 and u2 still have assignments
        u1notification = (
            UserNotification.query()
            .filter(UserNotification.notification == notification)
            .filter(UserNotification.user_id == self.u1)
            .scalar())
        assert u1notification is not None
        u2notification = (
            UserNotification.query()
            .filter(UserNotification.notification == notification)
            .filter(UserNotification.user_id == self.u2)
            .scalar())
        assert u2notification is not None

    def test_notification_counter(self):
        NotificationModel().create(
            created_by=self.u1, notification_subject=u'title',
            notification_body=u'hi there_delete', recipients=[self.u3, self.u1])
        Session().commit()

        # creator has it's own notification marked as read
        assert NotificationModel().get_unread_cnt_for_user(self.u1) == 0
        assert NotificationModel().get_unread_cnt_for_user(self.u2) == 0
        assert NotificationModel().get_unread_cnt_for_user(self.u3) == 1

        NotificationModel().create(
            created_by=self.u1, notification_subject=u'title',
            notification_body=u'hi there3',
            recipients=[self.u3, self.u1, self.u2])
        Session().commit()
        # creator has it's own notification marked as read
        assert NotificationModel().get_unread_cnt_for_user(self.u1) == 0
        assert NotificationModel().get_unread_cnt_for_user(self.u2) == 1
        assert NotificationModel().get_unread_cnt_for_user(self.u3) == 2
