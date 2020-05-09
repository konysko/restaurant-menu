from django.db.models import Prefetch
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .filters import DishesCountOrdering
from .models import Menu, Dish
from .serializers import MenuSerializer


class MenuReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MenuSerializer
    filter_backends = [DishesCountOrdering, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['name']
    filterset_fields = {
        'modified': ['lte', 'gte'],
        'created': ['lte', 'gte']
    }

    def get_queryset(self):
        if self.action == 'list':
            return Menu.objects.filter(dishes__isnull=False).distinct().order_by('pk')
        return Menu.objects.prefetch_related(
            Prefetch('dishes', queryset=Dish.objects.order_by('pk'))
        )

    def get_serializer(self, *args, **kwargs):
        if self.action == 'list':
            kwargs['fields'] = set(MenuSerializer.Meta.fields) - {'dishes'}
        return super().get_serializer(*args, **kwargs)
