from django.urls import path
from . import agendamento_views

# REMOVA o router e as rotas de API deste arquivo. Deixe apenas as views normais (HTML).

urlpatterns = [
    # Views Django tradicionais (Telas HTML)
    path('agendamentos/', agendamento_views.agendamentos_dashboard, name='agendamentos_dashboard'),
    path('agendamentos/novo/', agendamento_views.novo_agendamento, name='novo_agendamento'),
    path('agendamentos/<int:agendamento_id>/', agendamento_views.detalhes_agendamento, name='detalhes_agendamento'),
    path('agendamentos/<int:agendamento_id>/confirmar/', agendamento_views.confirmar_agendamento, name='confirmar_agendamento'),
    path('agendamentos/<int:agendamento_id>/cancelar/', agendamento_views.cancelar_agendamento, name='cancelar_agendamento'),
    path('agendamentos/<int:agendamento_id>/iniciar-lavagem/', agendamento_views.iniciar_lavagem_agendamento, name='iniciar_lavagem_agendamento'),
    path('agendamentos/calendario/', agendamento_views.calendario_agendamentos, name='calendario_agendamentos'),
    
    # APIs AJAX manuais (usadas nos selects do formulário, mantenha estas se ainda estiver usando jQuery/AJAX direto)
    path('api/locais-por-base/', agendamento_views.api_locais_por_base, name='api_locais_por_base'),
    path('api/verificar-disponibilidade/', agendamento_views.api_verificar_disponibilidade, name='api_verificar_disponibilidade'),
]