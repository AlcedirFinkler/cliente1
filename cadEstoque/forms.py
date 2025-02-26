from django import forms
from .models import Pecas
from CadFornecedor.models import Fornecedor
from django.core.exceptions import ValidationError

class PecasForm(forms.ModelForm):
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Selecione um fornecedor",
        label="FornecedorPeca"
    )
    
    class Meta:
        model = Pecas
        fields = ['descricao', 'codigo', 'estoque_minimo', 'estoque_atual', 'preco', 'foto', 'orcamentos', 'unidade_medida', 'localizacao', 'data_ultima_compra', 'vida_util', 'observacoes'] 
        labels = {
            'descricao': 'Descrição da peça:',
            'codigo': 'Código da peça:',
            'estoque_minimo': 'Estoque mínimo:',
            'estoque_atual': 'Estoque atual',
            'unidade_medida': 'Unidade de medida:',
            'localizacao': 'Localização:',
            'data_ultima_compra': 'Data última compra',
            'vida_util':'Vida útil (meses):',
            'preco': 'Preço (R$)',
            'foto':'Foto da peça:',
            'orcamentos': 'Orçamento (PDFs)',
            'observacoes': 'Observações:',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar todos os campos não obrigatórios inicialmente
        for field in self.fields.values():
            field.required = False
        # Tornar os campos específicos obrigatórios
        self.fields['codigo'].required = True
        self.fields['descricao'].required = True
        self.fields['data_ultima_compra'].input_formats = ['%d/%m/%Y']

    def clean_codigo(self):
        codigo = self.cleaned_data.get("codigo")
        qs = Pecas.objects.filter(codigo=codigo)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Uma peça com este código já está cadastrada.")
        return codigo