from rest_framework import serializers

from common.serializers import DynamicFieldsModelSerializer

from .models import Menu, Dish


class DishSerializer(DynamicFieldsModelSerializer):
    menu = serializers.SlugRelatedField(
        queryset=Menu.objects.all(),
        slug_field='name',
        write_only=True
    )

    class Meta:
        model = Dish
        fields = (
            'id', 'name', 'description', 'price', 'prepare_time', 'is_vegetarian', 'modified', 'created', 'menu',
            'picture'
        )


class MenuSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Menu
        fields = ('id', 'name', 'description', 'modified', 'created', 'dishes')

    dishes = DishSerializer(many=True)
