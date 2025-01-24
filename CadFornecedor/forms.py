from django import forms
from .models import Fornecedor

from django.contrib.auth.forms import AuthenticationForm


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = [
            'fornecedor', 'fornecedor_fone', 'fornecedor_site', 'fornecedor_email', 'rua', 'numero', 'cidade', 'cep', 'estado', 'contato', 'cnpj', 'observacoes', 'bairro', 'inscricao_estadual', 'prazo_entrega_medio'
        ]
        labels = {
            'fornecedor': '*Fornecedor:',
            'fornecedor_fone': '*Telefone do Fornecedor:',
            'fornecedor_site': 'Site do Fornecedor:',
            'fornecedor_email': 'E-mail do Fornecedor:',
            'prazo_entrega_medio': 'Prazo médio de entrega:',
            'rua': 'Rua:',
            'numero': 'Número:',
            'bairro': 'Bairro:',
            'cidade': 'Cidade:',
            'cep': 'CEP:',
            'estado': 'Estado:',
            'contato': 'Contato:',
            'cnpj': 'CNPJ:',
            'inscricao_estadual': 'INSC:',
            'observacoes': 'Observações:'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar todos os campos não obrigatórios inicialmente
        for field in self.fields.values():
            field.required = False
        # Tornar os campos específicos obrigatórios
        self.fields['fornecedor'].required = True
        self.fields['fornecedor_fone'].required = True


