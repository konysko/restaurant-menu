from typing import Union, Type, Any

from django.db.models import Prefetch, QuerySet
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework import viewsets, mixins, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.request import Request
from rest_framework.response import Response

from .filters import DishesCountOrdering, MenuFilterSet
from .models import Menu, Dish
from .serializers import MenuSerializer, DishSerializer, MenuDishesSerializer


@method_decorator(name='list', decorator=swagger_auto_schema(
    manual_parameters=[openapi.Parameter(
        name='ordering',
        in_=openapi.IN_QUERY,
        description='name, -name, dishes_count, -dishes_count',
        type=openapi.TYPE_STRING
    )]
))
class MenuReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    filter_backends = [DishesCountOrdering, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['name']
    filterset_class = MenuFilterSet

    def get_queryset(self) -> 'QuerySet[Menu]':
        if self.action == 'list':
            return Menu.objects.filter(dishes__isnull=False).distinct().order_by('pk')
        return Menu.objects.prefetch_related(
            Prefetch('dishes', queryset=Dish.objects.order_by('pk'))
        )

    def get_serializer_class(self) -> Type[Union[MenuSerializer, MenuDishesSerializer]]:
        if self.action == 'list':
            return MenuSerializer
        return MenuDishesSerializer


class MenuManageViewSet(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [DjangoModelPermissions]


class DishManageViewSet(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [DjangoModelPermissions]

    def get_serializer(self, *args: Any, **kwargs: Any) -> DishSerializer:
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
    def picture(self, request: Request, pk: int) -> Response:
        if request.method == 'PUT':
            super().update(request, pk)
        elif request.method == 'DELETE':
            super().destroy(request, pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance: Dish) -> None:
        if self.action == 'picture':
            instance.picture.delete()
        else:
            super().perform_destroy(instance)
