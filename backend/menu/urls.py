from rest_framework import routers

from .viewsets import MenuReadOnlyViewSet

router = routers.SimpleRouter()
router.register(r'menu', MenuReadOnlyViewSet, 'menu')

urlpatterns = router.urls
