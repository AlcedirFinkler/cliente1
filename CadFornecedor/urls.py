from . import views
from CadFornecedor.views import CadFornecedor, cria_fornecedor



from django.urls import path

urlpatterns = [
    path('CadFornecedor/', CadFornecedor, name='CadFornecedor'),  
    path('CriaFornecedor/', cria_fornecedor, name='CriaFornecedor'), 
    path('editar/<int:id>/', views.editar_fornecedor, name='editar_fornecedor'),
    path('excluir/<int:id>/', views.excluir_fornecedor, name='excluir_fornecedor'),
]