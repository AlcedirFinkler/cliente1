from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label="Usuário")
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")

class CadastroForm(forms.Form):
    username = forms.CharField(max_length=150, label="Usuário")
    email = forms.CharField(label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmar senha")
    grupo = forms.ChoiceField(choices=[("Solicitante", "Solicitante"), ("Técnico", "Técnico"), ("Estoquista", "Estoquista"), ("Gestor", "Gestor")], label="Grupo")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError('O e-mail informado é inválido.')
        
        return email