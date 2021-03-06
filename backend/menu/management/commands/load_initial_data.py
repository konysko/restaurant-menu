from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from rest_framework_simplejwt.tokens import RefreshToken

from menu.models import Menu, Dish
from menu.tests.factories import MenuFactory, DishFactory


class Command(BaseCommand):
    def handle(self, *args, **options):
        user_data = {
            'username': 'user',
            'email': 'mail@test.pl',
            'password': 'password'
        }
        user = self.create_user(**user_data)
        editors_group = self.create_editors_group()
        user.groups.add(editors_group)
        self.stdout.write(f'Created user with data: {user_data}')
        token = self.create_token_for_user(user)
        self.stdout.write(f'JWT token for authentication: Bearer f{token["access"]}')
        self.create_menus()
        self.stdout.write('Created menus')

    @staticmethod
    def create_user(username, email, password):
        return User.objects.create_user(username, email, password)

    @staticmethod
    def create_editors_group():
        menu_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Menu)
        )
        dish_permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Dish)
        )
        group = Group.objects.create(
            name='editors'
        )
        group.permissions.add(
            *menu_permissions,
            *dish_permissions
        )
        return group

    @staticmethod
    def create_menus():
        MenuFactory()
        menus = MenuFactory.create_batch(3)
        for menu in menus:
            DishFactory.create_batch(3, menu=menu)

    @staticmethod
    def create_token_for_user(user: User):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
