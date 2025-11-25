from django.urls import path
from . import views

urlpatterns = [
    path('estoque/', views.estoque_lista, name='estoque_lista'),
    path('estoque/produto/novo/', views.produto_create, name='produto_create'),
    path('estoque/produto/<int:pk>/editar/', views.produto_update, name='produto_update'),
    
    path('estoque/historico/<int:produto_id>/', views.historico_produto, name='historico_produto'),
    
    # URL ÚNICA DE SAÍDA (Substitui a antiga atribuir)
    path('estoque/saida/', views.registrar_saida, name='saida_estoque'),
    
    path('meu-estoque/', views.meu_estoque_pessoal, name='meu_estoque_pessoal'),
    path('meu-estoque/devolver/', views.registrar_devolucao, name='devolucao_estoque'), # Nome da view corrigido
    
    path('notas/', views.nota_fiscal_lista, name='nota_fiscal_lista'),
    path('notas/nova/', views.nota_fiscal_create, name='nota_fiscal_create'),
    # Categorias
    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/nova/', views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_update, name='categoria_update'),

    # Locais
    path('locais/', views.local_lista, name='local_lista'),
    path('locais/novo/', views.local_create, name='local_create'),
    path('locais/<int:pk>/editar/', views.local_update, name='local_update'),
]