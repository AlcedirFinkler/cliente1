# views.py from app gestaoUsuarios
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from .forms import LoginForm, CadastroForm
from .models import CadastroPendente
from .services import WeconnService
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
from django.http import JsonResponse


TENTATIVAS_MAXIMAS = 5
DURAÇÃO_DO_BLOQUEIO = timedelta(minutes=5)

@login_required
def get_modules_json(request):
    modules = get_user_modules(request.user)
    return JsonResponse({'modules': modules})

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
    # Verifica o status do pagamento do tenant
    weconn_service = WeconnService()
    access_status = weconn_service.check_access_status()
    payment_status = weconn_service.get_payment_status()
    plan_info = weconn_service.get_plan_info()
       
    # Limpar o cache da sessão para forçar uma nova verificação
    if 'tenant_access_status' in request.session:
        del request.session['tenant_access_status']
    if 'tenant_payment_status' in request.session:
        del request.session['tenant_payment_status']
    if 'tenant_plan_info' in request.session:
        del request.session['tenant_plan_info']
    
    # Guarda as informações do tenant na sessão
    request.session['tenant_access_status'] = access_status
    request.session['tenant_payment_status'] = payment_status
    request.session['tenant_plan_info'] = plan_info

    # Verifica se o pagamento está expirado ANTES de qualquer tentativa de login
    if access_status == 'expired' or access_status == 'blocked' or payment_status == 'expirado':
        # Redirecionar para a página de pagamento expirado sem fazer login
        return render(request, 'usuarios/pagamento_expirado.html')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(f"Login solicitado para {username}")

            if usuario_bloqueado(username):
                messages.error(request, "Muitas tentativas falhas. Tente novamente mais tarde.")
                return redirect('login')

            try:
                cadastro = CadastroPendente.objects.get(username=username)
                print(f"Cadastro encontrado: {cadastro.username}")

                if not cadastro.is_approved:
                    messages.error(request, "Aguardando aprovação!")
                    return redirect('login')
                               
                user = authenticate(request, username=username, password=password)               

                if user is not None:
                    testegrupo = user.groups.first().name if user.groups.exists() else None
                    print(f"Grupo do usuário: {testegrupo}")
                    print(user)

                    login(request, user)
                    reiniciar_tentativas(username)

                    # Verificar status de pagamento
                    if access_status == 'expired' or access_status == 'blocked' or payment_status == 'expirado':
                        return redirect('pagamento_expirado')
                    elif access_status == 'grace_period' or payment_status == 'atraso':
                        # Redirecionar para aviso de atraso, mas permitirá continuar
                        return redirect('pagamento_atrasado')

                    if testegrupo == "Solicitante":
                        print('Renderiza solicitante!')
                        return redirect('tela_inicial')
                    elif testegrupo == "Estoquista":
                        print('Renderiza Estoquista!')
                        return redirect('selecao_modulos')
                    elif testegrupo == "Técnico":
                        print('Renderiza técnico!')
                        return redirect('tela_inicial')
                    elif testegrupo == "Gestor":
                        print('Renderiza gestores!')
                        return redirect('selecao_modulos')
                    else:
                        return redirect('tela_inicial')
                else:
                    aumentar_numero_de_tentativas(username)
                    messages.error(request, "Usuário ou senha incorretos.")
                    return redirect('login')
                    
            except CadastroPendente.DoesNotExist:
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

            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, "O email fornecido é inválido. Por favor, insira um email válido.")
                return redirect('cadastro')
            
            if form.cleaned_data['password'] != form.cleaned_data['password_confirm']:
                messages.error(request, "As senhas não conferem.")
                return redirect('cadastro')

            if User.objects.filter(username=username).exists():
                messages.error(request, "O nome de usuário já está em uso. Escolha outro.")
                return redirect('cadastro')

            if User.objects.filter(email=email).exists():
                messages.error(request, "Este email já está cadastrado.")
                return redirect('cadastro')

            if CadastroPendente.objects.filter(username=username).exists():
                messages.error(request, "Este nome de usuário já está aguardando aprovação.")
                return redirect('cadastro')

            if CadastroPendente.objects.filter(email=email).exists():
                messages.error(request, "Este email já está aguardando aprovação.")
                return redirect('cadastro')

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

