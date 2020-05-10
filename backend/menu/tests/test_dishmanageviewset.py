from io import BytesIO

from django.core.files import File
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from common.tests import TestUtilsMixin
from menu.models import Dish
from menu.tests.factories import MenuFactory, DishFactory


class TestCaseDishManageViewSet(TestUtilsMixin, APITestCase):
    picture_path = 'menu/tests/mocks/picture.jpeg'

    def test_should_create_dish(self):
        self.authenticate_and_add_modify_permissions()
        menu = MenuFactory()
        payload = {
            'name': 'testnam',
            'price': '33.34',
            'prepare_time': '0:30:00',
            'is_vegetarian': False,
            'description': 'testdesc',
            'menu': menu.name
        }
        path = reverse('dish-manage-list')

        response = self.client.post(path, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected = Dish.objects.get(pk=response.json()['id'])

        self.assertEqual(payload['name'], expected.name)
        self.assertEqual(payload['price'], str(expected.price))
        self.assertEqual(payload['prepare_time'], str(expected.prepare_time))
        self.assertEqual(payload['is_vegetarian'], expected.is_vegetarian)
        self.assertEqual(payload['menu'], expected.menu.name)

    def test_should_raise_if_menu_doesnt_exist(self):
        self.authenticate_and_add_modify_permissions()
        payload = {
            'name': 'testnam',
            'price': '33.34',
            'description': 'testdesc',
            'prepare_time': '00:30:00',
            'is_vegetarian': False,
            'menu': 'testname'
        }
        path = reverse('dish-manage-list')

        response = self.client.post(path, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'menu': ['Object with name=testname does not exist.']})

    def test_should_edit_dish(self):
        self.authenticate_and_add_modify_permissions()
        dish = DishFactory()
        payload = {
            'price': '22.34',
        }
        path = reverse('dish-manage-detail', args=[dish.id])

        response = self.client.patch(path, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dish.refresh_from_db()
        self.assertEqual(str(dish.price), payload['price'])

    def test_should_raise_if_dish_name_already_exist(self):
        self.authenticate_and_add_modify_permissions()
        dish = DishFactory()
        dish1 = DishFactory()
        payload = {
            'name': dish1.name
        }
        path = reverse('dish-manage-detail', args=[dish.id])

        response = self.client.patch(path, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'name': ['dish with this name already exists.']})

    def test_should_raise_if_price_out_of_range(self):
        self.authenticate_and_add_modify_permissions()
        dish = DishFactory()
        payload = {
            'price': '334.444'
        }
        path = reverse('dish-manage-detail', args=[dish.id])

        response = self.client.patch(path, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {'price': ['Ensure that there are no more than 4 digits in total.']}
        )

    def test_should_raise_if_wrong_format_of_prepare_time(self):
        self.authenticate_and_add_modify_permissions()
        dish = DishFactory()
        payload = {
            'prepare_time': '30m'
        }
        path = reverse('dish-manage-detail', args=[dish.id])

        response = self.client.patch(path, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {'prepare_time': [
                'Duration has wrong format. Use one of these formats instead: [DD] [HH:[MM:]]ss[.uuuuuu].'
            ]}
        )

    def test_should_upload_a_picture(self):
        self.authenticate_and_add_modify_permissions()
        dish = DishFactory()
        payload = {
            'picture': File(open(self.picture_path, 'rb'))
        }
        path = reverse('dish-manage-picture', args=[dish.id])

        response = self.client.put(path, payload)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        dish.refresh_from_db()
        self.assertEqual(dish.picture.read(), open(self.picture_path, 'rb').read())

    def test_should_raise_if_wrong_picture_format(self):
        self.authenticate_and_add_modify_permissions()
        wrong_picture = BytesIO(b'somebytes')
        payload = {
            'picture': File(wrong_picture)
        }
        dish = DishFactory()
        path = reverse('dish-manage-picture', args=[dish.id])

        response = self.client.put(path, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {'picture': ['Upload a valid image. The file you uploaded was either not an image or a corrupted image.']}
        )

    def test_should_remove_picture(self):
        self.authenticate_and_add_modify_permissions()
        dish = DishFactory()
        dish.picture = File(open(self.picture_path, 'rb'))
        dish.save()
        path = reverse('dish-manage-picture', args=[dish.id])

        response = self.client.delete(path)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        dish.refresh_from_db()
        self.assertFalse(dish.picture)

    def test_should_raise_if_not_authenticated(self):
        self.authenticate_user()
        payload = {
            'name': 'test'
        }
        path = reverse('dish-manage-list')

        response = self.client.post(path, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {'detail': 'You do not have permission to perform this action.'})
