# models.py from app cadFornecedor

from django.db import models

class Fornecedor(models.Model):
    fornecedor = models.CharField(max_length=200)
    fornecedor_fone = models.CharField(max_length=200)
    fornecedor_site = models.CharField(max_length=200, null=True, blank=True)
    fornecedor_email = models.CharField(max_length=200, null=True, blank=True)
    rua = models.CharField(max_length=200, null=True, blank=True)
    numero = models.CharField(max_length=20, null=True, blank=True)
    bairro = models.CharField(max_length=20, null=True, blank=True)
    cidade = models.CharField(max_length=200, null=True, blank=True)
    cep = models.CharField(max_length=200, null=True, blank=True)
    estado = models.CharField(max_length=200, null=True, blank=True)
    contato = models.CharField(max_length=200, null=True, blank=True)
    cnpj = models.CharField(max_length=200, null=True, blank=True)
    inscricao_estadual = models.CharField(max_length=50, null=True, blank=True)
    prazo_entrega_medio = models.IntegerField(null=True, help_text="Prazo médio em dias")
    observacoes = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.fornecedor  