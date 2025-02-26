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
        required=False
    )

    class Meta:
        model = CadastroPendente
        fields = ['username', 'email', 'grupo', 'senha', 'is_approved']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            grupo_val = self.instance.grupo
            if not isinstance(grupo_val, Group):
                try:
                    grupo_obj = Group.objects.get(name=grupo_val)
                    self.initial['grupo'] = grupo_obj.pk
                except Group.DoesNotExist:
                    pass
            else:
                self.initial['grupo'] = grupo_val.pk

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('senha'):
            instance.senha = self.cleaned_data['senha']
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