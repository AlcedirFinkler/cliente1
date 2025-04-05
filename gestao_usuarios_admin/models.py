# models.py from gestao_usuarios_admin 
from django.db import models
from django.contrib.auth.models import User, Group

# Este modelo não é necessário, pois usaremos o CadastroPendente existente
# Mantido para referência futura, se necessário
class UsuarioGestao(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.user.username