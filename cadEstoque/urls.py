from cadEstoque import views
from . import views
from cadEstoque.views import teste



from django.urls import path

urlpatterns = [
    path('cadEstoque/', teste, name='cadEstoque'),  
    path('pecas/criar/', views.cria_peca, name='cria_peca'),
    path('pecas/editar/<int:id>/', views.editar_peca, name='editar_peca'),
    path('pecas/excluir/<int:id>/', views.excluir_peca, name='excluir_peca'),
    path('busca-fornecedores/', views.busca_fornecedores, name='busca_fornecedores'),
]