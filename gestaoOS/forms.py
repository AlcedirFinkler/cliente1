# forms.py do app gestaoOS
from django import forms
from .models import Chamado, Setor, Acao, AcaoPeca, AcaoColaborador 
from django.contrib.auth.models import User

from django.contrib.auth.forms import AuthenticationForm
from CadEquip.models import Equipamento


class ChamadoForm(forms.ModelForm):
    tecnico = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Técnico'),  # Filtra apenas usuários no grupo "Técnico"
        required=False,
        label='Técnico Responsável',
        empty_label="Selecione um técnico"
    )
    setor = forms.ModelChoiceField(
        queryset=Setor.objects.all(),
        required=True,
        label='Setor Responsável'
    )

    tipo_manutencao = forms.ChoiceField(
        choices=Chamado.TIPO_MANUTENCAO_CHOICES,
        initial='nao_informado',
        label='Tipo de Manutenção'
    )
    local = forms.CharField(
        max_length=150,
        required=False,
        label='Local',
        widget=forms.TextInput(attrs={'placeholder': 'Especifique o local da manutenção'}),
    )
    foto = forms.ImageField(
        required=False,
        label='Foto do Chamado'
    )

    equipamento = forms.ModelChoiceField(
        queryset=Equipamento.objects.all(),
        required=False,
        label='Equipamento'
    )

    class Meta:
        model = Chamado
        fields = ['titulo', 'setor', 'descricao', 'status', 'tecnico', 'tipo_manutencao', 'local', 'equipamento', 'foto', 'diagnostico', 'solucao', 'causa_raiz']
        labels = {
            'titulo': 'Título do Chamado',
            'setor': 'Setor Responsável',
            'descricao': 'Descrição do Problema',
            'status': 'Status',
            'equipamento': 'Equipamento',
            'diagnostico': 'Diagnóstico:', 
            'solucao': 'Solução:', 
            'causa_raiz': 'Causa Raiz'
        }
        error_messages = {
            'titulo': {
                'required': 'O título é obrigatório.',
            },
            'descricao': {
                'required': 'Por favor, forneça detalhes sobre o problema.',
            },
        }

    def __init__(self, *args, **kwargs):
        # Captura o parâmetro 'user', mas não o passa adiante
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['tecnico'].queryset = User.objects.filter(groups__name='Técnico')
        
        # Remove campos para usuários que não sejam superusuários
        if user and not user.is_superuser:
            self.fields.pop('status', None)
            self.fields.pop('tecnico', None)
        
        # Filtra as opções do campo tipo_manutencao
        self.fields['tipo_manutencao'].choices = [
            ('corretiva', 'Corretiva'),
            ('melhoria', 'Melhoria'),
        ]


class AcaoForm(forms.ModelForm): 
    peca = forms.CharField(required=False, widget=forms.HiddenInput())
    quantidade = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Acao
        fields = ['descricao', 'duracao', 'arquivos']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'descricao': 'Descrição da Ação',
            'duracao': 'Duração (horas)',
            'arquivos': 'Arquivos (PDFs)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add fields for dynamically handling collaborators and parts
        self.fields['colaboradores'] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields['horas'] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields['atividades'] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields['pecas'] = forms.CharField(required=False, widget=forms.HiddenInput())
        self.fields['quantidades'] = forms.CharField(required=False, widget=forms.HiddenInput())

    def save(self, commit=True):
        acao = super().save(commit=False)
        if commit:
            acao.save()
        return acao

    def clean(self):
        cleaned_data = super().clean()
        colaboradores = cleaned_data.get('colaboradores')
        horas = cleaned_data.get('horas')
        atividades = cleaned_data.get('atividades')
        pecas = cleaned_data.get('pecas')
        quantidades = cleaned_data.get('quantidades')

        # Here you would validate that lists are not empty if required, lengths match, etc.
        return cleaned_data

class FinalizarChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = ['diagnostico', 'solucao', 'causa_raiz']
        labels = {
            'diagnostico': 'Diagnóstico',
            'solucao': 'Solução',
            'causa_raiz': 'Causa Raiz'
        }
        widgets = {
            'diagnostico': forms.Textarea(attrs={'rows': 4}),
            'solucao': forms.Textarea(attrs={'rows': 4}),
            'causa_raiz': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

class FinalizarChamadoGestorForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = ['status', 'tecnico']
        labels = {
            'status': 'Status',
            'tecnico': 'Técnico'
        }
        error_messages = {
            'status': {
                'required': "Preenchimento desse campo é obrigatório!"
            },
            'tecnico': {
                'required': "Preenchimento desse campo é obrigatório!"
            }
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        
        return cleaned_data