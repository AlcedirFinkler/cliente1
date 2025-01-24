# models.py from app CadEquip

from django.db import models

class Setor(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class Equipamento(models.Model):
    CLASSIFICACAO = [
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
    ]
    nome = models.CharField(max_length=200)
    tag = models.CharField(max_length=200, unique=True)
    patrimonio = models.CharField(
        max_length=200, 
        unique=True, 
        blank=True,  # Allow blank values
        null=True   # Allow null values
    )
    modelo = models.CharField(max_length=200)
    fabricante = models.CharField(max_length=200)
    numero_serie = models.CharField(max_length=200, unique=False, blank=True, null=True)
    ano_fabricacao = models.CharField(max_length=200, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    setor = models.ForeignKey('gestaoOS.Setor', on_delete=models.CASCADE, related_name='equipamentos')
    local = models.CharField(max_length=150, blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_equipamentos/%Y/%m/%d/', null=True, blank=True)
    fornecedor = models.ForeignKey(
        'CadFornecedor.Fornecedor',  # Relaciona ao modelo Fornecedor do app CadFornecedor
        on_delete=models.SET_NULL,
        related_name='equipamentos',
        null=True,
        blank=True
    )
    manual_operacao = models.FileField(upload_to='manuais/', null=True, blank=True)
    garantia_termino = models.DateField(null=True, blank=True)
    classe = models.CharField(max_length=1, blank=True, null=True)
    ssma = models.CharField(
        max_length=1,
        choices=CLASSIFICACAO,
        default='c',
    )
    qualidade = models.CharField(
        max_length=1,
        choices=CLASSIFICACAO,
        default='c',
    )
    operacao = models.CharField(
        max_length=1,
        choices=CLASSIFICACAO,
        default='c',
    )
    entrega = models.CharField(
        max_length=1,
        choices=CLASSIFICACAO,
        default='c',
    )
    mtbf = models.CharField(
        max_length=1,
        choices=CLASSIFICACAO,
        default='c',
    )
    mttr = models.CharField(
        max_length=1,
        choices=CLASSIFICACAO,
        default='c',
    )

    def __str__(self):
        return f"{self.nome} ({self.tag}) - {self.setor.nome} - {self.fornecedor.fornecedor if self.fornecedor else 'Sem fornecedor'}"

    class Meta:
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'
