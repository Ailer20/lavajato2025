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

class BaseForm(forms.ModelForm):
    class Meta:
        model = Base
        fields = '__all__'

class TipoLavagemForm(forms.ModelForm):
    class Meta:
        model = TipoLavagem
        fields = '__all__'

class TransporteEquipamentoForm(forms.ModelForm):
    class Meta:
        model = TransporteEquipamento
        fields = '__all__'


