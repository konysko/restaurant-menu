import logging
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from menu.models import Menu

logger = logging.getLogger()


def notify_about_new_and_modified_menus():
    yesterday_date = timezone.now() - timedelta(days=1)
    yesterday_menus = Menu.objects.filter(
        Q(created__year=yesterday_date.year,
          created__month=yesterday_date.month,
          created_day=yesterday_date.day
          ) |
        Q(modified__year=yesterday_date.year,
          modified__month=yesterday_date.month,
          modified_day=yesterday_date.day
          )
    )
    logger.info(f'Menus created/modified on {yesterday_date.isoformat()}: {yesterday_menus.count()}')
