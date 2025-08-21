from rest_framework import serializers
from django.utils import timezone
from .agendamento_models import Agendamento
from .models import Lavagem
from clientes.models import Cliente, Veiculo, Lavador


class AgendamentoListSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    lavador_nome = serializers.CharField(source='lavador.nome', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)
    data_hora_agendamento = serializers.DateTimeField(read_only=True)
    esta_vencido = serializers.BooleanField(read_only=True)
    pode_ser_cancelado = serializers.BooleanField(read_only=True)
    pode_iniciar_lavagem = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Agendamento
        fields = [
            'id', 'codigo', 'placa_veiculo', 'data_agendamento', 'hora_agendamento',
            'status', 'status_display', 'prioridade', 'prioridade_display',
            'cliente_nome', 'base', 'local', 'tipo_lavagem', 'transporte_equipamento', 'lavador_nome',
            'valor_estimado', 'telefone_contato', 'observacoes',
            'data_hora_agendamento', 'esta_vencido', 'pode_ser_cancelado', 'pode_iniciar_lavagem',
            'created_at'
        ]


class AgendamentoDetailSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    veiculo_info = serializers.SerializerMethodField()
    lavador_nome = serializers.CharField(source='lavador.nome', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)
    data_hora_agendamento = serializers.DateTimeField(read_only=True)
    horario_fim_estimado = serializers.SerializerMethodField()
    esta_vencido = serializers.BooleanField(read_only=True)
    pode_ser_cancelado = serializers.BooleanField(read_only=True)
    pode_iniciar_lavagem = serializers.BooleanField(read_only=True)
    lavagem_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Agendamento
        fields = '__all__'
    
    def get_veiculo_info(self, obj):
        if obj.veiculo:
            return {
                'id': obj.veiculo.id,
                'marca': obj.veiculo.marca,
                'modelo': obj.veiculo.modelo,
                'ano': obj.veiculo.ano,
                'cor': obj.veiculo.cor
            }
        return None
    
    def get_horario_fim_estimado(self, obj):
        horario_fim = obj.get_horario_fim_estimado()
        if horario_fim:
            return horario_fim.strftime('%H:%M')
        return None
    
    def get_lavagem_info(self, obj):
        if obj.lavagem:
            return {
                'id': obj.lavagem.id,
                'codigo': obj.lavagem.codigo,
                'status': obj.lavagem.status,
                'status_display': obj.lavagem.get_status_display()
            }
        return None


class AgendamentoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = [
            'cliente', 'veiculo', 'placa_veiculo', 'base', 'local',
            'tipo_lavagem', 'transporte_equipamento', 'lavador',
            'data_agendamento', 'hora_agendamento', 'duracao_estimada',
            'prioridade', 'telefone_contato', 'email_contato',
            'observacoes', 'observacoes_internas'
        ]
    
    def validate_data_agendamento(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Não é possível agendar para uma data no passado.")
        return value
    
    def validate_hora_agendamento(self, value):
        if value.hour < 6 or value.hour >= 18:
            raise serializers.ValidationError("Agendamentos só podem ser feitos entre 6h e 18h.")
        return value
    
    def validate(self, data):
        data_agendamento = data.get('data_agendamento')
        hora_agendamento = data.get('hora_agendamento')
        local = data.get('local')
        
        if data_agendamento and hora_agendamento and local:
            conflito = Agendamento.objects.filter(
                data_agendamento=data_agendamento,
                hora_agendamento=hora_agendamento,
                local=local,
                status__in=['AGENDADO', 'CONFIRMADO']
            ).exists()
            
            if conflito:
                raise serializers.ValidationError(
                    "Já existe um agendamento para este horário e local."
                )
        
        return data


class AgendamentoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = [
            'data_agendamento', 'hora_agendamento', 'duracao_estimada',
            'prioridade', 'telefone_contato', 'email_contato',
            'observacoes', 'observacoes_internas', 'lavador'
        ]
    
    def validate(self, data):
        if self.instance.status not in ['AGENDADO', 'CONFIRMADO']:
            raise serializers.ValidationError(
                "Só é possível alterar agendamentos com status 'Agendado' ou 'Confirmado'."
            )
        return data


class AgendamentoStatusSerializer(serializers.Serializer):
    STATUS_CHOICES = [
        ('CONFIRMADO', 'Confirmar'),
        ('CANCELADO', 'Cancelar'),
        ('NAO_COMPARECEU', 'Não Compareceu'),
    ]
    
    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    motivo = serializers.CharField(required=False, allow_blank=True, max_length=500)
    confirmado_por = serializers.CharField(required=False, allow_blank=True, max_length=100)
    
    def validate(self, data):
        agendamento = self.context['agendamento']
        novo_status = data['status']
        
        if novo_status == 'CONFIRMADO' and agendamento.status != 'AGENDADO':
            raise serializers.ValidationError("Só é possível confirmar agendamentos com status 'Agendado'.")
        
        if novo_status == 'CANCELADO' and not agendamento.pode_ser_cancelado:
            raise serializers.ValidationError("Este agendamento não pode ser cancelado.")
        
        if novo_status == 'CANCELADO' and not data.get('motivo'):
            raise serializers.ValidationError("É obrigatório informar o motivo do cancelamento.")
        
        return data


class IniciarLavagemSerializer(serializers.Serializer):
    hora_inicio = serializers.DateTimeField(required=False)
    observacoes_adicionais = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate(self, data):
        agendamento = self.context['agendamento']
        
        if not agendamento.pode_iniciar_lavagem:
            raise serializers.ValidationError("Este agendamento não pode ser convertido em lavagem.")
        
        if not data.get('hora_inicio'):
            data['hora_inicio'] = timezone.now()
        
        return data


class AgendamentoCalendarioSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    
    class Meta:
        model = Agendamento
        fields = ['id', 'codigo', 'title', 'start', 'end', 'color', 'status']
    
    def get_title(self, obj):
        return f"{obj.placa_veiculo} - {obj.cliente.nome if obj.cliente else 'Cliente não informado'}"
    
    def get_start(self, obj):
        if obj.data_hora_agendamento:
            return obj.data_hora_agendamento.isoformat()
        return None
    
    def get_end(self, obj):
        horario_fim = obj.get_horario_fim_estimado()
        if horario_fim:
            return horario_fim.isoformat()
        return None
    
    def get_color(self, obj):
        colors = {
            'AGENDADO': '#007bff',
            'CONFIRMADO': '#28a745',
            'EM_ANDAMENTO': '#ffc107',
            'CONCLUIDO': '#6f42c1',
            'CANCELADO': '#dc3545',
            'NAO_COMPARECEU': '#6c757d'
        }
        return colors.get(obj.status, '#007bff')


