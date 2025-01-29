# models.py from app GestaoPrev

from django.db import models
from django.urls import reverse
from datetime import datetime, timedelta, date
from calendar import monthrange

class ManutencaoPreventiva(models.Model):
    equipamento = models.ForeignKey(
        'CadEquip.Equipamento', on_delete=models.CASCADE, related_name='manutencoes'
    ) 
    pecas = models.ManyToManyField(
    'cadEstoque.Pecas', 
    related_name='manutencoes', 
    blank=True
    )
    tipo_calculo = models.CharField(max_length=100, choices=[('horas', 'Horas'), ('meses', 'Meses'), ('ambos', 'Ambos')])
    requer_parada = models.BooleanField(default=False)
    descricao = models.TextField()
    status = models.CharField(max_length=50, choices=[
        ('programada', 'Programada'),
        ('em_execucao', 'Em Execução'),
        ('atrasada', 'Atrasada')
    ], default='Programada')
    duracao_estimada = models.FloatField(help_text="Duração estimada em horas", null=True)
    duracao_real = models.FloatField(help_text="Duração real em horas", null=True)
    data_ultima_manutencao = models.DateField(null=True, blank=True)
    data_proxima_manutencao = models.DateField(null=True, blank=True)
    horimetro_atual = models.FloatField(null=True, blank=True)
    periodo_meses = models.IntegerField(null=True, blank=True)
    horas_intervalo = models.FloatField(null=True, blank=True)
    procedimentos = models.FileField(upload_to='procedimento_pdfs/', blank=True, null=True)

    @property
    def possui_os_aberta(self):
        """Verifica se existe uma OS em andamento para esta manutenção"""
        from gestaoOS.models import Chamado
        return Chamado.objects.filter(
            equipamento=self.equipamento,
            tipo_manutencao='preventiva',
            status__in=['pendente', 'em_andamento', 'aguardando_peca']
        ).exists()

    @classmethod
    def atualizar_todos_status(cls):
        """Atualiza o status de todas as manutenções"""
        hoje = date.today()
        
        # Atualiza para 'atrasada' as manutenções que já passaram da data
        cls.objects.filter(
            data_proxima_manutencao__lt=hoje,
            status='programada'
        ).update(status='atrasada')
        
        # Retorna ao status 'programada' se a data foi atualizada para uma futura
        cls.objects.filter(
            data_proxima_manutencao__gte=hoje,
            status='atrasada'
        ).update(status='programada')


    @property
    def custo_total_pecas(self):
        return sum(pm.custo_total for pm in self.pecas_necessarias.all())

    def calcular_proxima_manutencao(self):
        if not self.data_ultima_manutencao or not self.periodo_meses:
            return None
            
        data_ultima = self.data_ultima_manutencao
        meses = self.periodo_meses
        
        # Calcula o ano e mês da próxima manutenção
        ano = data_ultima.year + ((data_ultima.month + meses - 1) // 12)
        mes = ((data_ultima.month + meses - 1) % 12) + 1
        
        # Obtém o último dia do mês alvo
        _, ultimo_dia = monthrange(ano, mes)
        
        # Garante que o dia não ultrapasse o último dia do mês
        dia = min(data_ultima.day, ultimo_dia)
        
        return date(ano, mes, dia)
    
    def save(self, *args, **kwargs):
        if self.data_ultima_manutencao and self.tipo_calculo in ['meses', 'ambos'] and self.periodo_meses:
            self.data_proxima_manutencao = self.calcular_proxima_manutencao()
            
        # Verifica se está atrasada ao salvar
        if self.data_proxima_manutencao and self.data_proxima_manutencao < date.today():
            if self.status != 'em_execucao':  # Não altera se estiver em execução
                self.status = 'atrasada'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Manutenção: {self.equipamento.nome}"

    def get_absolute_url(self):
        return reverse('listar_manutencoes')
    
class PecasManutencao(models.Model):
    manutencao = models.ForeignKey(
        ManutencaoPreventiva, on_delete=models.CASCADE, related_name="pecas_necessarias"
    )
    peca = models.ForeignKey(
        'cadEstoque.Pecas', on_delete=models.CASCADE, related_name="manutencoes_necessarias"
    )
    quantidade = models.PositiveIntegerField(default=1)

    @property
    def custo_total(self):
        return self.peca.custo * self.quantidade

    def __str__(self):
        return f"{self.quantidade}x {self.peca.descricao} para {self.manutencao}"
