# usuarios/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-custom'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-custom'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Senha atual",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-custom', 'autocomplete': 'current-password'}),
    )
    new_password1 = forms.CharField(
        label="Nova senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-custom', 'autocomplete': 'new-password'}),
    )
    new_password2 = forms.CharField(
        label="Confirmação da nova senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-custom', 'autocomplete': 'new-password'}),
    )
