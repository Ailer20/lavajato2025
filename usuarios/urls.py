# usuarios/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views # Importe as views de autenticação do Django
from .views import CustomLoginView, meu_perfil

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('perfil/', meu_perfil, name='meu_perfil'),

    # --- URLs PARA RESET DE SENHA ---
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='usuarios/password_reset.html'), 
         name='password_reset'),
         
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='usuarios/password_reset_done.html'), 
         name='password_reset_done'),
         
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='usuarios/password_reset_confirm.html'), 
         name='password_reset_confirm'),
         
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='usuarios/password_reset_complete.html'), 
         name='password_reset_complete'),
]
