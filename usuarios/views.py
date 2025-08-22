# No arquivo: usuarios/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import UserUpdateForm, CustomPasswordChangeForm

# --- ESTA É A CLASSE QUE ESTÁ FALTANDO ---
class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    # Se o login for bem-sucedido, redireciona para o dashboard principal
    success_url = reverse_lazy('dashboard') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Login'
        return context

# --- ESTA É A VIEW DO PERFIL QUE JÁ CRIAMOS ---
@login_required
def meu_perfil(request):
    if request.method == 'POST':
        # Verifica qual formulário foi enviado
        if 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Mantém o usuário logado
                messages.success(request, 'Sua senha foi alterada com sucesso!')
                return redirect('meu_perfil')
            else:
                user_form = UserUpdateForm(instance=request.user)
        else:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Seu perfil foi atualizado com sucesso!')
                return redirect('meu_perfil')
            else:
                password_form = CustomPasswordChangeForm(request.user)
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(request.user)

    context = {
        'user_form': user_form,
        'password_form': password_form
    }
    return render(request, 'usuarios/meu_perfil.html', context)
