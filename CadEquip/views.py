from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import EquipamentoForm  
from gestaoOS.models import Setor
from .models import Equipamento
from CadFornecedor.models import Fornecedor
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q

@login_required
def teste(request):
    return render(request, 'teste.html')


@login_required
def cria_equipamento(request):
    if request.method == "POST":
        form = EquipamentoForm(request.POST, request.FILES)
        fornecedor_id = request.POST.get('fornecedor')
        # print("Request POST:", request.POST)  # Debug do formulário enviado
        # print("Fornecedor ID recebido:", fornecedor_id)  # Debug do fornecedor


        
        if form.is_valid():
            # Verifica se a tag já existe
            tag = form.cleaned_data.get('tag')
            if Equipamento.objects.filter(tag=tag).exists():
                form.add_error('tag', 'Essa tag já está cadastrada.')

            equipamento = form.save(commit=False)
            
            # Verifica fornecedor
            if fornecedor_id:
                try:
                    equipamento.fornecedor = Fornecedor.objects.get(id=fornecedor_id)
                except Fornecedor.DoesNotExist:
                    form.add_error('fornecedor', 'Fornecedor selecionado não existe.')
 
            # Explicitly set patrimonio to None if it's an empty string
            if not equipamento.patrimonio or equipamento.patrimonio.strip() == '':
                equipamento.patrimonio = None

            # Recuperando os valores dos campos necessários
            ssma = form.cleaned_data.get('ssma')
            qualidade = form.cleaned_data.get('qualidade')
            operacao = form.cleaned_data.get('operacao')
            entrega = form.cleaned_data.get('entrega')
            mtbf = form.cleaned_data.get('mtbf')
            mttr = form.cleaned_data.get('mttr')

            # Utilizando a função para definir a classe
            equipamento.classe = definir_classe(ssma, qualidade, operacao, entrega, mtbf, mttr)


            # Se não houver erros, salva o equipamento
            if not form.errors:
                fornecedor_id = request.POST.get('fornecedor')
                # print("Fornecedor ID antes de salvar:", fornecedor_id)
                if fornecedor_id:
                    equipamento.fornecedor_id = fornecedor_id
                equipamento.save()
                # print("Equipamento:", equipamento)
                # print("Fornecedor:", equipamento.fornecedor)
                # print('Equipamento salvo com sucesso!')
                return redirect('CadEquip')
            else:
                messages.error(request, 'Erro ao cadastrar equipamento. Corrija os campos destacados.')

        else:
            messages.error(request, 'Erro ao processar o formulário. Verifique os dados informados.')
            # print("Erros do formulário:", form.errors)  # Debug para desenvolvimento

    else:
        form = EquipamentoForm()

    todos_fornecedores = Fornecedor.objects.all()
    return render(request, 'cria_equipamento.html', {'form': form, 'fornecedores': todos_fornecedores})

@login_required
def cadastrar_equipamento(request):
    fornecedores = Fornecedor.objects.all()  # Obtém todos os fornecedores cadastrados
    return render(request, 'cadastro_equipamento.html', {'fornecedores': fornecedores})

@login_required
def listar_equipamentos(request):
    equipamentos = Equipamento.objects.all()
    
    # Filtro por TAG
    tag = request.GET.get('tag')
    if tag:
        equipamentos = equipamentos.filter(tag__icontains=tag)
    
    # Filtro por Setor
    setor_id = request.GET.get('setor')
    if setor_id:
        equipamentos = equipamentos.filter(setor_id=setor_id)
    
    # Filtro por Nome
    nome = request.GET.get('nome')
    if nome:
        equipamentos = equipamentos.filter(nome__icontains=nome)
    
    # Filtro por Descrição
    descricao = request.GET.get('descricao')
    if descricao:
        equipamentos = equipamentos.filter(descricao__icontains=descricao)
    
    # Filtro por Fabricante
    fabricante = request.GET.get('fabricante')
    if fabricante:
        equipamentos = equipamentos.filter(fabricante__icontains=fabricante)
    
    # Filtro por Classe
    classe = request.GET.get('classe')
    if classe:
        equipamentos = equipamentos.filter(classe__icontains=classe)
    
    setores = Setor.objects.all()
    
    return render(request, 'CadEquipHome.html', {
        'equipamentos': equipamentos,
        'setores': setores
    })

