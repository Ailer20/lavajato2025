from django.contrib import admin
from .models import Produto, MovimentacaoEstoque, NotaFiscalEntrada, ItemNotaFiscal, Categoria, LocalArmazenamento
# --- ADICIONE ESTAS DUAS CLASSES ---
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(LocalArmazenamento)
class LocalArmazenamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)
# -----------------------------------

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'unidade_medida', 'quantidade_atual', 'estoque_minimo', 'custo_medio')
    search_fields = ('nome',)
    list_filter = ('unidade_medida',)


# Registre também as notas fiscais se desejar visualizá-las aqui
class ItemNotaFiscalInline(admin.TabularInline):
    model = ItemNotaFiscal
    extra = 1

@admin.register(NotaFiscalEntrada)
class NotaFiscalEntradaAdmin(admin.ModelAdmin):
    list_display = ('numero_nota', 'razao_social', 'data_emissao', 'valor_total_nota')
    inlines = [ItemNotaFiscalInline]


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('data_movimento', 'tipo', 'produto', 'quantidade', 'responsavel', 'usuario_sistema')
    list_filter = ('tipo', 'data_movimento', 'responsavel')
    search_fields = ('produto__nome', 'responsavel__nome', 'observacao')
    readonly_fields = ('saldo_anterior', 'saldo_atual', 'data_movimento', 'usuario_sistema')

    def has_delete_permission(self, request, obj=None):
        # Para ser robusto, não permitimos apagar logs de estoque pelo admin
        return False