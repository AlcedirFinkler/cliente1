from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from .forms import LoginForm, CadastroForm
from .models import CadastroPendente
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import timedelta, datetime
from django.core.cache import cache
from django.db.models import Q, F
from CadFornecedor.models import Fornecedor
from gestaoOS.models import Chamado
from GestaoPrev.models import ManutencaoPreventiva
from cadEstoque.models import Pecas
from django.contrib.auth.models import User

TENTATIVAS_MAXIMAS = 5
DURAÇÃO_DO_BLOQUEIO = timedelta(minutes=5)

def usuario_bloqueado(user):
    chave_bloqueio = f"login_bloqueado_{user}"
    return cache.get(chave_bloqueio) is not None

def aumentar_numero_de_tentativas(user):
    chave_tentativas = f"login_tentativas_{user}"
    tentativas = cache.get(chave_tentativas, 0) + 1
    cache.set(chave_tentativas, tentativas, timeout=DURAÇÃO_DO_BLOQUEIO.seconds)

    if tentativas >= TENTATIVAS_MAXIMAS:
        chave_bloqueio = f"login_bloqueado_{user}"
        cache.set(chave_bloqueio, True, timeout=DURAÇÃO_DO_BLOQUEIO.seconds)

def reiniciar_tentativas(user):
    chave_tentativas = f"login_tentativas_{user}"
    cache.delete(chave_tentativas)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Verifica se o usuário existe na tabela de pendentes
            print(f"Login solicitado para {username}")

            if usuario_bloqueado(username):
                messages.error(request, "Muitas tentativas falhas. Tente novamente mais tarde.")
                return redirect('login')

            try:
                cadastro = CadastroPendente.objects.get(username=username)
                print(f"Cadastro encontrado: {cadastro.username}")

                # Verifica se o cadastro está aprovado
                if not cadastro.is_approved:
                    messages.error(request, "Aguardando aprovação!")
                    return redirect('login')
                
                # Se aprovado, tenta autenticar o usuário
                print('Tentando autenticar usuário...')
                print(f"Senha fornecida: {password}")
                
                user = authenticate(request, username=username, password=password)               

                if user is not None:  # Verifica se o usuário foi autenticado corretamente
                    testegrupo=user.groups.first().name
                    print(f"Grupo do usuário: {testegrupo}")
                    print(user)

                    login(request, user)
                    group_name = user.groups.first().name if user.groups.exists() else None
                    print(f"Grupo do usuário: {group_name}")

                    reiniciar_tentativas(username)

                    # Redireciona de acordo com o grupo do usuário
                    if group_name == "Solicitante":
                        print('Renderiza solicitante!')
                        return redirect('tela_inicial')
                        #return redirect('solicitantes_home')
                    elif group_name == "Estoquista":
                        print('Renderiza Estoquista!')
                        return redirect('modulos')
                        #return redirect('tecnicos_home')
                    elif group_name == "Técnico":
                        print('Renderiza técnico!')
                        return redirect('tela_inicial')
                        #return redirect('tecnicos_home')
                    elif group_name == "Gestor":
                        print('Renderiza gestores!')
                        return redirect('selecao_modulos')
                        #return redirect('gestores_home')
                else:
                    aumentar_numero_de_tentativas(username)
                    messages.error(request, "Usuário ou senha incorretos.")
                    return redirect('login')
                    
                        
            except CadastroPendente.DoesNotExist:
                print('Usuário não cadastrado')
                messages.error(request, "Usuário não cadastrado.")
                return redirect('login')
               
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

