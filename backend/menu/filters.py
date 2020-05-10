from django.db.models import Count
from rest_framework.filters import BaseFilterBackend
from rest_framework.compat import coreapi


class DishesCountOrdering(BaseFilterBackend):
    value = 'dishes_count'

    def filter_queryset(self, request, queryset, view):
        params = request.query_params.get('ordering', '').split(',')
        ordering_value = self.get_ordering_value(params)
        if not ordering_value:
            return queryset

        return queryset.annotate(dishes_count=Count('dishes')).order_by(ordering_value)

    def get_ordering_value(self, params):
        for param in params:
            descending = param.startswith('-')
            param = param[1:] if descending else param
            if param == self.value:
                return "-%s" % param if descending else param

    def get_schema_fields(self, view):
        # todo
        return coreapi.Field(
            name='ordering'
        )
