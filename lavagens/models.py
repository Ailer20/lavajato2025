from django.db import models
from django.utils import timezone
from clientes.models import Cliente, Veiculo, Lavador


class Lavagem(models.Model):
    """
    Modelo principal para representar uma lavagem
    """
    STATUS_CHOICES = [
        ("EM_ANDAMENTO", "Lavagem em Andamento"),
        ("CONCLUIDA", "Lavagem Concluída"),
        ("CANCELADA", "Cancelada"),
    ]

    codigo = models.CharField("Código", max_length=20, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="lavagens", null=True, blank=True)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.PROTECT, related_name="lavagens", null=True, blank=True)

    base = models.ForeignKey('Base', on_delete=models.PROTECT, related_name='lavagens_base', null=True, blank=True)
    local = models.CharField('Local', max_length=100, blank=True, null=True)
    tipo_lavagem = models.ForeignKey('TipoLavagem', on_delete=models.PROTECT, related_name='lavagens_tipo', null=True, blank=True)
    transporte_equipamento = models.ForeignKey('TransporteEquipamento', on_delete=models.PROTECT, related_name='lavagens_transporte', null=True, blank=True)
    lavador = models.ForeignKey(Lavador, on_delete=models.PROTECT, related_name="lavagens", null=True, blank=True)
    placa_veiculo = models.CharField("Placa do Veículo", max_length=10)
    hora_inicio = models.DateTimeField("Hora de Início")
    hora_termino = models.DateTimeField("Hora de Término", null=True, blank=True)
    data_lavagem = models.DateField("Data da Lavagem")
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default="EM_ANDAMENTO")
    valor_servico = models.DecimalField("Valor do Serviço", max_digits=10, decimal_places=2, null=True, blank=True)
    desconto = models.DecimalField("Desconto", max_digits=10, decimal_places=2, default=0)
    valor_final = models.DecimalField("Valor Final", max_digits=10, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField("Observações", blank=True)
    recebimento = models.CharField("Recebimento", max_length=200, blank=True)
    contrato = models.CharField("Contrato", max_length=100, blank=True, help_text="Número ou código do contrato")

    class Meta:
        verbose_name = "Lavagem"
        verbose_name_plural = "Lavagens"
        ordering = ["-data_lavagem", "-hora_inicio"]

    def __str__(self):
        return f"{self.codigo} - {self.placa_veiculo} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.codigo:
            import random
            import string
            self.codigo = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        #if self.hora_inicio and not self.data_lavagem:
        #    self.data_lavagem = self.hora_inicio.date()
        
        if self.valor_servico is not None:
            self.valor_final = self.valor_servico - (self.desconto or 0)
        
        super().save(*args, **kwargs)

    @property
    def duracao_lavagem(self):
        if self.hora_inicio and self.hora_termino:
            delta = self.hora_termino - self.hora_inicio
            return int(delta.total_seconds() / 60)
        return None

    @property
    def esta_em_andamento(self):
        return self.status == "EM_ANDAMENTO"

    @property
    def esta_concluida(self):
        return self.status == "CONCLUIDA"

    def concluir_lavagem(self):
        self.status = "CONCLUIDA"
        if not self.hora_termino:
            self.hora_termino = timezone.now()
        self.save()

    def cancelar_lavagem(self, motivo=""):
        self.status = "CANCELADA"
        if motivo:
            self.observacoes = f"{self.observacoes}\nCancelada: {motivo}".strip()
        self.save()


from .agendamento_models import Agendamento





class TipoLavagem(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    preco_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Tipo de Lavagem"
        verbose_name_plural = "Tipos de Lavagem"

    def __str__(self):
        return self.nome

class Base(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Base"
        verbose_name_plural = "Bases"

    def __str__(self):
        return self.nome

class TransporteEquipamento(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    multiplicador_preco = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)

    class Meta:
        verbose_name = "Transporte/Equipamento"
        verbose_name_plural = "Transportes/Equipamentos"

    def __str__(self):
        return self.nome


