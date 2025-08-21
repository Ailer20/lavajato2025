from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from clientes.models import Cliente, Veiculo, Lavador
from clientes.models import Lavador
from decimal import Decimal


class Agendamento(models.Model):
    """
    Modelo para representar agendamentos de lavagens
    """
    STATUS_CHOICES = [
        ("AGENDADO", "Agendado"),
        ("CONFIRMADO", "Confirmado"),
        ("EM_ANDAMENTO", "Em Andamento"),
        ("CONCLUIDO", "Concluído"),
        ("CANCELADO", "Cancelado"),
        ("NAO_COMPARECEU", "Não Compareceu"),
    ]

    PRIORIDADE_CHOICES = [
        ("BAIXA", "Baixa"),
        ("NORMAL", "Normal"),
        ("ALTA", "Alta"),
        ("URGENTE", "Urgente"),
    ]

    codigo = models.CharField("Código", max_length=20, unique=True)
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.PROTECT, 
        related_name="agendamentos",
        help_text="Cliente que solicitou o agendamento"
    )
    veiculo = models.ForeignKey(
        Veiculo, 
        on_delete=models.PROTECT, 
        related_name="agendamentos",
        null=True, 
        blank=True,
        help_text="Veículo a ser lavado (opcional se apenas placa)"
    )
    base = models.CharField("Base", max_length=100, blank=True)
    local = models.CharField("Local", max_length=100, blank=True)
    tipo_lavagem = models.CharField("Tipo de Lavagem", max_length=50, blank=True)
    transporte_equipamento = models.CharField("Transporte/Equipamento", max_length=50, blank=True)
    lavador = models.ForeignKey(
        Lavador, 
        on_delete=models.PROTECT, 
        related_name="agendamentos",
        null=True, 
        blank=True,
        help_text="Lavador designado (opcional)"
    )
    
    placa_veiculo = models.CharField("Placa do Veículo", max_length=10)
    data_agendamento = models.DateField("Data do Agendamento")
    hora_agendamento = models.TimeField("Hora do Agendamento")
    duracao_estimada = models.PositiveIntegerField(
        "Duração Estimada (minutos)", 
        default=30,
        help_text="Tempo estimado para conclusão da lavagem"
    )
    
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default="AGENDADO")
    prioridade = models.CharField("Prioridade", max_length=10, choices=PRIORIDADE_CHOICES, default="NORMAL")
    
    valor_estimado = models.DecimalField(
        "Valor Estimado", 
        max_digits=10, 
        decimal_places=2,
        help_text="Valor estimado da lavagem",
        null=True, blank=True
    )
    desconto_agendamento = models.DecimalField(
        "Desconto por Agendamento", 
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Desconto especial por agendar"
    )
    
    telefone_contato = models.CharField(
        "Telefone de Contato", 
        max_length=20, 
        blank=True,
        help_text="Telefone para confirmação do agendamento"
    )
    email_contato = models.EmailField(
        "Email de Contato", 
        blank=True,
        help_text="Email para envio de confirmações"
    )
    
    observacoes = models.TextField("Observações", blank=True)
    observacoes_internas = models.TextField(
        "Observações Internas", 
        blank=True,
        help_text="Observações visíveis apenas para funcionários"
    )
    
    confirmado_em = models.DateTimeField("Confirmado em", null=True, blank=True)
    confirmado_por = models.CharField("Confirmado por", max_length=100, blank=True)
    
    cancelado_em = models.DateTimeField("Cancelado em", null=True, blank=True)
    motivo_cancelamento = models.TextField("Motivo do Cancelamento", blank=True)
    
    lavagem = models.OneToOneField(
        "Lavagem", 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="agendamento_origem",
        help_text="Lavagem criada a partir deste agendamento"
    )
    
    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ["data_agendamento", "hora_agendamento"]
        
        unique_together = [
            ["data_agendamento", "hora_agendamento", "local"]
        ]

    def __str__(self):
        return f"{self.codigo} - {self.placa_veiculo} ({self.data_agendamento} {self.hora_agendamento})"

    def save(self, *args, **kwargs):
        if not self.codigo:
            import random
            import string
            self.codigo = "AGD" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Definir valor estimado e duração estimada como valores fixos ou remover a lógica
        if not self.valor_estimado:
            self.valor_estimado = Decimal("25.00") # Valor fixo
        if not self.duracao_estimada:
            self.duracao_estimada = 30 # Duração fixa
        
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        
        if self.data_agendamento and self.data_agendamento < timezone.now().date():
            raise ValidationError("Não é possível agendar para uma data no passado.")
        
        if self.hora_agendamento:
            hora = self.hora_agendamento.hour
            if hora < 6 or hora >= 18:
                raise ValidationError("Agendamentos só podem ser feitos entre 6h e 18h.")

    @property
    def data_hora_agendamento(self):
        if self.data_agendamento and self.hora_agendamento:
            return timezone.datetime.combine(self.data_agendamento, self.hora_agendamento)
        return None

    @property
    def esta_vencido(self):
        if self.data_hora_agendamento:
            return timezone.now() > self.data_hora_agendamento
        return False

    @property
    def pode_ser_cancelado(self):
        return self.status in ["AGENDADO", "CONFIRMADO"]

    @property
    def pode_iniciar_lavagem(self):
        return self.status in ["AGENDADO", "CONFIRMADO"] and not self.esta_vencido

    def confirmar_agendamento(self, confirmado_por=""):
        self.status = "CONFIRMADO"
        self.confirmado_em = timezone.now()
        self.confirmado_por = confirmado_por
        self.save()

    def cancelar_agendamento(self, motivo=""):
        self.status = "CANCELADO"
        self.cancelado_em = timezone.now()
        self.motivo_cancelamento = motivo
        self.save()

    def marcar_nao_compareceu(self):
        self.status = "NAO_COMPARECEU"
        self.save()

    def iniciar_lavagem(self):
        from .models import Lavagem
        
        if not self.pode_iniciar_lavagem:
            raise ValidationError("Este agendamento não pode ser convertido em lavagem.")
        
        lavagem = Lavagem.objects.create(
            cliente=self.cliente,
            veiculo=self.veiculo,
            base=self.base,
            local=self.local,
            tipo_lavagem=self.tipo_lavagem,
            transporte_equipamento=self.transporte_equipamento,
            lavador=self.lavador,
            placa_veiculo=self.placa_veiculo,
            hora_inicio=timezone.now(),
            data_lavagem=timezone.now().date(),
            valor_servico=self.valor_estimado,
            desconto=self.desconto_agendamento,
            observacoes=f"Criada a partir do agendamento {self.codigo}. {self.observacoes}".strip()
        )
        
        self.status = "EM_ANDAMENTO"
        self.lavagem = lavagem
        self.save()
        
        return lavagem

    def get_horario_fim_estimado(self):
        if self.data_hora_agendamento and self.duracao_estimada:
            from datetime import timedelta
            return self.data_hora_agendamento + timedelta(minutes=self.duracao_estimada)
        return None


