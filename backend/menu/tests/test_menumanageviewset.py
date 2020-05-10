from datetime import datetime, timezone
from unittest.mock import patch

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from common.tests import TestUtilsMixin
from menu.models import Menu, Dish
from menu.tests.factories import MenuFactory, DishFactory


class TestCaseMenuManageViewSet(TestUtilsMixin, APITestCase):
    def test_should_create_menu(self):
        self.authenticate_and_add_modify_permissions()
        payload = {
            'name': 'test name',
            'description': 'dsfdsf'
        }
        path = reverse('menu-manage-list')

        response = self.client.post(path, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = Menu.objects.get(pk=response.json()['id'])
        self.assertEqual(payload['name'], expected.name)
        self.assertEqual(payload['description'], expected.description)

    def test_should_update_modified_on_edit(self):
        self.authenticate_and_add_modify_permissions()
        payload = {
            'description': 'newdesc'
        }
        menu = MenuFactory()
        path = reverse('menu-manage-detail', args=[menu.id])
        mocked_date = datetime(2019, 12, 12, 12, 12, 12, tzinfo=timezone.utc)

        with patch('django.utils.timezone.now') as current_date:
            current_date.return_value = mocked_date
            response = self.client.patch(path, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        menu.refresh_from_db()
        self.assertEqual(menu.modified, mocked_date)

    def test_should_update_created_on_creation(self):
        self.authenticate_and_add_modify_permissions()
        payload = {
            'name': 'newname',
            'description': 'sdf'
        }
        path = reverse('menu-manage-list')
        mocked_date = datetime(2019, 12, 12, 12, 12, 12, tzinfo=timezone.utc)

        with patch('django.utils.timezone.now') as current_date:
            current_date.return_value = mocked_date
            response = self.client.post(path, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = Menu.objects.get(pk=response.json()['id'])
        self.assertEqual(expected.created, mocked_date)

    def test_should_raise_if_name_already_exist(self):
        self.authenticate_and_add_modify_permissions()
        menu = MenuFactory()
        payload = {
            'name': menu.name,
            'description': 'sdescf'
        }
        path = reverse('menu-manage-list')

        response = self.client.post(path, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'name': ['menu with this name already exists.']})

    def test_should_edit_menu(self):
        self.authenticate_and_add_modify_permissions()
        menu = MenuFactory()
        payload = {
            'name': 'test'
        }
        path = reverse('menu-manage-detail', args=[menu.id])

        response = self.client.patch(path, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        menu.refresh_from_db()
        self.assertEqual(menu.name, payload['name'])

    def test_should_delete_menu_with_all_dishes(self):
        self.authenticate_and_add_modify_permissions()
        menu = MenuFactory()
        DishFactory(menu=menu)
        path = reverse('menu-manage-detail', args=[menu.id])

        response = self.client.delete(path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Menu.objects.count(), 0)
        self.assertEqual(Dish.objects.count(), 0)

    def test_should_raise_if_not_authorized(self):
        self.authenticate_user()
        payload = {
            'name': 'test',
            'description': 'test'
        }
        path = reverse('menu-manage-list')

        response = self.client.post(path, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'detail': 'You do not have permission to perform this action.'})
