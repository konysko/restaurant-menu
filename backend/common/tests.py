from django.contrib.auth.models import User

from menu.management.commands.load_initial_data import Command


class TestUtilsMixin:
    def authenticate_user(self) -> User:
        self.user = User.objects.create_user(username='test', password='test')
        token = Command.create_token_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token['access'])
        return self.user

    def authenticate_and_add_modify_permissions(self):
        user = self.authenticate_user()
        group = Command.create_editors_group()
        user.groups.add(group)
        return user

    @staticmethod
    def transform_date(date):
        value = date.isoformat()
        if value.endswith('+00:00'):
            value = value[:-6] + 'Z'
        return value
