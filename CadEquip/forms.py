from django import forms
from .models import Equipamento
from gestaoOS.models import Setor
from CadFornecedor.models import Fornecedor

class EquipamentoForm(forms.ModelForm):
    setor = forms.ModelChoiceField(
        queryset=Setor.objects.all(),
        required=True,
        label='Setor Responsável'
    )
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.all(),
        required=False,  # Tornar obrigatório, se necessário
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Selecione um fornecedor",
        label="Fornecedor"
    )
    
    class Meta:
        model = Equipamento
        fields = [
            'nome', 'modelo', 'fabricante', 'tag', 'patrimonio', 'local', 
            'numero_serie', 'setor', 'ano_fabricacao', 'ssma', 'qualidade', 'operacao', 'entrega', 'mtbf', 'mttr', 'classe', 'manual_operacao', 'garantia_termino', 'foto'
        ]
        labels = {
            'nome': '*Nome do Equipamento:',
            'modelo': '*Modelo:',
            'fabricante': '*Fabricante:',
            'tag': 'Tag do Equipamento:',
            'patrimonio': 'Número de Patrimônio:',
            'local': 'Localização:',
            'numero_serie': 'Número de Série:',
            'setor': '*Setor:',
            'ano_fabricacao': 'Ano de Fabricação:',
            'foto':'Foto:',
            'garantia_termino': 'Término da garantia:',
            'manual_operacao': 'Manual Operacao e Manutenção:',
            'ssma': 'SSMA:',
            'qualidade': 'Qualidade:',
            'operacao': 'Operação:',
            'entrega': 'Entrega:',
            'mttr': 'MTTR:',
            'mtbf': 'MTBF:',
            'classe': 'Classe:',
        }
        widgets = {
            'setor': forms.Select(attrs={'class': 'form-select'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'fabricante': forms.TextInput(attrs={'class': 'form-control'}),
            'tag': forms.TextInput(attrs={'class': 'form-control'}),
            'patrimonio': forms.TextInput(attrs={'class': 'form-control'}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'ano_fabricacao': forms.TextInput(attrs={'class': 'form-control'}),
            'ssma': forms.Select(attrs={'class': 'form-select'}),
            'qualidade': forms.Select(attrs={'class': 'form-select'}),
            'operacao': forms.Select(attrs={'class': 'form-select'}),
            'entrega': forms.Select(attrs={'class': 'form-select'}),
            'mttr': forms.Select(attrs={'class': 'form-select'}),
            'mtbf': forms.Select(attrs={'class': 'form-select'}),
            'classe': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar todos os campos não obrigatórios inicialmente
        for field in self.fields.values():
            field.required = False
        # Tornar os campos específicos obrigatórios
        self.fields['nome'].required = True
        self.fields['modelo'].required = True
        self.fields['fabricante'].required = True
        self.fields['setor'].required = True
        self.fields['fornecedor'].required = False
        infra_setor = Setor.objects.filter(nome="Infraestrutura").first()
        if infra_setor:
            self.fields['setor'].initial = infra_setor.id
        print(self.fields['fornecedor'].queryset)  # Verificar se o queryset é carregado corretamente
  
    def clean_patrimonio(self):
        patrimonio = self.cleaned_data.get('patrimonio')
        
        # If patrimonio is empty or None, return None
        if not patrimonio or patrimonio.strip() == '':
            return None
        
        # Check for existing patrimonio only if a value is provided
        if Equipamento.objects.filter(patrimonio=patrimonio).exists():
            raise forms.ValidationError("Este número de patrimônio já está cadastrado.")
        
        return patrimonio

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make patrimonio optional
        self.fields['patrimonio'].required = False
