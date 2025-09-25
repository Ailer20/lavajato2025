from django.contrib import admin
from django.utils.html import format_html
from .models import Lavagem
from .agendamento_models import Agendamento


@admin.register(Lavagem)
class LavagemAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'placa_veiculo', 'status_colored', 'base', 
        'tipo_lavagem', 'get_lavadores', 'data_lavagem', 'valor_final'
    ]
    list_filter = [
        'status', 'base', 'tipo_lavagem', 'transporte_equipamento',
        'data_lavagem'
    ]
    search_fields = [
        'codigo', 'placa_veiculo', 'cliente__nome', 'lavadores__nome', 
        'observacoes'
    ]
    ordering = ['-data_lavagem', '-hora_inicio']
    readonly_fields = ['codigo', 'duracao_lavagem']
    def get_lavadores(self, obj):
        return ", ".join([lavador.nome for lavador in obj.lavadores.all()])
    get_lavadores.short_description = 'Lavadores'


    fieldsets = (
        ('Informações Básicas', {
            'fields': ('codigo', 'status', 'data_lavagem')
        }),
        ('Veículo e Cliente', {
            'fields': ('placa_veiculo', 'cliente', 'veiculo')
        }),
        ('Local e Serviço', {
            'fields': ('base', 'tipo_lavagem', 'transporte_equipamento', 'lavador')
        }),
        ('Horários', {
            'fields': ('hora_inicio', 'hora_termino', 'duracao_lavagem')
        }),
        ('Valores', {
            'fields': ('valor_servico', 'desconto', 'valor_final')
        }),
        ('Observações', {
            'fields': ('contrato', 'observacoes')
        }),
    )

    def status_colored(self, obj):
        colors = {
            'EM_ANDAMENTO': 'orange',
            'CONCLUIDA': 'green',
            'CANCELADA': 'red',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'

    def duracao_lavagem(self, obj):
        duracao = obj.duracao_lavagem
        if duracao:
            return f"{duracao} minutos"
        return "Em andamento"
    duracao_lavagem.short_description = 'Duração'

    actions = ['marcar_como_concluida']

    def marcar_como_concluida(self, request, queryset):
        count = 0
        for lavagem in queryset:
            if lavagem.status == 'EM_ANDAMENTO':
                lavagem.concluir_lavagem()
                count += 1
        self.message_user(request, f'{count} lavagens marcadas como concluídas.')
    marcar_como_concluida.short_description = 'Marcar como concluída'


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'placa_veiculo', 'status_colored', 'data_agendamento', 
        'hora_agendamento', 'cliente', 'base', 'local', 'valor_estimado'
    ]
    list_filter = [
        'status', 'prioridade', 'base', 'local', 'tipo_lavagem', 
        'data_agendamento'
    ]
    search_fields = [
        'codigo', 'placa_veiculo', 'cliente__nome', 'telefone_contato',
        'email_contato', 'observacoes'
    ]
    ordering = ['data_agendamento', 'hora_agendamento']
    readonly_fields = ['codigo', 'data_hora_agendamento', 'esta_vencido']
    date_hierarchy = 'data_agendamento'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('codigo', 'status', 'prioridade', 'data_agendamento', 'hora_agendamento', 'duracao_estimada')
        }),
        ('Cliente e Veículo', {
            'fields': ('cliente', 'placa_veiculo', 'veiculo')
        }),
        ('Local e Serviço', {
            'fields': ('base', 'tipo_lavagem', 'transporte_equipamento', 'lavadores')
        }),
        ('Contato', {
            'fields': ('telefone_contato', 'email_contato')
        }),
        ('Valores', {
            'fields': ('valor_estimado', 'desconto_agendamento')
        }),
        ('Observações', {
            'fields': ('observacoes', 'observacoes_internas')
        }),
        ('Controle', {
            'fields': ('confirmado_em', 'confirmado_por', 'cancelado_em', 'motivo_cancelamento'),
            'classes': ('collapse',)
        }),
        ('Lavagem Relacionada', {
            'fields': ('lavagem',),
            'classes': ('collapse',)
        }),
    )

    def status_colored(self, obj):
        colors = {
            'AGENDADO': 'blue',
            'CONFIRMADO': 'green',
            'EM_ANDAMENTO': 'orange',
            'CONCLUIDO': 'darkgreen',
            'CANCELADO': 'red',
            'NAO_COMPARECEU': 'purple',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'

    def data_hora_agendamento(self, obj):
        if obj.data_hora_agendamento:
            return obj.data_hora_agendamento.strftime('%d/%m/%Y %H:%M')
        return '-'
    data_hora_agendamento.short_description = 'Data/Hora'

    def esta_vencido(self, obj):
        if obj.esta_vencido:
            return format_html('<span style="color: red;">✗ Vencido</span>')
        else:
            return format_html('<span style="color: green;">✓ No prazo</span>')
    esta_vencido.short_description = 'Status Prazo'

    actions = ['confirmar_agendamentos', 'cancelar_agendamentos', 'iniciar_lavagens']

    def confirmar_agendamentos(self, request, queryset):
        count = 0
        for agendamento in queryset:
            if agendamento.status == 'AGENDADO':
                agendamento.confirmar_agendamento(confirmado_por=request.user.username)
                count += 1
        self.message_user(request, f'{count} agendamentos confirmados.')
    confirmar_agendamentos.short_description = 'Confirmar agendamentos'

    def cancelar_agendamentos(self, request, queryset):
        count = 0
        for agendamento in queryset:
            if agendamento.pode_ser_cancelado:
                agendamento.cancelar_agendamento(motivo='Cancelado via admin')
                count += 1
        self.message_user(request, f'{count} agendamentos cancelados.')
    cancelar_agendamentos.short_description = 'Cancelar agendamentos'

    def iniciar_lavagens(self, request, queryset):
        count = 0
        for agendamento in queryset:
            if agendamento.pode_iniciar_lavagem:
                try:
                    agendamento.iniciar_lavagem()
                    count += 1
                except Exception as e:
                    self.message_user(request, f'Erro ao iniciar lavagem para {agendamento.codigo}: {str(e)}', level='ERROR')
        if count > 0:
            self.message_user(request, f'{count} lavagens iniciadas a partir dos agendamentos.')
    iniciar_lavagens.short_description = 'Iniciar lavagens'



from .models import TipoLavagem, Base, TransporteEquipamento





@admin.register(TipoLavagem)
class TipoLavagemAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco_base')
    search_fields = ('nome',)

@admin.register(Base)
class BaseAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(TransporteEquipamento)
class TransporteEquipamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'multiplicador_preco')
    search_fields = ('nome',)


