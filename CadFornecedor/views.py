from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import FornecedorForm
from .models import Fornecedor
from django.contrib import messages

@login_required
def CadFornecedor(request):
    fornecedores = Fornecedor.objects.all()
    
    # Filtro por nome do fornecedor
    nome = request.GET.get('fornecedor')
    if nome:
        fornecedores = fornecedores.filter(fornecedor__icontains=nome)
    
    # Filtro por email
    email = request.GET.get('email')
    if email:
        fornecedores = fornecedores.filter(fornecedor_email__icontains=email)
        
    # Filtro por telefone
    telefone = request.GET.get('telefone')
    if telefone:
        fornecedores = fornecedores.filter(fornecedor_fone__icontains=telefone)
    
    return render(request, 'CadFornecedor.html', {
        'fornecedores': fornecedores
    })

@login_required
def cria_fornecedor(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            fornecedor = form.save(commit=False)
            fornecedor.save()
            return redirect('CadFornecedor')
    else:
        # print('Faltando dados:')
        form = FornecedorForm()

    return render(request, 'cria_fornecedor.html', {'form': form})


@login_required  # Add login requirement for security
def excluir_fornecedor(request, id):
    fornecedor = get_object_or_404(Fornecedor, id=id)
    
    if request.method == 'POST':
        fornecedor.delete()
        return redirect('CadFornecedor')
    
    # Create a separate template for deletion confirmation
    return render(request, 'confirmar_exclusao.html', {
        'fornecedor': fornecedor
    })

@login_required
def editar_fornecedor(request, id):
    fornecedor = get_object_or_404(Fornecedor, id=id)

    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            return redirect('CadFornecedor')
    else:
        form = FornecedorForm(instance=fornecedor)

    return render(request, 'editar_fornecedor.html', {'form': form})