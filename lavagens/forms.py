from django import forms
from .models import Agendamento, Base, TipoLavagem, TransporteEquipamento,Lavagem



class LavagemForm(forms.ModelForm):
    class Meta:
        model = Lavagem
        fields = '__all__'
        
        # Exclui os campos que serão preenchidos automaticamente
        exclude = [
            'codigo',
            'valor_final',
            'data_lavagem'
        ]

        # Melhora a aparência dos campos no template
        widgets = {
            'hora_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control-custom'}),
            'hora_termino': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control-custom'}),
            'observacoes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control-custom'}),
        }

    def __init__(self, *args, **kwargs):
        """Aplica a classe CSS a todos os campos para o tema escuro."""
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control-custom'

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = '__all__'



# 1. CRIE ESTA CLASSE MIXIN
class FormStyleMixin(forms.Form):
    """
    Um Mixin para aplicar classes CSS do Bootstrap a todos os campos de um formulário.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Adiciona a classe 'form-control' para a maioria dos campos
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                # Checkboxes usam uma classe diferente
                widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(widget, forms.Select):
                # Selects usam 'form-select'
                widget.attrs.update({'class': 'form-select'})
            else:
                # Inputs de texto, número, email, etc.
                widget.attrs.update({'class': 'form-control'})


# 2. FAÇA SEUS FORMULÁRIOS HERDAREM DO MIXIN
class BaseForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Base
        fields = '__all__'

from django.forms import inlineformset_factory
from .models import MaterialLavagem

class TipoLavagemForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = TipoLavagem
        fields = ['nome', 'preco_base']

MaterialLavagemFormSet = inlineformset_factory(TipoLavagem, MaterialLavagem, fields=('nome', 'valor'), extra=1, can_delete=True)


class TransporteEquipamentoForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = TransporteEquipamento
        fields = '__all__'


