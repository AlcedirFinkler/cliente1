from gestaoOS import views
from .views import tela_inicial, criar_chamado, gerenciar_acoes, finalizar_chamado, historico_equipamento


from django.urls import path

urlpatterns = [
    path('tela_inicial/', tela_inicial, name='tela_inicial'),
    path('chamado/criar/', criar_chamado, name='criar_chamado'),
    path('excluir_chamado/<int:id>/', views.excluir_chamado, name='excluir_chamado'),
    path('chamados/<int:chamado_id>/acoes/', views.gerenciar_acoes, name='gerenciar_acoes'),
    path('chamados/<int:chamado_id>/finalizar/', views.finalizar_chamado, name='finalizar_chamado'),
    path('equipamento/<int:equipamento_id>/historico/', views.historico_equipamento, name='historico_equipamento'),
]
