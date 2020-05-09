from common.serializers import DynamicFieldsModelSerializer
from menu.models import Menu, Dish


class DishSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Dish
        fields = ('id', 'name', 'description', 'price', 'prepare_time', 'is_vegetarian', 'modified', 'created', 'menu')


class MenuSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Menu
        fields = ('id', 'name', 'description', 'modified', 'created', 'dishes')
        dishes_fields = set(DishSerializer.Meta.fields) - {'menu'}

    dishes = DishSerializer(many=True, fields=Meta.dishes_fields)
