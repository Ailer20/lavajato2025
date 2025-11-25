from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from clientes.models import Lavador
from django.contrib.auth.models import User


class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nome
    class Meta: verbose_name_plural = "Categorias"

class LocalArmazenamento(models.Model):
    """Onde o item está guardado fisicamente"""
    nome = models.CharField('Nome/Identificação', max_length=50, help_text="Ex: Prateleira A1, Armário 2")
    descricao = models.CharField('Descrição', max_length=100, blank=True)
    
    def __str__(self):
        return self.nome
    class Meta: verbose_name = "Local de Armazenamento"

class Produto(models.Model):
    TIPO_CHOICES = [
        ('CONSUMIVEL', 'Consumível (Sabão, Cera, etc.)'),
        ('DURAVEL', 'Durável/Ferramenta (Politriz, etc.)'),
    ]
    
    nome = models.CharField('Produto', max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='CONSUMIVEL')
    unidade_medida = models.CharField('Unidade', max_length=20, default='UN')
    localizacao = models.ForeignKey(LocalArmazenamento, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Localização Física")
    
    estoque_minimo = models.PositiveIntegerField('Estoque Mínimo', default=5)
    quantidade_atual = models.PositiveIntegerField('Quantidade em Estoque', default=0)
    custo_medio = models.DecimalField('Custo Médio', max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.nome} ({self.quantidade_atual} {self.unidade_medida})"

    class Meta:
        verbose_name = 'Produto do Estoque'
        verbose_name_plural = 'Catálogo de Produtos'

class MovimentacaoEstoque(models.Model):
    """LOG AUDITÁVEL DE TODAS AS AÇÕES NO ESTOQUE"""
    TIPO_MOVIMENTO = [
        ('ENTRADA', 'Entrada (Compra/NF)'),
        ('SAIDA', 'Saída (Uso/Retirada)'),
        ('DEVOLUCAO', 'Devolução ao Estoque'),
        ('AJUSTE', 'Ajuste de Inventário/Perda'),
    ]
    
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMENTO)
    quantidade = models.PositiveIntegerField()
    
    # Rastreabilidade
    saldo_anterior = models.IntegerField(editable=False)
    saldo_atual = models.IntegerField(editable=False)
    
    # Quem e Quando
    data_movimento = models.DateTimeField(auto_now_add=True)
    usuario_sistema = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, help_text="Usuário que registrou no sistema")
    
    # Para saídas/devoluções
    responsavel = models.ForeignKey(Lavador, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Colaborador Responsável")
    
    observacao = models.CharField('Observação/Motivo', max_length=255, blank=True)
    
    # Vínculos
    nota_fiscal = models.ForeignKey('NotaFiscalEntrada', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # 1. Captura saldo anterior
        self.saldo_anterior = self.produto.quantidade_atual
        
        # 2. Calcula novo saldo
        if self.tipo in ['ENTRADA', 'DEVOLUCAO']:
            self.saldo_atual = self.saldo_anterior + self.quantidade
        elif self.tipo in ['SAIDA', 'AJUSTE']:
            if self.quantidade > self.saldo_anterior:
                raise ValidationError(f"Estoque insuficiente para o produto {self.produto.nome}.")
            self.saldo_atual = self.saldo_anterior - self.quantidade
            
        # 3. Atualiza o Produto
        self.produto.quantidade_atual = self.saldo_atual
        self.produto.save()
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Log de Movimentação'
        verbose_name_plural = 'Histórico de Movimentações'
        ordering = ['-data_movimento']

# --- MANTENDO A NOTA FISCAL (Com atualização para usar Movimentacao) ---
class NotaFiscalEntrada(models.Model):
    numero_nota = models.CharField('Número da Nota', max_length=50)
    cnpj_fornecedor = models.CharField('CNPJ Fornecedor', max_length=18)
    razao_social = models.CharField('Razão Social', max_length=200, blank=True)
    data_emissao = models.DateField('Data de Emissão')
    data_vencimento = models.DateField('Data de Vencimento')
    valor_total_nota = models.DecimalField('Valor Total da Nota', max_digits=10, decimal_places=2)
    arquivo_pdf = models.FileField(upload_to='notas_fiscais/', blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"NF {self.numero_nota}"

class ItemNotaFiscal(models.Model):
    nota_fiscal = models.ForeignKey(NotaFiscalEntrada, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Gera o Log de Entrada automaticamente
        MovimentacaoEstoque.objects.create(
            produto=self.produto,
            tipo='ENTRADA',
            quantidade=self.quantidade,
            nota_fiscal=self.nota_fiscal,
            observacao=f"Entrada via NF {self.nota_fiscal.numero_nota}"
        )