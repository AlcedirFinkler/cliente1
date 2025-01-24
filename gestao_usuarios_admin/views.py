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
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')

    pendentes = CadastroPendente.objects.all()
    
    if query:
        pendentes = pendentes.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query)
        )
    
    if status == 'aprovados':
        pendentes = pendentes.filter(is_approved=True)
    elif status == 'nao_aprovados':
        pendentes = pendentes.filter(is_approved=False)

    return render(request, 'listar_pendentes.html', {
        'pendentes': pendentes,
        'query': query,
        'status': status
    })

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