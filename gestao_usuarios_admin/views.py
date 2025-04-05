# views.py from gestao_usuarios_admin 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User, Group
from gestaoUsuarios.models import CadastroPendente
from .forms import UsuarioPendenteForm, NovoUsuarioForm, SetorForm
from gestaoOS.models import Setor

def is_gestor(user):
    """Verifica se o usuário é do grupo Gestor"""
    return user.groups.filter(name='Gestor').exists()

@login_required
@user_passes_test(is_gestor)
def listar_usuarios_pendentes(request):
    # [Código existente - não alterado]
    usuarios_pendentes = CadastroPendente.objects.all()

    usuario = request.GET.get('usuario')
    email = request.GET.get('email')
    status = request.GET.get('status')

    if usuario:
        usuarios_pendentes = usuarios_pendentes.filter(username__icontains=usuario)
    if email:
        usuarios_pendentes = usuarios_pendentes.filter(email__icontains=email)
    if status:
        if status == 'aprovados':
            usuarios_pendentes = usuarios_pendentes.filter(is_approved=True)
        elif status == 'nao_aprovados':
            usuarios_pendentes = usuarios_pendentes.filter(is_approved=False)

    context = {
        'pendentes': usuarios_pendentes,
        'usuario': usuario,
        'email': email,
        'status': status,
    }
    return render(request, 'listar_pendentes.html', context)

@login_required
@user_passes_test(is_gestor)
def editar_usuario_pendente(request, pk):
    cadastro = get_object_or_404(CadastroPendente, pk=pk)
    senha_original = cadastro.senha  # Armazena a senha original antes de qualquer alteração
    
    if request.method == 'POST':
        form = UsuarioPendenteForm(request.POST, instance=cadastro)
        if form.is_valid():
            try:
                # Verifica se o formulário tem uma nova senha
                nova_senha = form.cleaned_data.get('senha')
                
                # Se não houver nova senha, restaura a senha original
                if not nova_senha:
                    # Importante: o instance ainda não foi salvo, então podemos modificá-lo
                    form.instance.senha = senha_original
                
                # Salva o formulário, agora com a senha correta
                usuario = form.save()
                
                # Se aprovado, cria/atualiza usuário no sistema
                if usuario.is_approved:
                    # Loga as informações para depuração
                    print(f"Processando aprovação de usuário: {usuario.username}")
                    print(f"Grupo: {usuario.grupo}, Senha presente: {'Sim' if usuario.senha else 'Não'}")
                    
                    # Usar diretamente a senha do modelo (que deve estar correta agora)
                    password_for_user = usuario.senha
                    print(f"Senha que será usada: {password_for_user[:3]}*** (primeiros 3 caracteres)")
                    
                    # Verifica se já existe um usuário com esse nome
                    try:
                        user = User.objects.get(username=usuario.username)
                        user_exists = True
                    except User.DoesNotExist:
                        user_exists = False
                    
                    if user_exists:
                        # Atualiza usuário existente
                        user.email = usuario.email
                        if password_for_user:
                            user.set_password(password_for_user)
                        user.save()
                        print(f"Usuário existente {usuario.username} atualizado")
                    else:
                        # Cria um novo usuário usando a função direta do Django admin
                        if password_for_user:
                            try:
                                # Usando o método que funciona no admin
                                user = User.objects.create_user(
                                    username=usuario.username,
                                    email=usuario.email,
                                    password=password_for_user
                                )
                                print(f"Usuário {usuario.username} criado com senha")
                            except Exception as e:
                                print(f"Erro ao criar usuário com senha: {str(e)}")
                                # Fallback sem senha
                                user = User.objects.create(username=usuario.username, email=usuario.email)
                                user.set_unusable_password()
                                user.save()
                                print(f"AVISO: Usuário {usuario.username} criado sem senha devido a erro")
                        else:
                            print(f"AVISO: Nenhuma senha disponível para o usuário {usuario.username}")
                            user = User.objects.create(username=usuario.username, email=usuario.email)
                            user.set_unusable_password()
                            user.save()
                    
                    # Adiciona ao grupo correto
                    try:
                        grupo_nome = usuario.grupo
                        grupo = Group.objects.get(name=grupo_nome)
                        user.groups.clear()
                        user.groups.add(grupo)
                        print(f"Usuário {usuario.username} adicionado ao grupo {grupo_nome}")
                    except Group.DoesNotExist:
                        print(f"Erro: Grupo '{usuario.grupo}' não encontrado")
                        messages.error(request, f"Grupo '{usuario.grupo}' não encontrado.")
                
                messages.success(request, 'Usuário atualizado com sucesso!')
                return redirect('listar_usuarios_pendentes')
            except Exception as e:
                import traceback
                print(f"Erro ao processar usuário: {str(e)}")
                print(traceback.format_exc())
                messages.error(request, f'Erro ao salvar: {str(e)}')
    else:
        form = UsuarioPendenteForm(instance=cadastro)
    
    return render(request, 'editar_pendente.html', {'form': form})

@login_required
@user_passes_test(is_gestor)
def criar_usuario(request):
    # [Código existente - não alterado]
    if request.method == 'POST':
        form = NovoUsuarioForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Usuário criado com sucesso!')
                return redirect('listar_usuarios_pendentes')
            except Exception as e:
                messages.error(request, f'Erro ao criar usuário: {str(e)}')
    else:    
        form = NovoUsuarioForm()
    
    return render(request, 'criar_usuario.html', {'form': form})

@login_required
@user_passes_test(is_gestor)
def criar_setor(request):
    # [Código existente - não alterado] 
    if request.method == 'POST':
        form = SetorForm(request.POST)
        if form.is_valid():
            nome = form.cleaned_data['nome']
            if Setor.objects.filter(nome=nome).exists():
                messages.error(request, "Setor com esse nome já existe!")
            else:
                form.save()
                messages.success(request, "Setor criado com sucesso!")
                return redirect('criar_setor')
    else:
        form = SetorForm()
    return render(request, 'criar_setor.html', {'form': form, 'setores': Setor.objects.all()})