from datetime import timedelta

import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText, FuzzyChoice, FuzzyDecimal

from menu.models import Menu, Dish


class MenuFactory(DjangoModelFactory):
    class Meta:
        model = Menu

    name = factory.Sequence(lambda n: f'name{n}')
    description = FuzzyText(length=50)


class DishFactory(DjangoModelFactory):
    class Meta:
        model = Dish

    name = factory.Sequence(lambda n: f'name{n}')
    description = FuzzyText(length=50)
    prepare_time = timedelta(minutes=40)
    price = FuzzyDecimal(low=1, high=99)
    is_vegetarian = FuzzyChoice([False, True])

    menu = factory.SubFactory(MenuFactory)
