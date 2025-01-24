from django.urls import path
from CadEquip.views import (
    listar_equipamentos,
    cria_equipamento,
    editar_equipamento,
    excluir_equipamento,
    busca_fornecedores
)

urlpatterns = [
    path('CadEquip/', listar_equipamentos, name='CadEquip'),
    path('CadEquip/cria_equipamento/', cria_equipamento, name='cria_equipamento'),
    path('equipamento/<int:id>/editar/', editar_equipamento, name='editar_equipamento'),
    path('equipamento/<int:id>/excluir/', excluir_equipamento, name='excluir_equipamento'),
    path('busca-fornecedores/', busca_fornecedores, name='busca_fornecedores'),
]

