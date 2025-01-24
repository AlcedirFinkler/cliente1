from django.core.management.base import BaseCommand
from GestaoPrev.models import ManutencaoPreventiva

class Command(BaseCommand):
    help = 'Atualiza o status de todas as manutenções preventivas'

    def handle(self, *args, **kwargs):
        ManutencaoPreventiva.atualizar_todos_status()
        self.stdout.write(self.style.SUCCESS('Status das manutenções atualizados com sucesso!'))