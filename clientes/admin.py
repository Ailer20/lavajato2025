from django.contrib import admin
from .models import Cliente, Veiculo, Lavador


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'email', 'ativo']
    list_filter = ["ativo"]
    search_fields = ['nome', 'telefone', 'email']
    ordering = ['nome']


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ['placa', 'marca', 'modelo', 'ano', 'tipo', 'cliente', 'ativo']
    list_filter = ["tipo", "marca", "ativo"]
    search_fields = ['placa', 'marca', 'modelo', 'cliente__nome']
    ordering = ['placa']


@admin.register(Lavador)
class LavadorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'telefone', 'data_admissao', 'ativo']
    list_filter = ["ativo", "data_admissao"]
    search_fields = ['nome', 'cpf', 'telefone']
    ordering = ['nome']

