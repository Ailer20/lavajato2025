from django.urls import path, include
from . import views

urlpatterns = [
    # Views principais de lavagens
    path('', views.dashboard, name='dashboard'),
    path('nova/', views.nova_lavagem, name='nova_lavagem'),
    path('detalhes/<int:lavagem_id>/', views.detalhes_lavagem, name='detalhes_lavagem'),
    
    # Ações de lavagens
    path('concluir/<int:lavagem_id>/', views.concluir_lavagem, name='concluir_lavagem'),
    path('cancelar/<int:lavagem_id>/', views.cancelar_lavagem, name='cancelar_lavagem'),
    
    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    
    # APIs AJAX para lavagens
    path('api/locais-por-base/', views.api_locais_por_base, name='api_locais_por_base'),
    path('api/buscar-veiculo/', views.api_buscar_veiculo, name='api_buscar_veiculo'),
    
    # URLs de agendamentos
    path('', include('lavagens.agendamento_urls')),
]




# URLs para Bases
urlpatterns += [
    path("bases/", views.base_list, name="base_list"),
    path("bases/add/", views.base_create, name="base_create"),
    path("bases/<int:pk>/edit/", views.base_update, name="base_update"),
    path("bases/<int:pk>/delete/", views.base_delete, name="base_delete"),
]

# URLs para Tipos de Lavagem
urlpatterns += [
    path("tipos-lavagem/", views.tipo_lavagem_list, name="tipo_lavagem_list"),
    path("tipos-lavagem/add/", views.tipo_lavagem_create, name="tipo_lavagem_create"),
    path("tipos-lavagem/<int:pk>/edit/", views.tipo_lavagem_update, name="tipo_lavagem_update"),
    path("tipos-lavagem/<int:pk>/delete/", views.tipo_lavagem_delete, name="tipo_lavagem_delete"),
]

# URLs para Transportes/Equipamentos
urlpatterns += [
    path("transportes-equipamentos/", views.transporte_equipamento_list, name="transporte_equipamento_list"),
    path("transportes-equipamentos/add/", views.transporte_equipamento_create, name="transporte_equipamento_create"),
    path("transportes-equipamentos/<int:pk>/edit/", views.transporte_equipamento_update, name="transporte_equipamento_update"),
    path("transportes-equipamentos/<int:pk>/delete/", views.transporte_equipamento_delete, name="transporte_equipamento_delete"),
]


