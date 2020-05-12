from typing import List

from django.db.models import Count, QuerySet
from rest_framework.filters import BaseFilterBackend
from django_filters import rest_framework as filters
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

from .models import Menu, Dish


class DishesCountOrdering(BaseFilterBackend):
    value = 'dishes_count'

    def filter_queryset(self, request: Request, queryset: 'QuerySet[Dish]', view: GenericViewSet) -> 'QuerySet[Dish]':
        params = request.query_params.get('ordering', '').split(',')
        ordering_value = self.get_ordering_value(params)
        if not ordering_value:
            return queryset

        return queryset.annotate(dishes_count=Count('dishes')).order_by(ordering_value)

    def get_ordering_value(self, params: List[str]) -> str:
        for param in params:
            descending = param.startswith('-')
            param = param[1:] if descending else param
            if param == self.value:
                return '-%s' % param if descending else param
        return ''


class MenuFilterSet(filters.FilterSet):
    class Meta:
        model = Menu
        fields = ('modified', 'created')

    modified = filters.IsoDateTimeFromToRangeFilter()
    created = filters.IsoDateTimeFromToRangeFilter()
