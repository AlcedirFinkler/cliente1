from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('modulos/', views.modulos, name='modulos'),
    path('api/modules/', views.get_modules_json, name='api_modules'),
    path('selecao_modulos/', views.selecao_modulos, name='selecao_modulos'),
]