def cadastro_view(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']

            # Validação do formato do email
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, "O email fornecido é inválido. Por favor, insira um email válido.")
                return redirect('cadastro')
            
            if form.cleaned_data['password'] != form.cleaned_data['password_confirm']:
                messages.error(request, "As senhas não conferem.")
                return redirect('cadastro')

            # Verifica se o username já existe no banco de dados
            if User.objects.filter(username=username).exists():
                messages.error(request, "O nome de usuário já está em uso. Escolha outro.")
                return redirect('cadastro')

            # Verifica se o email já está cadastrado
            if User.objects.filter(email=email).exists():
                messages.error(request, "Este email já está cadastrado.")
                return redirect('cadastro')

            # Verifica se o username está na tabela de pendentes
            if CadastroPendente.objects.filter(username=username).exists():
                messages.error(request, "Este nome de usuário já está aguardando aprovação.")
                return redirect('cadastro')

            # Verifica se o email está na tabela de pendentes
            if CadastroPendente.objects.filter(email=email).exists():
                messages.error(request, "Este email já está aguardando aprovação.")
                return redirect('cadastro')

            # Criação do cadastro pendente
            CadastroPendente.objects.create(
                username=username,
                email=email,
                senha=form.cleaned_data['password'],
                grupo=form.cleaned_data['grupo']
            )
            messages.success(request, "Cadastro realizado com sucesso! Aguarde aprovação.")
            return redirect('login')
        else:        
            if 'email' in form.errors:
                messages.error(request, "O email fornecido é inválido.")
    else:
        form = CadastroForm()
    return render(request, 'usuarios/cadastro.html', {'form': form})

def aprovar_cadastro(request, cadastro_id):
    cadastro = CadastroPendente.objects.get(id=cadastro_id)
    user = User.objects.create_user(
        username=cadastro.username,
        email=cadastro.email,
        password=cadastro.senha
    )
    group = Group.objects.get(name=cadastro.grupo)
    user.groups.add(group)
    cadastro.delete()
    return redirect('/admin/')

"""
def solicitantes_home(request):
    return render(request, 'dashboard.html')

def tecnicos_home(request):
    return render(request, 'usuarios/tecnicos.html')

def gestores_home(request):
    return render(request, 'usuarios/gestores.html')
"""

@login_required
def modulos(request):
    if request.user.groups.filter(name="Gestor").exists():
        modules = [
            {"name": "Gestão OSs", "url": reverse('tela_inicial'), "enabled": True},
            {"name": "Mant. Preventivas", "url": reverse('listar_manutencoes'), "enabled": True},
            {"name": "Controle Estoque", "url": reverse('cadEstoque'), "enabled": True},
            {"name": "Cadastro Equipamentos", "url": reverse('CadEquip'), "enabled": True},
            {"name": "Cadastro Fornecedores", "url": reverse('CadFornecedor'), "enabled": True},
            {"name": "Relatórios", "url": reverse('relatorios_index'), "enabled": True},  
            {"name": "Gestão Usuários", "url": reverse('listar_usuarios_pendentes'), "enabled": True},
            # Adicione até o total de 12 módulos
        ]
        return render(request, 'usuarios/selecao_modulos.html', {'modules': modules})
    
    if request.user.groups.filter(name="Estoquista").exists():
        modules = [
            {"name": "Gestão OSs", "url": reverse('tela_inicial'), "enabled": False},
            {"name": "Mant. Preventivas", "url": reverse('listar_manutencoes'), "enabled": False},
            {"name": "Controle Estoque", "url": reverse('cadEstoque'), "enabled": True},
            {"name": "Cadastro Equipamentos", "url": reverse('CadEquip'), "enabled": False},
            {"name": "Cadastro Fornecedores", "url": reverse('CadFornecedor'), "enabled": True},
            {"name": "Relatórios", "url": reverse('relatorios_index'), "enabled": True},
            {"name": "Gestão Usuários", "url": "/modulo6/", "enabled": False},
            # Adicione até o total de 12 módulos
        ]
        return render(request, 'usuarios/selecao_modulos.html', {'modules': modules})

@login_required
def selecao_modulos(request):
    manutencoes_atrasadas = ManutencaoPreventiva.objects.filter(
        data_proxima_manutencao__lt=datetime.now(), status='atrasada'
    )

    oss_pendentes = Chamado.objects.filter(status='pendente')

    pecas_estoque_minimo = Pecas.objects.filter(estoque_atual__lt=F('estoque_minimo'))

    usuarios_pendentes = User.objects.filter(is_active=False)

    duas_semanas = datetime.now() + timedelta(weeks=2)
    proximas_manutencoes = ManutencaoPreventiva.objects.filter(
        data_proxima_manutencao__lte=duas_semanas, status='programada'
    )

    context = {
        'manutencoes_atrasadas': manutencoes_atrasadas,
        'oss_pendentes': oss_pendentes,
        'pecas_estoque_minimo': pecas_estoque_minimo,
        'usuarios_pendentes': usuarios_pendentes,
        'proximas_manutencoes': proximas_manutencoes,
    }
    return render(request, 'usuarios/selecao_modulos.html', context)
