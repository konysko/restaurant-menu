from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework import viewsets, mixins, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response

from .filters import DishesCountOrdering
from .models import Menu, Dish
from .serializers import MenuSerializer, DishSerializer


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


class MenuManageViewSet(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [DjangoModelPermissions]

    def get_serializer(self, *args, **kwargs):
        kwargs['fields'] = set(MenuSerializer.Meta.fields) - {'dishes'}
        return super().get_serializer(*args, **kwargs)


class DishManageViewSet(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [DjangoModelPermissions]

    def get_serializer(self, *args, **kwargs):
        if self.action == 'picture':
            kwargs['fields'] = ['picture']
        else:
            kwargs['fields'] = set(DishSerializer.Meta.fields) - {'picture'}
        return super().get_serializer(*args, **kwargs)

    @action(
        methods=['PUT', 'DELETE'],
        detail=True,
        parser_classes=[MultiPartParser, FormParser]
    )
    def picture(self, request, pk):
        if request.method == 'PUT':
            super().update(request, pk)
        elif request.method == 'DELETE':
            super().destroy(request, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        if self.action == 'picture':
            return instance.picture.delete()
        return super().perform_destroy(instance)
