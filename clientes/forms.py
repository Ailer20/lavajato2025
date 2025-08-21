from django import forms
from .models import Cliente, Veiculo, Lavador


class ClienteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplica a classe 'form-control' a todos os campos
        for field_name, field in self.fields.items():
            # Para checkboxes, o estilo é diferente
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'
    
    class Meta:
        model = Cliente
        fields = '__all__'

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = '__all__'

class LavadorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Este loop aplica as classes CSS a todos os campos do formulário
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input form-control-custom'
            else:
                field.widget.attrs['class'] = 'form-control-custom'

    class Meta:
        model = Lavador
        fields = '__all__'

