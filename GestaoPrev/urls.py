# urls.py from app GestaoPrev
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('manutencoes/', views.listar_manutencoes, name='listar_manutencoes'),
    path('excluir_manutencao/<int:id>/', views.excluir_manutencao, name='excluir_manutencao'),
    path('editar_manutencao/<int:id>/', views.editar_manutencao, name='editar_manutencao'),
    # path('gerar_os_preventiva/<int:manutencao_id>/', views.gerar_os_preventiva, name='gerar_os_preventiva'),
    path('manutencao/<int:manutencao_id>/gerar-os/', views.gerar_os_preventiva, name='gerar_os_preventiva'),
    path('manutencoes/criar/', views.criar_manutencao, name='criar_manutencao'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)