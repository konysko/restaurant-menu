from datetime import datetime, timedelta
from typing import List, Tuple

from celery import task, group
from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import get_connection, send_mail
from django.db.models import QuerySet
from django.template.loader import render_to_string
from django.utils import timezone

from menu.models import Dish

logger = get_task_logger(__name__)


class NotifyManager:
    base_template_path = 'menu/recently_modified_mail'

    @classmethod
    def run(cls, chunk_size: int) -> None:
        yesterday_date = timezone.now() - timedelta(days=1)
        modified_dishes = cls.get_modified_dishes(yesterday_date)
        created_dishes = cls.get_created_dishes(yesterday_date)
        logger.info(f'Menus created/modified on {yesterday_date.isoformat()}: '
                    f'{created_dishes.count()}/{modified_dishes.count()}')

        context = {
            'created_dishes': created_dishes,
            'modified_dishes': modified_dishes
        }
        template_html = render_to_string(
            f'{cls.base_template_path}.html',
            context
        )
        template_text = render_to_string(
            f'{cls.base_template_path}.txt',
            context
        )
        mails = cls.get_mails(template_text, template_html)

        sent_mails, failed_mails = cls.send(mails, chunk_size)

        if failed_mails:
            logger.info('Retrying sending failed mails')
            cls.send(failed_mails, chunk_size)

        logger.info('Finishing')

    @staticmethod
    def send(mails: List[dict], chunk_size: int) -> Tuple[List[dict], List[dict]]:
        logger.info(f'Sending mails in {chunk_size} batches')
        chunked_tasks = group(
            send_emails.s(mails[i:i + chunk_size])
            for i in range(0, len(mails), chunk_size)
        )()

        sent_mails = []
        failed_mails = []
        for result in chunked_tasks.get():
            sent_mails.extend(result[0])
            failed_mails.extend(result[1])

        logger.info(f'Sent/failed mails {len(sent_mails)} / {len(failed_mails)}')
        return sent_mails, failed_mails

    @staticmethod
    def get_mails(template_text: str, template_html: str) -> List[dict]:
        return [{
            'subject': 'Recently modified and created dishes',
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'message': template_text,
            'html_message': template_html,
            'recipient_list': [user_mail]
        } for user_mail in User.objects.values_list('email', flat=True).distinct()]

    @staticmethod
    def get_modified_dishes(yesterday_date: datetime) -> 'QuerySet[Dish]':
        return Dish.objects.filter(
            modified__year=yesterday_date.year,
            modified__month=yesterday_date.month,
            modified__day=yesterday_date.day
        ).select_related('menu')

    @staticmethod
    def get_created_dishes(yesterday_date: datetime) -> 'QuerySet[Dish]':
        return Dish.objects.filter(
            created__year=yesterday_date.year,
            created__month=yesterday_date.month,
            created__day=yesterday_date.day
        ).select_related('menu')


@task
def notify_about_new_and_modified_dishes(chunk_size: int = 10) -> None:
    NotifyManager.run(chunk_size)


@task
def send_emails(emails: List[dict]) -> Tuple[List[dict], List[dict]]:
    failed_mails = []
    sent_mails = []
    connection = get_connection()
    for mail in emails:
        result = send_mail(**mail, connection=connection, fail_silently=True)
        if result == 1:
            sent_mails.append(mail)
        else:
            failed_mails.append(mail)
    connection.close()
    return sent_mails, failed_mails
