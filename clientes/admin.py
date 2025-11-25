from django.contrib import admin
from .models import Cliente, Veiculo, Lavador

@admin.register(Lavador)
class LavadorAdmin(admin.ModelAdmin):
    # Adicione 'usuario' na lista para facilitar a visualização
    list_display = ['nome', 'usuario', 'cpf', 'matricula', 'ativo']
    
    # Adicione 'usuario' na busca
    search_fields = ['nome', 'cpf', 'usuario__username']
    
    # Garante que o campo apareça no formulário de edição
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome', 'cpf', 'telefone', 'data_admissao')
        }),
        ('Vínculo com Sistema', {
            'fields': ('usuario', 'matricula'), # <--- O CAMPO DEVE ESTAR AQUI
            'description': 'Vincule um usuário de login a este colaborador para acesso ao sistema.'
        }),
        ('Contrato', {
            'fields': ('salario', 'jornada_trabalho', 'escala_trabalho', 'ativo', 'observacoes')
        }),
    )

# ... (Mantenha os outros admins de Cliente e Veiculo) ...
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'email', 'ativo']
    search_fields = ['nome']

@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ['placa', 'modelo', 'cliente']
    search_fields = ['placa']