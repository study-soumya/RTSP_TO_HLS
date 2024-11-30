from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StreamAPIView


router = DefaultRouter()
router.register('streams', StreamAPIView)

urlpatterns = [
    path('', include(router.urls))
]