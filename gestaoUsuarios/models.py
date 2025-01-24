# models.py from app gestaoUsuarios

from django.db import models
from django.contrib.auth.models import User, Group

class CadastroPendente(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)
    grupo = models.CharField(max_length=50, choices=[("Solicitante", "Solicitante"), ("Técnico", "Técnico"), ("Estoquista", "Estoquista"), ("Gestor", "Gestor")], default='Solicitante')
    data_cadastro = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)  # Novo campo

    def __str__(self):
        return f"{self.username} ({self.grupo})"
