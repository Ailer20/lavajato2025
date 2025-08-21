from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    LavagemViewSet
)

# Criar router para as APIs
router = DefaultRouter()
router.register(r'lavagens', LavagemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]


