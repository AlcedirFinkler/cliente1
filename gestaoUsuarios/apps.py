from django.apps import AppConfig
from django.db.models.signals import post_migrate

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestaoUsuarios'

    def ready(self):
        # Conecta o sinal ao método que cria os grupos
        post_migrate.connect(criar_grupos, sender=self)

def criar_grupos(sender, **kwargs):
    """
    Função para criar os grupos 'Solicitante', 'Técnico' e 'Gestor' automaticamente.
    """
    from django.contrib.auth.models import Group
    grupos = ["Solicitante", "Técnico", "Gestor"]
    for nome in grupos:
        Group.objects.get_or_create(name=nome)