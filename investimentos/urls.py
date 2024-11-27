# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_usuario, name='login'),
    path('logout/', views.logout_view, name='logout'),  # Usa a função personalizada
]
