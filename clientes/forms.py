from django import forms
from .models import Cliente, Veiculo, Lavador

class FormStyleMixin:
    """
    Um Mixin reutilizável para aplicar classes CSS do Bootstrap a todos os 
    campos de um formulário, garantindo um visual consistente.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            
            # Define a classe padrão com base no tipo de widget
            if isinstance(widget, forms.CheckboxInput):
                # Checkboxes usam 'form-check-input'
                css_class = 'form-check-input'
            elif isinstance(widget, forms.Select):
                # Selects (menus suspensos) usam 'form-select'
                css_class = 'form-select'
            else:
                # Todos os outros campos (texto, número, data, etc.) usam 'form-control'
                css_class = 'form-control'
            
            # Aplica a classe ao widget do campo
            widget.attrs.update({'class': css_class})



class ClienteForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

class VeiculoForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = '__all__'

class LavadorForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Lavador
        fields = '__all__'

