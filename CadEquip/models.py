# models.py from app CadEquip

from django.db import models
from django.utils import timezone
from datetime import datetime



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
    horimetro_atual = models.FloatField(default=0, help_text="Horas totais de operação do equipamento")
    ultima_atualizacao = models.DateTimeField(null=True, blank=True)

    def atualizar_horimetro(self, novas_horas):
        """
        Atualiza o horímetro do equipamento e mantém o histórico mensal de horas trabalhadas.
        """
        agora = timezone.now()
        ano_atual = agora.year
        mes_atual = agora.month

        if self.ultima_atualizacao:
            ultima_data = self.ultima_atualizacao
            ultimo_mes = ultima_data.month
            ultimo_ano = ultima_data.year

            # Caso tenha mudado o mês, calcula o total de horas do mês anterior
            if ultimo_ano != ano_atual or ultimo_mes != mes_atual:
                horas_mes_anterior = novas_horas - self.horimetro_atual
                HistoricoHorasMensais.objects.create(
                    equipamento=self,
                    ano=ultimo_ano,
                    mes=ultimo_mes,
                    horas_trabalhadas=horas_mes_anterior
                )

        # Atualiza os dados do horímetro
        self.horimetro_atual = novas_horas
        self.ultima_atualizacao = agora
        self.save()

    def __str__(self):
        return f"{self.nome} ({self.tag}) - {self.setor.nome} - {self.fornecedor.fornecedor if self.fornecedor else 'Sem fornecedor'}"

    class Meta:
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'

class HistoricoHorasMensais(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='historico_horas_mensais')
    ano = models.IntegerField(help_text="Ano do registro")
    mes = models.IntegerField(help_text="Mês do registro (1 a 12)")
    horas_trabalhadas = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['equipamento', 'ano', 'mes']
        ordering = ['-ano', '-mes']

    def __str__(self):
        return f"{self.equipamento.tag} - {self.mes}/{self.ano} - Horas: {self.horas_trabalhadas}"

