from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.core import mail

from common.tests import TestUtilsMixin
from menu.tasks.notify_about_new_and_modified_dishes import notify_about_new_and_modified_dishes
from menu.tests.factories import DishFactory


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TasksTestCase(TestUtilsMixin, TestCase):
    def test_should_notify_about_yesterday_dishes(self):
        user_mail = 'mail@test.pl'
        User.objects.create_user('test_user', user_mail, 'password')
        current_date = datetime(2020, 12, 12, 12, 12, 12, tzinfo=timezone.utc)
        created_dishes, modified_dishes = self.create_dishes(current_date)
        with patch('django.utils.timezone.now') as date:
            date.return_value = current_date
            notify_about_new_and_modified_dishes.apply().get()

        self.assertEqual(len(mail.outbox), 1)
        received_mail = mail.outbox[0]
        expected_template_html = render_to_string(
            'menu/recently_modified_mail.html',
            {'created_dishes': created_dishes, 'modified_dishes': modified_dishes}
        )
        expected_template_string = render_to_string(
            'menu/recently_modified_mail.txt',
            {'created_dishes': created_dishes, 'modified_dishes': modified_dishes}
        )

        self.assertEqual(received_mail.alternatives[0][0], expected_template_html)
        self.assertEqual(received_mail.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(received_mail.body, expected_template_string)
        self.assertEqual(received_mail.subject, 'Recently modified and created dishes')
        self.assertEqual(received_mail.to[0], user_mail)

    def create_dishes(self, current_date):
        yesterday_date = current_date - timedelta(days=1)
        yesterday_created = self.call_with_mocked_date(DishFactory, yesterday_date)
        yesterday_modified = self.call_with_mocked_date(DishFactory, current_date - timedelta(days=3))
        self.call_with_mocked_date(yesterday_modified.save, yesterday_date)

        self.call_with_mocked_date(DishFactory, current_date)
        self.call_with_mocked_date(DishFactory, current_date - timedelta(days=2))

        return [yesterday_created], [yesterday_created, yesterday_modified]
