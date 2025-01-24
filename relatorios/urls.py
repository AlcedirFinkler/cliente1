# reports/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # path('', views.relatorios_view, name='relatorios'),
    path('equipamentos/', views.gerar_relatorio_equipamentos, name='relatorio_equipamentos'),
    #path('pecas/', views.gerar_relatorio_pecas, name='relatorio_pecas'),
    #path('chamados/status/', views.gerar_relatorio_chamados_status, name='relatorio_chamados_status'),
    #path('chamados/tecnico/', views.gerar_relatorio_chamados_tecnico, name='relatorio_chamados_tecnico'),
    #path('chamados/equipamento/', views.gerar_relatorio_chamados_equipamento, name='relatorio_chamados_equipamento'),
    #path('manutencoes/proximas/', views.gerar_relatorio_manutencoes_preventivas_proximidade, name='relatorio_manutencoes_proximas'),
    #path('manutencoes/pecas/', views.gerar_relatorio_pecas_manutencoes_proximas, name='relatorio_pecas_manutencoes'),
]