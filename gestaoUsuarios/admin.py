# admin.py from app gestaoUsuarios
from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import CadastroPendente

@admin.register(CadastroPendente)
class CadastroPendenteAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'grupo', 'is_approved')  # Exibe os campos
    list_filter = ('is_approved', 'grupo')  # Filtro por aprovação e grupo
    actions = ['aprovar_usuario']  # Adiciona ação no admin

    # Método para ações customizadas no admin
    @admin.action(description="Aprovar usuários selecionados")
    def aprovar_usuario(self, request, queryset):
        for cadastro in queryset:
            if not cadastro.is_approved:  # Apenas aprova se ainda não aprovado
                self._aprovar_usuario(cadastro)
                self.message_user(request, f"Usuário {cadastro.username} aprovado com sucesso.")

    # Sobrescrevendo o método de salvar
    def save_model(self, request, obj, form, change):
        if obj.is_approved and not User.objects.filter(username=obj.username).exists():
            self._aprovar_usuario(obj)
        super().save_model(request, obj, form, change)

    # Lógica compartilhada para aprovar usuário
    def _aprovar_usuario(self, cadastro):
        try:
            # Criação do usuário no sistema com senha criptografada
            user = User.objects.create_user(
                username=cadastro.username,
                email=cadastro.email,
                password=cadastro.senha  # Certifique-se de que "senha" é o campo correto
            )
            # Atribuição ao grupo correto
            group = Group.objects.get(name=cadastro.grupo)
            user.groups.add(group)
            user.save()
            print(f"Usuário {cadastro.username} criado e salvo com sucesso!")
        except Exception as e:
            print(f"Erro ao criar usuário {cadastro.username}: {e}")
