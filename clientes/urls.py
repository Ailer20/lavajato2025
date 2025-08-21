from django.urls import path
from . import views

urlpatterns = [
    path("clientes/", views.cliente_list, name="cliente_list"),
    path("clientes/add/", views.cliente_create, name="cliente_create"),
    path("clientes/<int:pk>/edit/", views.cliente_update, name="cliente_update"),
    path("clientes/<int:pk>/delete/", views.cliente_delete, name="cliente_delete"),

    path("veiculos/", views.veiculo_list, name="veiculo_list"),
    path("veiculos/add/", views.veiculo_create, name="veiculo_create"),
    path("veiculos/<int:pk>/edit/", views.veiculo_update, name="veiculo_update"),
    path("veiculos/<int:pk>/delete/", views.veiculo_delete, name="veiculo_delete"),

    path("lavadores/", views.lavador_list, name="lavador_list"),
    path("lavadores/add/", views.lavador_create, name="lavador_create"),
    path("lavadores/<int:pk>/edit/", views.lavador_update, name="lavador_update"),
    path("lavadores/<int:pk>/delete/", views.lavador_delete, name="lavador_delete"),
]