def get_user_modules(user):
    """
    Define os módulos disponíveis para o usuário baseado em seu grupo
    """
    # Configuração padrão: todos os módulos desativados
    modules = [
        {"name": "Tela Inicial", "url": reverse('selecao_modulos'), "icon": "bi-house", "enabled": False},
        {"name": "Gestão OSs", "url": reverse('tela_inicial'), "icon": "bi-clipboard-check", "enabled": False},
        {"name": "Mant. Preventivas", "url": reverse('listar_manutencoes'), "icon": "bi-tools", "enabled": False,
          "submenu": [
             {"name": "Tabelas", "url": reverse('listar_manutencoes')},
             {"name": "Gráfico Gantt", "url": reverse('gantt_manutencoes')}
         ]},
        {"name": "Controle Estoque", "url": reverse('cadEstoque'), "icon": "bi-box", "enabled": False},
        {"name": "Cadastro Equipamentos", "url": reverse('CadEquip'), "icon": "bi-gear", "enabled": False},
        {"name": "Cadastro Fornecedores", "url": reverse('CadFornecedor'), "icon": "bi-building", "enabled": False},
        {"name": "Relatórios", "url": reverse('relatorios_index'), "icon": "bi-file-earmark-text", "enabled": False,
         "submenu": [
             {"name": "Peças", "url": reverse('relatorio_pecas')},
             {"name": "Técnicos", "url": reverse('relatorio_tecnicos')},
             {"name": "Indicadores", "url": reverse('relatorio_indicadores')}
         ]},
        {"name": "Configurações", "url": reverse('listar_usuarios_pendentes'), "icon": "bi-person-fill-gear", "enabled": False,
         "submenu": [
             {"name": "Usuários Pendentes", "url": reverse('listar_usuarios_pendentes')},
             {"name": "Criar Setor", "url": reverse('criar_setor')},
        ]},
        {"name": "Horimetros", "url": reverse('device_list'), "icon": "bi-clock", "enabled": False}
    ]
    
    # Se for gestor, ativa todos os módulos
    if user.groups.filter(name="Gestor").exists():
        for module in modules:
            module["enabled"] = True
        return modules
    
    # Se for estoquista, ativa apenas módulos específicos
    elif user.groups.filter(name="Estoquista").exists():
        for module in modules:
            if module["name"] in ["Tela Inicial", "Controle Estoque", "Cadastro Fornecedores", "Relatórios"]:
                module["enabled"] = True
        return modules
    
    # Se for técnico
    elif user.groups.filter(name="Técnico").exists():
        for module in modules:
            if module["name"] in ["Tela Inicial", "Gestão OSs", "Mant. Preventivas"]:
                module["enabled"] = True
        return modules
    
    # Se for solicitante
    elif user.groups.filter(name="Solicitante").exists():
        for module in modules:
            if module["name"] in ["Tela Inicial", "Gestão OSs"]:
                module["enabled"] = True
        return modules
    
    # Para outros casos ou usuários sem grupo
    return modules

@login_required
def modulos(request):
    request.user.refresh_from_db()  
    modules = get_user_modules(request.user)
    context = {'modules': modules}
    
    return render(request, 'usuarios/selecao_modulos.html', context)


# Adicionar as funções para pagamento_atrasado e pagamento_expirado
def pagamento_atrasado(request):
    """
    Exibe um alerta de pagamento em atraso, mas permite continuar.
    """
    if request.method == 'POST':
        # Quando o usuário clicar em "Continuar"
        user = request.user
        grupo = user.groups.first().name if user.groups.exists() else None
        
        if grupo == "Solicitante":
            return redirect('tela_inicial')
        elif grupo == "Estoquista":
            return redirect('selecao_modulos')
        elif grupo == "Técnico":
            return redirect('tela_inicial')
        elif grupo == "Gestor":
            return redirect('selecao_modulos')
        else:
            return redirect('tela_inicial')
    
    return render(request, 'usuarios/pagamento_atrasado.html')

def pagamento_expirado(request):
    """
    Exibe uma tela de pagamento expirado e não permite continuar.
    """
    return render(request, 'usuarios/pagamento_expirado.html')


@login_required
def selecao_modulos(request):
    modules = get_user_modules(request.user)
    is_estoquista = request.user.groups.filter(name="Estoquista").exists()
    is_gestor = request.user.groups.filter(name="Gestor").exists()
    
    # Obtém as informações do tenant (plano e status de pagamento)
    weconn_service = WeconnService()
    payment_status = weconn_service.get_payment_status()
    plan_info = weconn_service.get_plan_info()
    
    context = {
        'modules': modules,
        'is_estoquista': is_estoquista,
        'is_gestor': is_gestor,
        'tenant_payment_status': payment_status,
        'tenant_plan_info': plan_info,
    }
    
    if is_estoquista:
        context.update({
            'pecas_estoque_minimo': Pecas.objects.filter(estoque_atual__lt=F('estoque_minimo')),
            'pecas_proximas_estoque': Pecas.objects.filter(
                estoque_atual__gte=F('estoque_minimo'),
                estoque_atual__lt=F('estoque_minimo') * 1.2
            ),
        })
    else:
        duas_semanas = datetime.now() + timedelta(weeks=2)
        context.update({
            'manutencoes_atrasadas': ManutencaoPreventiva.objects.filter(
                data_proxima_manutencao__lt=datetime.now(), 
                status='atrasada'
            ),
            'oss_pendentes': Chamado.objects.filter(status='pendente'),
            'pecas_estoque_minimo': Pecas.objects.filter(estoque_atual__lt=F('estoque_minimo')),
            'usuarios_pendentes': CadastroPendente.objects.filter(is_approved=False),
            'proximas_manutencoes': ManutencaoPreventiva.objects.filter(
                data_proxima_manutencao__lte=duas_semanas, 
                status='programada'
            ),
        })
    
    return render(request, 'usuarios/selecao_modulos.html', context)