@login_required
def editar_equipamento(request, id):
    # print('Acessou a tela de edição de equipamento!')
    equipamento = get_object_or_404(Equipamento, id=id)
    fornecedor_selecionado = equipamento.fornecedor  # Obtem o fornecedor diretamente, se existir
    # Adicionando prints para debug
    # print("\n=== DEBUG INFORMAÇÕES DO EQUIPAMENTO E FORNECEDORES ===")
    # print(f"Equipamento ID: {equipamento.id}")
    # print(f"Fornecedor selecionado: {fornecedor_selecionado}")
    # if fornecedor_selecionado:
        # print(f"Detalhes do fornecedor selecionado:")
        # print(f"- ID: {fornecedor_selecionado.id}")
        # print(f"- Nome: {fornecedor_selecionado.fornecedor}")
        # print(f"- Email: {fornecedor_selecionado.fornecedor_email}")
        # print(f"- Telefone: {fornecedor_selecionado.fornecedor_fone}")

    if request.method == 'POST':
        form = EquipamentoForm(request.POST, request.FILES, instance=equipamento)
        fornecedor_id = request.POST.get('fornecedor')

        if form.is_valid():
            equipamento = form.save(commit=False)
            if fornecedor_id:
                try:
                    fornecedor = Fornecedor.objects.get(id=fornecedor_id)
                    equipamento.fornecedor = fornecedor
                except Fornecedor.DoesNotExist:
                    form.add_error('fornecedor', 'Fornecedor selecionado não existe.')

            # Recuperando os valores dos campos necessários
            ssma = form.cleaned_data.get('ssma')
            qualidade = form.cleaned_data.get('qualidade')
            operacao = form.cleaned_data.get('operacao')
            entrega = form.cleaned_data.get('entrega')
            mtbf = form.cleaned_data.get('mtbf')
            mttr = form.cleaned_data.get('mttr')

            # Utilizando a função para definir a classe
            equipamento.classe = definir_classe(ssma, qualidade, operacao, entrega, mtbf, mttr)

            equipamento.save()
            messages.success(request, 'Equipamento editado com sucesso!')
            return redirect('CadEquip')
    else:
        form = EquipamentoForm(instance=equipamento)

    todos_fornecedores = Fornecedor.objects.all()

     # Print para debug dos fornecedores
    # print("\n=== DEBUG LISTA DE FORNECEDORES ===")
    # print(f"Quantidade total de fornecedores: {todos_fornecedores.count()}")
    # for fornecedor in todos_fornecedores:
        # print(f"Fornecedor ID: {fornecedor.id}, Nome: {fornecedor.fornecedor}")

    # Print do contexto final
    # print("\n=== DEBUG CONTEXTO DO TEMPLATE ===")
    # print(f"Form válido: {form.is_valid() if request.method == 'POST' else 'GET request'}")
    # print(f"Quantidade de fornecedores no contexto: {len(todos_fornecedores)}")
    # print(f"Fornecedor selecionado no contexto: {fornecedor_selecionado}")
    # print("==========================================\n")
    
    return render(request, 'editar_equipamento.html', {
        'form': form,
        'equipamento': equipamento,
        'fornecedores': todos_fornecedores,
        'fornecedor_selecionado': fornecedor_selecionado,  # Passa o fornecedor selecionado completo
    })

@login_required
def excluir_equipamento(request, id):
    # Obtém o equipamento pelo ID
    equipamento = get_object_or_404(Equipamento, id=id)

    # Verifica se o método é POST para confirmar a exclusão
    if request.method == 'POST':
        equipamento.delete()  # Exclui o equipamento
        return redirect('CadEquip')  # Redireciona para a lista de equipamentos após a exclusão

    # Se não for um POST, exibe uma página de confirmação
    return render(request, 'confirmar_exclusao.html', {'equipamento': equipamento})


# Função auxiliar para definir a classe do equipamento
def definir_classe(ssma, qualidade, operacao, entrega, mtbf, mttr):
    if ssma == 'a' or qualidade == 'a':
        return 'A'
    elif ssma in ['b', 'c'] and qualidade in ['b', 'c'] and operacao in ['a', 'b'] and entrega == 'a' and mtbf == 'a' and mttr == 'a':
        return 'A'
    elif ssma in ['b', 'c'] and qualidade in ['b', 'c'] and operacao in ['a', 'b'] and entrega == 'b' and mtbf in ['a', 'b'] and mttr in ['a', 'b']:
        return 'B'
    elif ssma in ['b', 'c'] and qualidade in ['b', 'c'] and operacao in ['a', 'b'] and entrega == 'a' and mtbf == 'b' and mttr in ['a', 'b']:
        return 'B'
    elif ssma in ['b', 'c'] and qualidade in ['b', 'c'] and operacao in ['a', 'b'] and entrega == 'a' and mtbf == 'a' and mttr == 'b':
        return 'B'
    elif ssma in ['b', 'c'] and qualidade in ['b', 'c'] and operacao == 'c' and entrega in ['a', 'b'] and mtbf in ['a', 'b'] and mttr in ['a', 'b']:
        return 'B'
    else:
        return 'C'

@login_required
def busca_fornecedores(request):
    nome_parcial = request.GET.get('nome', '')
    fornecedores = Fornecedor.objects.filter(
        nome__icontains=nome_parcial
    )
    
    # Converte os fornecedores para uma lista de dicionários
    resultados = [
        {
            'id': fornecedor.id, 
            'nome': fornecedor.nome
        } for fornecedor in fornecedores
    ]
    
    return JsonResponse({'fornecedores': resultados})