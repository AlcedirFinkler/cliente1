from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('modulos/', views.modulos, name='modulos'),
    #path('solicitantes/', views.solicitantes_home, name='solicitantes_home'),
    #path('tecnicos/', views.tecnicos_home, name='tecnicos_home'),
    #path('gestores/', views.gestores_home, name='gestores_home'),
]