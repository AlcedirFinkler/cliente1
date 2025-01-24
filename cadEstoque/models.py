# models.py from app cadEstoque

from django.db import models
from CadFornecedor.models import Fornecedor

class Fornecedor(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class Pecas(models.Model):
    descricao = models.CharField(max_length=255)
    codigo = models.CharField(max_length=100)
    estoque_minimo = models.IntegerField(default=0)
    estoque_atual = models.IntegerField(default=0) 
    preco =  models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidade_medida = models.CharField(max_length=20)  # kg, unidade, metro, etc
    localizacao = models.CharField(max_length=100, help_text="Localização física no estoque")
    data_ultima_compra = models.DateField(null=True)
    vida_util = models.IntegerField(null=True, help_text="Vida útil em dias")
    fornecedor = models.ForeignKey(
        'CadFornecedor.Fornecedor',  # Relaciona ao modelo Fornecedor do app CadFornecedor
        on_delete=models.SET_NULL,
        related_name='pecas',
        null=True,
        blank=True
    )
    orcamentos = models.FileField(upload_to='orcamentos/', blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_pecas/', null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.descricao}- {self.fornecedor.fornecedor if self.fornecedor else 'Sem fornecedor'}"

