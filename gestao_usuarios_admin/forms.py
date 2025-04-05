# forms.py from gestao_usuarios_admin 
from django import forms
from django.contrib.auth.models import User, Group
from gestaoUsuarios.models import CadastroPendente
from gestaoOS.models import Setor

class UsuarioPendenteForm(forms.ModelForm):
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(), 
        label="Grupo",
        required=True
    )
    senha = forms.CharField(
        widget=forms.PasswordInput, 
        label="Senha",
        required=False,
        help_text="Deixe em branco para manter a senha atual"
    )

    class Meta:
        model = CadastroPendente
        fields = ['username', 'email', 'grupo', 'senha', 'is_approved']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Importante: Inicializa o campo de senha com o valor atual do modelo
            # (não será mostrado visualmente devido ao widget PasswordInput,
            # mas estará disponível para o processamento do formulário)
            self.initial['senha'] = self.instance.senha
            
            # Processamento do grupo
            grupo_val = self.instance.grupo
            if isinstance(grupo_val, str):
                try:
                    grupo_obj = Group.objects.get(name=grupo_val)
                    self.initial['grupo'] = grupo_obj.pk
                except Group.DoesNotExist:
                    print(f"Grupo '{grupo_val}' não encontrado para o usuário {self.instance.username}")
            elif hasattr(grupo_val, 'pk'):
                self.initial['grupo'] = grupo_val.pk
            else:
                try:
                    grupo_obj = Group.objects.get(pk=grupo_val)
                    self.initial['grupo'] = grupo_obj.pk
                except (Group.DoesNotExist, ValueError, TypeError):
                    print(f"Valor de grupo inválido: {grupo_val} para o usuário {self.instance.username}")

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # IMPORTANTE: Se a senha não foi fornecida no formulário, 
        # mantém a senha original do modelo
        senha_form = self.cleaned_data.get('senha')
        if senha_form:
            instance.senha = senha_form
        # Caso contrário, mantém a senha original (que já está no instance)
        
        # Armazena o grupo como string (nome do grupo)
        if self.cleaned_data.get('grupo'):
            grupo_obj = self.cleaned_data['grupo']
            instance.grupo = grupo_obj.name
            
        if commit:
            instance.save()
        return instance

class NovoUsuarioForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput, 
        label="Senha",
        required=True
    )
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(), 
        label="Grupo",
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        group = self.cleaned_data['grupo']
        user.groups.add(group)
        return user

class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ['nome']