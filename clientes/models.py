from django.db import models
from django.contrib.auth.models import User  # <--- IMPORTANTE: Esta importação é necessária

class Cliente(models.Model):
    nome = models.CharField('Nome', max_length=200)
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Veiculo(models.Model):
    TIPOS_VEICULO = [
        ('CARRO', 'Carro'),
        ('MOTO', 'Moto'),
        ('CAMINHAO', 'Caminhão'),
        ('ONIBUS', 'Ônibus'),
        ('VAN', 'Van'),
        ('PICKUP', 'Pick-up'),
        ('OUTROS', 'Outros'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='veiculos')
    placa = models.CharField('Placa', max_length=10, unique=True)
    modelo = models.CharField('Modelo', max_length=100)
    marca = models.CharField('Marca', max_length=50)
    ano = models.PositiveIntegerField('Ano', null=True, blank=True)
    cor = models.CharField('Cor', max_length=30, blank=True)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPOS_VEICULO, default='CARRO')
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        ordering = ['placa']

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"

class Lavador(models.Model):
    nome = models.CharField('Nome Completo', max_length=200)
    
    # --- CAMPO NOVO ---
    usuario = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='lavador_perfil', 
        verbose_name="Usuário do Sistema"
    )
    # ------------------

    cpf = models.CharField('CPF', max_length=14, unique=True)
    
    # Campos novos do RH
    matricula = models.CharField('Matrícula', max_length=20, unique=True, blank=True, null=True)
    jornada_trabalho = models.CharField('Jornada de Trabalho', max_length=100, blank=True)
    escala_trabalho = models.CharField('Escala', max_length=50, blank=True)
    
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    data_admissao = models.DateField('Data de Admissão')
    salario = models.DecimalField('Salário', max_digits=10, decimal_places=2, null=True, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores (RH)'
        ordering = ['nome']

    def __str__(self):
        return self.nome