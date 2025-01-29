from django.urls import path
from .views import (
    relatorios_index, 
    gerar_relatorio_chamados, 
    gerar_relatorio_pecas, 
    gerar_relatorio_tecnicos,
    gerar_relatorio_indicadores
)

urlpatterns = [
    path('relatorios_index', relatorios_index, name='relatorios_index'),
    path('chamados/', gerar_relatorio_chamados, name='relatorio_chamados'),
    path('pecas/', gerar_relatorio_pecas, name='relatorio_pecas'),
    path('tecnicos/', gerar_relatorio_tecnicos, name='relatorio_tecnicos'),
    path('indicadores/', gerar_relatorio_indicadores, name='relatorio_indicadores'),
    # Adicione mais paths conforme necessário para outras views...
]