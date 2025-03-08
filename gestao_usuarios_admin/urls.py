from django.urls import path
from . import views

urlpatterns = [
    path('listar-pendentes/', views.listar_usuarios_pendentes, name='listar_usuarios_pendentes'),
    path('editar-pendente/<int:pk>/', views.editar_usuario_pendente, name='editar_usuario_pendente'),
    path('criar-usuario/', views.criar_usuario, name='criar_usuario'),
    path('configuracoes/criar_setor/', views.criar_setor, name='criar_setor')
]