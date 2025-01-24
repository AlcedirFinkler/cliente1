from django import forms
from django.contrib.auth.models import User, Group
from gestaoUsuarios.models import CadastroPendente

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
        fields = ['username', 'email', 'grupo', 'is_approved']

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