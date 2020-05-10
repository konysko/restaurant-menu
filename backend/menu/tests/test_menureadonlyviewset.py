from datetime import datetime, timezone
from unittest.mock import patch

from django.utils.duration import duration_string
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from common.tests import TestUtilsMixin
from .factories import MenuFactory, DishFactory
from menu.models import Menu, Dish


class TestCaseMenuReadOnlyViewSet(TestUtilsMixin, APITestCase):
    def test_should_list_nonempty_menus(self):
        menus = MenuFactory.create_batch(5)
        DishFactory(menu=menus[0])
        DishFactory(menu=menus[2])

        path = reverse('menu-list')
        response = self.client.get(path)
        expected = [self.transform_menu(menu) for menu in
                    Menu.objects.filter(pk__in=map(lambda n: n.id, menus), dishes__isnull=False)]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json(), expected)

    def test_should_retrieve_menu_with_dishes(self):
        menu = MenuFactory()
        dishes = DishFactory.create_batch(5, menu=menu)

        path = reverse('menu-detail', args=[menu.id])
        response = self.client.get(path)

        expected = {
            **self.transform_menu(menu),
            'dishes': [self.transform_dish(dish) for dish in dishes]
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(), expected)

    def test_should_order_menus_by_name_ascending(self):
        menus = [
            *MenuFactory.create_batch(5),
            MenuFactory(name='aaaa'),
            MenuFactory(name='zzzz')
        ]
        for menu in menus:
            DishFactory(menu=menu)

        path = reverse('menu-list')
        response = self.client.get(path, data={'ordering': 'name'})

        expected = [self.transform_menu(menu) for menu in Menu.objects.order_by('name')]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json(), expected)

    def test_should_order_menus_by_name_descending(self):
        menus = [
            *MenuFactory.create_batch(5),
            MenuFactory(name='aaaa'),
            MenuFactory(name='zzzz')
        ]
        for menu in menus:
            DishFactory(menu=menu)

        path = reverse('menu-list')
        response = self.client.get(path, data={'ordering': '-name'})

        expected = [self.transform_menu(menu) for menu in Menu.objects.order_by('-name')]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json(), expected)

    def test_should_order_menus_by_dishes_number_ascending(self):
        menu1 = MenuFactory()
        DishFactory.create_batch(1, menu=menu1)
        menu3 = MenuFactory()
        DishFactory.create_batch(5, menu=menu3)
        menu2 = MenuFactory()
        DishFactory.create_batch(3, menu=menu2)

        path = reverse('menu-list')
        response = self.client.get(path, data={'ordering': 'dishes_count'})

        expected = [self.transform_menu(menu) for menu in [menu1, menu2, menu3]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json(), expected)

    def test_should_order_menus_by_dishes_number_descending(self):
        menu1 = MenuFactory()
        DishFactory.create_batch(1, menu=menu1)
        menu2 = MenuFactory()
        DishFactory.create_batch(3, menu=menu2)
        menu3 = MenuFactory()
        DishFactory.create_batch(5, menu=menu3)

        path = reverse('menu-list')
        response = self.client.get(path, data={'ordering': '-dishes_count'})

        expected = [self.transform_menu(menu) for menu in [menu3, menu2, menu1]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json(), expected)

    def test_should_filter_menus_by_modified_date(self):
        menu1 = self.call_with_mocked_date(MenuFactory, datetime(2020, 8, 12, 12, 12, 12, tzinfo=timezone.utc))
        DishFactory(menu=menu1)
        menu2 = self.call_with_mocked_date(MenuFactory, datetime(2020, 9, 12, 12, 12, 12, tzinfo=timezone.utc))
        DishFactory(menu=menu2)
        menu3 = self.call_with_mocked_date(MenuFactory, datetime(2020, 10, 12, 12, 12, 12, tzinfo=timezone.utc))
        DishFactory(menu=menu3)
        menu4 = self.call_with_mocked_date(MenuFactory, datetime(2020, 11, 12, 12, 12, 12, tzinfo=timezone.utc))
        DishFactory(menu=menu4)

        path = reverse('menu-list')
        payload = {
            'modified__gte': self.transform_date(menu2.modified),
            'modified__lte': self.transform_date(menu3.modified)
        }
        response = self.client.get(path, data=payload)

        expected = [self.transform_menu(menu) for menu in [menu2, menu3]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json(), expected)

    def test_should_filter_menus_by_created_date(self):
        menu1 = self.call_with_mocked_date(MenuFactory, datetime(2020, 8, 12, 12, 12, 12, tzinfo=timezone.utc))
        DishFactory(menu=menu1)
        menu2 = self.call_with_mocked_date(MenuFactory, datetime(2020, 9, 12, 12, 12, 12, tzinfo=timezone.utc))
        DishFactory(menu=menu2)
        menu3 = self.call_with_mocked_date(MenuFactory, datetime(2020, 10, 12, 12, 12, 12, tzinfo=timezone.utc))
        DishFactory(menu=menu3)
        menu4 = self.call_with_mocked_date(MenuFactory, datetime(2020, 11, 12, 12, 12, 12, tzinfo=timezone.utc))
        DishFactory(menu=menu4)

        path = reverse('menu-list')
        payload = {
            'created__gte': self.transform_date(menu2.created),
            'created__lte': self.transform_date(menu3.created)
        }
        response = self.client.get(path, data=payload)

        expected = [self.transform_menu(menu) for menu in [menu2, menu3]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.json(), expected)

    def test_should_raise_if_filter_with_wrong_date_format(self):
        path = reverse('menu-list')
        payload = {
            'created__gte': '666-wrong-format'
        }

        response = self.client.get(path, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'created__gte': ['Enter a valid date/time.']})

    @classmethod
    def transform_dish(cls, dish: Dish):
        return {
            'id': dish.id,
            'name': dish.name,
            'description': dish.description,
            'price': str(dish.price),
            'prepare_time': duration_string(dish.prepare_time),
            'is_vegetarian': dish.is_vegetarian,
            'modified': cls.transform_date(dish.modified),
            'created': cls.transform_date(dish.created),
            'picture': dish.picture.url if dish.picture else None
        }

    @classmethod
    def transform_menu(cls, menu: Menu):
        return {
            'id': menu.id,
            'name': menu.name,
            'description': menu.description,
            'modified': cls.transform_date(menu.modified),
            'created': cls.transform_date(menu.created)
        }

    @staticmethod
    def call_with_mocked_date(obj, date):
        with patch('django.utils.timezone.now') as current_date:
            current_date.return_value = date
            return obj()
