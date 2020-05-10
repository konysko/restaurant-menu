from rest_framework import routers

from .viewsets import MenuReadOnlyViewSet, MenuManageViewSet, DishManageViewSet

router = routers.SimpleRouter()
router.register(r'manage/menu/dish', DishManageViewSet, 'dish-manage')
router.register(r'manage/menu', MenuManageViewSet, 'menu-manage')
router.register(r'menu', MenuReadOnlyViewSet, 'menu')
urlpatterns = router.urls
