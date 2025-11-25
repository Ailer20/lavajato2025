from django import forms
from .models import Produto, MovimentacaoEstoque, NotaFiscalEntrada, Categoria, LocalArmazenamento


class FormStyleMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

class CategoriaForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']

class LocalArmazenamentoForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = LocalArmazenamento
        fields = ['nome', 'descricao']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }


class ProdutoForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'categoria', 'tipo', 'unidade_medida', 'localizacao', 'estoque_minimo', 'custo_medio', 'quantidade_atual']

class NotaFiscalForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = NotaFiscalEntrada
        fields = '__all__'
        widgets = {
            'data_emissao': forms.DateInput(attrs={'type': 'date'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
        }

class SaidaUnificadaForm(FormStyleMixin, forms.ModelForm):
    """
    Formulário ÚNICO para qualquer tipo de saída (Consumo ou Atribuição).
    """
    class Meta:
        model = MovimentacaoEstoque
        fields = ['produto', 'quantidade', 'responsavel', 'observacao']
        widgets = {
            'observacao': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Motivo da baixa ou observações sobre a entrega...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Rótulos mais claros
        self.fields['produto'].label = "Produto / Material"
        self.fields['responsavel'].label = "Responsável (Opcional)"
        self.fields['responsavel'].help_text = "Selecione o colaborador se for um empréstimo/entrega de ferramenta. Deixe em branco para consumo interno."
        
        # Filtrar apenas produtos que têm saldo positivo (> 0)
        self.fields['produto'].queryset = Produto.objects.filter(quantidade_atual__gt=0)
        
        # Mostrar o saldo atual no nome do produto para facilitar
        self.fields['produto'].label_from_instance = lambda obj: f"{obj.nome} (Em estoque: {obj.quantidade_atual} {obj.unidade_medida})"

class DevolverMaterialForm(FormStyleMixin, forms.ModelForm):
    """Formulário para o Colaborador devolver material"""
    class Meta:
        model = MovimentacaoEstoque
        fields = ['produto', 'quantidade', 'observacao']

    def __init__(self, user_lavador, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_lavador = user_lavador
        self.fields['produto'].label = "Material para devolver"
        self.fields['observacao'].label = "Motivo / Estado do material"