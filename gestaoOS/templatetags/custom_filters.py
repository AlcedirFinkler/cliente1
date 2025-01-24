# gestaoOS/templatetags/custom_filters.py

from django import template
from ..models import Acao  # Substitua pelo nome correto do modelo

register = template.Library()

@register.filter
def filtrar_acoes(chamado):
    """
    Retorna todas as ações associadas a um determinado chamado.
    """
    return Acao.objects.filter(chamado=chamado)
