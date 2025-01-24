from django.contrib import admin
from .models import Equipamento

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'modelo', 'fabricante', 'setor', 'patrimonio', 'ano_fabricacao')
    search_fields = ('nome', 'fabricante', 'setor__nome')  # Pesquisar também pelo nome do setor
    list_filter = ('setor', 'ano_fabricacao')  # Filtros laterais