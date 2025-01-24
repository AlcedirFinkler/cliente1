# forms.py do app GestaoPrev
from django import forms
from .models import ManutencaoPreventiva
from CadEquip.models import Equipamento
from cadEstoque.models import Pecas

class PecasQuantidadeForm(forms.Form):
    peca = forms.ModelChoiceField(
        queryset=Pecas.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False
    )
    quantidade = forms.IntegerField(
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        initial=1,
        required=False
    )

class ManutencaoPreventivaForm(forms.ModelForm):
    pecas_quantidade = forms.Field(required=False, widget=forms.HiddenInput)
    
    equipamento = forms.ModelChoiceField(
        queryset=Equipamento.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="Selecione o Equipamento:",
        required=True
    )
    
    pecas = forms.ModelMultipleChoiceField(
        queryset=Pecas.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        required=False
    )

    class Meta:
        model = ManutencaoPreventiva
        fields = [
            'equipamento', 'descricao', 'tipo_calculo',
            'requer_parada', 'data_ultima_manutencao', 'horimetro_atual',
            'periodo_meses', 'horas_intervalo', 'procedimentos', 'pecas', 'duracao_estimada', 'media_horas', 'duracao_real', 'status'
        ]
        labels = {
            'duracao_estimada': 'Duração em horas:',
            'media_horas': 'Média de horas semanais:',
        }
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'tipo_calculo': forms.Select(attrs={'class': 'form-control'}),
            'data_ultima_manutencao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'horimetro_atual': forms.NumberInput(attrs={'class': 'form-control'}),
            'periodo_meses': forms.NumberInput(attrs={'class': 'form-control'}),
            'horas_intervalo': forms.NumberInput(attrs={'class': 'form-control'}),
            'duracao_estimada': forms.NumberInput(attrs={'class': 'form-control'}), 
            'media_horas': forms.NumberInput(attrs={'class': 'form-control'}),
            'duracao_real': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar todos os campos não obrigatórios inicialmente
        for field in self.fields.values():
            field.required = False
        # Tornar os campos específicos obrigatórios
        self.fields['equipamento'].required = True
        self.fields['descricao'].required = True
        self.fields['tipo_calculo'].required = True
        self.fields['requer_parada'].required = True