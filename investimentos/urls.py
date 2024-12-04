from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('comprar/', views.pagina_comprar, name='pagina_comprar'),
    path('vender/', views.pagina_vender, name='pagina_vender'),
    path('comprar/<int:ativo_id>/', views.comprar_ativo, name='comprar_ativo'),
    path('vender/<int:ativo_id>/', views.vender_ativo, name='vender_ativo'),
    path('historico/', views.historico_view, name='historico'),
    path('relatorios/', views.relatorios_view, name='relatorios'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('', views.login_usuario, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('atualizar_simulacao/', views.atualizar_simulacao, name='atualizar_simulacao'),  # N
]
