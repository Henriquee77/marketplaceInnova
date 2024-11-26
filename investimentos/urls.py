from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('', views.login_usuario, name='login'),
    path('home/', views.home_view, name='home'),
]
