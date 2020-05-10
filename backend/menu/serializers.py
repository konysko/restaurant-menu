from rest_framework import serializers

from common.serializers import DynamicFieldsModelSerializer

from .models import Menu, Dish


class DishSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Dish
        fields = (
            'id', 'name', 'description', 'price', 'prepare_time', 'is_vegetarian', 'modified', 'created', 'menu',
            'picture'
        )

    menu = serializers.SlugRelatedField(
        queryset=Menu.objects.all(),
        slug_field='name',
        write_only=True
    )


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ('id', 'name', 'description', 'modified', 'created')


class MenuDishesSerializer(MenuSerializer):
    class Meta:
        model = Menu
        fields = MenuSerializer.Meta.fields + ('dishes',)
        dish_fields = set(DishSerializer.Meta.fields) - {'menu'}

    dishes = DishSerializer(many=True, fields=Meta.dish_fields)
