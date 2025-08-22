# No arquivo: lavagens/urls.py

from django.urls import path
# from . import views <-- REMOVA esta linha
# from . import agendamento_views as views <-- REMOVA esta linha

# --- PASSO 1: IMPORTE OS DOIS ARQUIVOS COM APELIDOS DIFERENTES ---
from . import views as lavagens_views
from . import agendamento_views as agendamento_views

urlpatterns = [
    # --- PASSO 2: USE O APELIDO CORRETO PARA CADA VIEW ---
    
    # Views principais de lavagens (usam lavagens_views)
    path('', lavagens_views.dashboard, name='dashboard'),
    path('nova/', lavagens_views.nova_lavagem, name='nova_lavagem'),
    path('detalhes/<int:lavagem_id>/', lavagens_views.detalhes_lavagem, name='detalhes_lavagem'),
    
    # Ações de lavagens (usam lavagens_views)
    path('concluir/<int:lavagem_id>/', lavagens_views.concluir_lavagem, name='concluir_lavagem'),
    path('cancelar/<int:lavagem_id>/', lavagens_views.cancelar_lavagem, name='cancelar_lavagem'),
    
    # Relatórios (usa lavagens_views)
    path('relatorios/', lavagens_views.relatorios, name='relatorios'),
    
    # APIs AJAX para lavagens (usam lavagens_views)
    path('api/locais-por-base/', lavagens_views.api_locais_por_base, name='api_locais_por_base'),
    path('api/buscar-veiculo/', lavagens_views.api_buscar_veiculo, name='api_buscar_veiculo'),
    
    # URLs de agendamentos (usam agendamento_views)
    # path('', include('lavagens.agendamento_urls')), <-- REMOVA esta linha, é redundante
    path('agendamentos/', agendamento_views.agendamentos_dashboard, name='agendamentos_dashboard'),
    path('agendamentos/novo/', agendamento_views.novo_agendamento, name='novo_agendamento'),
]

# --- PASSO 3: CORRIJA AS VIEWS DE CADASTRO (usam lavagens_views) ---
# URLs para Bases
urlpatterns += [
    path("bases/", lavagens_views.base_list, name="base_list"),
    path("bases/add/", lavagens_views.base_create, name="base_create"),
    path("bases/<int:pk>/edit/", lavagens_views.base_update, name="base_update"),
    path("bases/<int:pk>/delete/", lavagens_views.base_delete, name="base_delete"),
]

# URLs para Tipos de Lavagem
urlpatterns += [
    path("tipos-lavagem/", lavagens_views.tipo_lavagem_list, name="tipo_lavagem_list"),
    path("tipos-lavagem/add/", lavagens_views.tipo_lavagem_create, name="tipo_lavagem_create"),
    path("tipos-lavagem/<int:pk>/edit/", lavagens_views.tipo_lavagem_update, name="tipo_lavagem_update"),
    path("tipos-lavagem/<int:pk>/delete/", lavagens_views.tipo_lavagem_delete, name="tipo_lavagem_delete"),
]

# URLs para Transportes/Equipamentos
urlpatterns += [
    path("transportes-equipamentos/", lavagens_views.transporte_equipamento_list, name="transporte_equipamento_list"),
    path("transportes-equipamentos/add/", lavagens_views.transporte_equipamento_create, name="transporte_equipamento_create"),
    path("transportes-equipamentos/<int:pk>/edit/", lavagens_views.transporte_equipamento_update, name="transporte_equipamento_update"),
    path("transportes-equipamentos/<int:pk>/delete/", lavagens_views.transporte_equipamento_delete, name="transporte_equipamento_delete"),
]
