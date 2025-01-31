from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User, Group
from gestaoUsuarios.models import CadastroPendente
from .forms import UsuarioPendenteForm, NovoUsuarioForm

def is_gestor(user):
    """Verifica se o usuário é do grupo Gestor"""
    return user.groups.filter(name='Gestor').exists()

@login_required
@user_passes_test(is_gestor)
def listar_usuarios_pendentes(request):
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
    
    if request.method == 'POST':
        form = UsuarioPendenteForm(request.POST, instance=cadastro)
        if form.is_valid():
            try:
                usuario = form.save()
                
                # Se aprovado, cria usuário no sistema
                if usuario.is_approved:
                    from django.contrib.auth.models import User
                    User.objects.create_user(
                        username=usuario.username,
                        email=usuario.email,
                        password=usuario.senha
                    )
                    grupo = Group.objects.get(name=usuario.grupo)
                    user = User.objects.get(username=usuario.username)
                    user.groups.add(grupo)
                
                messages.success(request, 'Usuário atualizado com sucesso!')
                return redirect('listar_usuarios_pendentes')
            except Exception as e:
                messages.error(request, f'Erro ao salvar: {str(e)}')
    else:
        form = UsuarioPendenteForm(instance=cadastro)
    
    return render(request, 'editar_pendente.html', {'form': form})

@login_required
@user_passes_test(is_gestor)
def criar_usuario(request):
    if request.method == 'POST':
        print("hello1")
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