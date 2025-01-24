from django.contrib import admin
from .models import Chamado, Setor

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)



admin.site.register(Chamado)
