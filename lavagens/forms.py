from django import forms
from .models import Agendamento, Base, TipoLavagem, TransporteEquipamento

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


