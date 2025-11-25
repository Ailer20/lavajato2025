from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import LavagemViewSet
from .agendamento_views import AgendamentoViewSet  # <--- Importe o AgendamentoViewSet

# Criar router UNIFICADO para todas as APIs
router = DefaultRouter()
router.register(r'lavagens', LavagemViewSet)
router.register(r'agendamentos', AgendamentoViewSet) # <--- Registre aqui

urlpatterns = [
    path('', include(router.urls)),
]