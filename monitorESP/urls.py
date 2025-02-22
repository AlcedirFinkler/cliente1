from django.urls import path
from . import views
from .views import toggle_auto_update

urlpatterns = [
    path('device_list', views.device_list, name='device_list'),
    path('delete/<int:device_id>/', views.delete_device, name='delete_device'),
    path('atualiza_horimetro/', views.atualiza_horimetro, name='atualiza_horimetro'),
    path('update-offset/<int:device_id>/', views.update_offset, name='update_offset'),
    path('toggle-auto-update/<int:device_id>/', toggle_auto_update, name='toggle_auto_update'),
    path('update-horimetro-atual/<int:device_id>/', views.update_horimetro_atual, name='update_horimetro_atual'),
]