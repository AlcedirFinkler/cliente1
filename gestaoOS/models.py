# models.py from app gestaoOS

from django.db import models
from django.contrib.auth.models import User
from CadEquip.models import Equipamento

class Setor(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

class Chamado(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('finalizado', 'finalizado'),
        ('concluido', 'Concluído'),
    ]

    TIPO_MANUTENCAO_CHOICES = [
        ('corretiva', 'Corretiva'),
        ('preventiva', 'Preventiva'),
        ('melhoria', 'Melhoria'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chamados')  
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pendente')
    setor = models.ForeignKey(Setor, on_delete=models.CASCADE, related_name='setor')
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='chamados_equipamento', null=True,blank=True) 
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    tempo_parada = models.FloatField(null=True, help_text="Tempo de parada em horas")
    custo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    diagnostico = models.TextField(null=True, blank=True)
    solucao = models.TextField(null=True, blank=True)
    causa_raiz = models.TextField(null=True, blank=True)
    data_inicio_atendimento = models.DateTimeField(null=True)
    data_fim_atendimento = models.DateTimeField(null=True)
    tipo_manutencao = models.CharField(
        max_length=20,
        choices=TIPO_MANUTENCAO_CHOICES,
        default='corretiva',
    )
    tecnico = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tecnico_chamados',
        limit_choices_to={'groups__name': 'Técnico'},  # Filtra apenas usuários no grupo "Técnico"
    )
    local = models.CharField(max_length=150, blank=True)
    foto = models.ImageField(upload_to='fotos_chamados/', null=True, blank=True)

    def __str__(self):
        return self.titulo
    
class AcaoPeca(models.Model):
    acao = models.ForeignKey('Acao', on_delete=models.CASCADE, related_name='acoes_pecas')
    peca = models.ForeignKey('cadEstoque.Pecas', on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.peca.descricao} - Qtd: {self.quantidade}"

class AcaoColaborador(models.Model):
    acao = models.ForeignKey('Acao', on_delete=models.CASCADE, related_name='acoes_colaboradores')
    colaborador = models.ForeignKey(User, on_delete=models.CASCADE)
    horas_trabalhadas = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Horas Trabalhadas')
    descricao_atividade = models.TextField(verbose_name='Descrição da Atividade')
    
    def __str__(self):
        return f"{self.colaborador.username} - {self.horas_trabalhadas}h - {self.acao}"

    class Meta:
        verbose_name = 'Colaborador da Ação'
        verbose_name_plural = 'Colaboradores da Ação'

class Acao(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name='acoes')
    descricao = models.TextField(max_length=500, verbose_name='Descrição')
    duracao = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Duração (em horas)')
    data_criacao = models.DateTimeField(auto_now_add=True)
    arquivos = models.FileField(upload_to='acoes_pdfs/', blank=True, null=True)
    pecas_utilizadas = models.ManyToManyField('cadEstoque.Pecas', 
        through='AcaoPeca',
        through_fields=('acao', 'peca'),
        related_name='AcoesPecas', 
        blank=True)
       
    def __str__(self):
        return f"Ação para {self.chamado.titulo} - {self.descricao[:50]}"