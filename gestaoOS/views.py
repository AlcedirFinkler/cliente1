# views.py do app gestaoOS
from django.shortcuts import render, redirect, get_object_or_404
from itertools import count
from django.db.models import Count, Q
from django.contrib import messages
from django.db import models
from CadEquip.models import Equipamento

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Setor
from .models import Chamado, Acao, AcaoPeca, AcaoColaborador
from gestaoUsuarios.models import CadastroPendente

from cadEstoque.models import Pecas

from CadEquip.models import Equipamento

from .forms import ChamadoForm, AcaoForm, FinalizarChamadoForm, FinalizarChamadoGestorForm

@login_required
def tela_inicial(request):
    if request.user.groups.filter(name="Gestor").exists():
        chamados = Chamado.objects.select_related('usuario', 'setor', 'tecnico')
        
        # Filtro por Status
        status = request.GET.get('status', 'pendente')
        if status:
            chamados = chamados.filter(status=status)

        # Filtro por Técnico
        tecnico_id = request.GET.get('tecnico')
        if tecnico_id:
            chamados = chamados.filter(tecnico__id=tecnico_id)

        # Filtro por Setor
        setor_id = request.GET.get('setor')
        if setor_id:
            chamados = chamados.filter(setor__id=setor_id)

        # Filtro por Usuário (nome parcial, case insensitive)
        usuario = request.GET.get('usuario', '').strip()
        if usuario:
            chamados = chamados.filter(usuario__username__icontains=usuario)

        # Filtro por Título/Descrição
        titulo_descricao = request.GET.get('titulo_descricao', '').strip()
        if titulo_descricao:
            chamados = chamados.filter(
                models.Q(titulo__icontains=titulo_descricao) |
                models.Q(descricao__icontains=titulo_descricao)
            )
        
        # Filtro por Equipamento
        equipamento = request.GET.get('equipamento', '').strip()
        if equipamento:
            chamados = chamados.filter(equipamento__nome__icontains=equipamento)
 
        # Filtro por Data
        data = request.GET.get('data', '')
        if data == "mais_antigo":
            chamados = chamados.order_by('data_criacao')
        else:
            chamados = chamados.order_by('-data_criacao')

        # Passar técnicos e setores para popular os dropdowns
        tecnicos = User.objects.filter(groups__name="Técnico")
        setores = Setor.objects.all()

                 # Add foto_url to each chamado
        for chamado in chamados:
            chamado.foto_url = chamado.foto.url if chamado.foto else None

        return render(request, 'tela_gestor.html', {
            'chamados_por_solicitante': chamados,
            'tecnicos': tecnicos,
            'setores': setores,
        })
    
    elif request.user.groups.filter(name="Solicitante").exists():
        # Usuários normais veem apenas seus próprios chamados
        ordenar = request.GET.get('ordenar')
        chamados = Chamado.objects.filter(usuario=request.user).prefetch_related('acoes')
        
        if ordenar == "mais_recente":
            chamados = chamados.order_by('-data_criacao')
        elif ordenar == "mais_antigo":
            chamados = chamados.order_by('data_criacao')
        elif ordenar == "pendente":
            chamados = chamados.filter(status='pendente')
        elif ordenar == "em_andamento":
            chamados = chamados.filter(status='em_andamento')
        elif ordenar == "finalizado":
            chamados = chamados.filter(status='finalizado')
        elif ordenar == "concluido":
            chamados = chamados.filter(status='concluido')

        # Organiza as ações associadas a cada chamado
        chamados_com_acoes = []
        for chamado in chamados:
            acoes = chamado.acoes.all()
            chamados_com_acoes.append({'chamado': chamado, 'acoes': acoes})

        return render(request, 'tela_solicitante.html', {'chamados_com_acoes': chamados_com_acoes})
    
    elif request.user.groups.filter(name="Técnico").exists():
        # Defina valores padrão para tipo e ordenar
        tipo = request.GET.get('tipo', 'recebidos')  # Padrão é "recebidos"
    
        # Define ordenar com base no tipo, garantindo que sempre tenha um valor
        if tipo == 'realizados':
            ordenar = request.GET.get('ordenar', 'mais_recente')  # Se tipo é "realizados", padrão é "mais_recente"
        else:
            ordenar = request.GET.get('ordenar', 'em_andamento')  # Padrão é "em_andamento" para outros tipos

        if tipo == 'realizados':
            chamados = Chamado.objects.filter(usuario=request.user).select_related('setor', 'tecnico')
        elif tipo == 'recebidos':
            chamados = Chamado.objects.filter(tecnico=request.user).select_related('usuario', 'setor')
        else:
            chamados = Chamado.objects.none()  # Caso tipo tenha um valor inválido

        # Aplicar a ordenação com base no valor de 'ordenar'
        if ordenar == "mais_recente":
            chamados = chamados.order_by('-data_criacao')
        elif ordenar == "mais_antigo":
            chamados = chamados.order_by('data_criacao')
        elif ordenar == "pendente":
            chamados = chamados.filter(status='pendente')
        elif ordenar == "em_andamento":
            chamados = chamados.filter(status='em_andamento')
        elif ordenar == "finalizado":
            chamados = chamados.filter(status='finalizado')
        elif ordenar == "concluido":
            chamados = chamados.filter(status='concluido')
        else:  # Caso ordenar tenha um valor inválido ou não especificado
            chamados = chamados.filter(status='em_andamento') if tipo == 'recebidos' else chamados.order_by('-data_criacao')

        return render(request, 'tela_tecnico.html', {'chamados': chamados, 'tipo': tipo, 'ordenar': ordenar})

@login_required
def criar_chamado(request):


    if request.method == 'POST':
        form = ChamadoForm(request.POST, request.FILES, user=request.user)  # Passa o usuário para o formulário
        if form.is_valid():
            chamado = form.save(commit=False)  # Cria o objeto sem salvar no banco ainda
            chamado.usuario = request.user   # Define o usuário logado como dono do chamado
            chamado.save()                   # Salva o objeto no banco de dados
            # print('Chamado salvo com sucesso!')
            # messages.success(request, "Chamado cadastrado com sucesso!")
            return redirect('tela_inicial')
        else:
            # print('faltando dados no chamado!')
            messages.error(request, "Faltando dados!")
    else:
        form = ChamadoForm(user=request.user)

    # Busca os equipamentos
    equipamentos = Equipamento.objects.all()
    query = request.GET.get('q')
    if query:
        equipamentos = equipamentos.filter(
            Q(nome__icontains=query) | Q(tag__icontains=query)
        )
    

    return render(request, 'criar_chamado.html', {'form': form, 'equipamentos': equipamentos})

@login_required
def excluir_chamado(request, id):
    chamado = get_object_or_404(Chamado, id=id)
    chamado.delete()
    return redirect('tela_inicial')  # Redirecione para o tela_inicial após a exclusão

@login_required
def gerenciar_acoes(request, chamado_id):
    


    if request.user.groups.filter(name="Técnico").exists():
        chamado = get_object_or_404(Chamado, id=chamado_id)
        acoes = Acao.objects.filter(chamado=chamado).prefetch_related('acoes_pecas__peca', 'acoes_colaboradores__colaborador')
        pecas = Pecas.objects.all()

        for acao in acoes:
            pecas_detalhes = [
                {"descricao": acao_peca.peca.descricao, "quantidade": acao_peca.quantidade}
                for acao_peca in acao.acoes_pecas.all()
            ]

        # Construir um dicionário com ações e suas respectivas peças
        acoes_com_pecas = []
        for acao in acoes:   
            # Coletar peças e suas quantidades
            pecas_detalhes = []
            for acao_peca in acao.acoes_pecas.all():
                peca_info = {
                    "descricao": acao_peca.peca.descricao,
                    "quantidade": acao_peca.quantidade
                }
                pecas_detalhes.append(peca_info)
            
            acoes_com_pecas.append({
                "acao": acao,
                "pecas": pecas_detalhes
            })

        # Define acoes_com_detalhes for both GET and POST methods
        acoes_com_detalhes = []
        for acao in acoes:
            colaboradores_detalhes = [
                {
                    "nome": ac.colaborador.get_full_name() or ac.colaborador.username,
                    "horas": ac.horas_trabalhadas,
                    "atividade": ac.descricao_atividade
                }
                for ac in acao.acoes_colaboradores.all()
            ]

            acoes_com_detalhes.append({
                "acao": acao,
                "pecas": [
                    {"descricao": ap.peca.descricao, "quantidade": ap.quantidade}
                    for ap in acao.acoes_pecas.all()
                ],
                "colaboradores": colaboradores_detalhes
            })

        # Fetch approved technicians
        approved_technicians = User.objects.filter(
        groups__name='Técnico'
        ).filter(
            username__in=CadastroPendente.objects.filter(
                is_approved=True, 
                grupo='Técnico'
            ).values_list('username', flat=True)
        ).distinct()


        if request.method == 'POST':
            form = AcaoForm(request.POST, request.FILES)

            if form.is_valid():
                acao = form.save(commit=False)
                acao.chamado = chamado
                acao.save()

                # Process collaborators
                colaborador_ids = [col_id.strip() for col_id in request.POST.get('colaboradores[]', '').split(',') if col_id.strip().isdigit()]
                horas = request.POST.get('horas[]', '').split(',')
                atividades = request.POST.get('atividades[]', '').split('|||')

                if len(colaborador_ids) == len(horas) == len(atividades):
                    for col_id, horas_trab, atividade in zip(colaborador_ids, horas, atividades):
                        try:
                            if col_id and horas_trab and atividade:
                                colaborador = User.objects.get(id=col_id)
                                AcaoColaborador.objects.create(
                                    acao=acao,
                                    colaborador=colaborador,
                                    horas_trabalhadas=float(horas_trab),
                                    descricao_atividade=atividade
                                )
                                # print(f"Colaborador {colaborador} adicionado com sucesso.")
                        except (User.DoesNotExist, ValueError) as e:
                            # print(f"Erro ao processar colaborador ID {col_id}: {e}")
                            messages.error(request, f"Erro ao processar colaborador: {e}")
                # else:
                    # print("Erro na correspondência dos dados dos colaboradores. Verifique os IDs, horas e atividades.")
                            
                # Processar peças utilizadas
                pecas_ids = request.POST.getlist('peca[]')[0].split(',') if request.POST.getlist('peca[]') else []
                quantidades = request.POST.getlist('quantidade[]')[0].split(',') if request.POST.getlist('quantidade[]') else []

                if pecas_ids and quantidades and len(pecas_ids) == len(quantidades):
                    for peca_id, quantidade in zip(pecas_ids, quantidades):
                        try:
                            if peca_id and quantidade:  # Verifica se ambos têm valores
                                peca = Pecas.objects.get(id=peca_id)
                                quantidade = int(quantidade)
                                if quantidade > 0:
                                    AcaoPeca.objects.create(
                                        acao=acao,
                                        peca=peca,
                                        quantidade=quantidade
                                    )
                        except (Pecas.DoesNotExist, ValueError) as e:
                            messages.error(request, f"Erro ao processar peça: {str(e)}")
                            continue

                messages.success(request, 'Ação registrada com sucesso!')
                return redirect('gerenciar_acoes', chamado_id=chamado.id)
        else:
            form = AcaoForm()
            # print("Formulário inválido")

        context = {
            'form': form,
            'acoes': acoes,
            'chamado': chamado,
            'acoes_com_pecas': acoes_com_pecas,
            'acoes_com_detalhes': acoes_com_detalhes,
            'pecas': pecas,
            'approved_technicians': approved_technicians,
        }

        return render(request, 'gerenciar_acoes.html', context)
    
    if request.user.groups.filter(name="Gestor").exists():
        chamado = get_object_or_404(Chamado, id=chamado_id)
        acoes = Acao.objects.filter(chamado=chamado).prefetch_related('acoes_pecas__peca', 'acoes_colaboradores__colaborador')
        pecas = Pecas.objects.all()

        for acao in acoes:
            pecas_detalhes = [
                {"descricao": acao_peca.peca.descricao, "quantidade": acao_peca.quantidade}
                for acao_peca in acao.acoes_pecas.all()
            ]

        # Construir um dicionário com ações e suas respectivas peças
        acoes_com_pecas = []
        for acao in acoes:   
            # Coletar peças e suas quantidades
            pecas_detalhes = []
            for acao_peca in acao.acoes_pecas.all():
                peca_info = {
                    "descricao": acao_peca.peca.descricao,
                    "quantidade": acao_peca.quantidade
                }
                pecas_detalhes.append(peca_info)
            
            acoes_com_pecas.append({
                "acao": acao,
                "pecas": pecas_detalhes
            })

        # Define acoes_com_detalhes for both GET and POST methods
        acoes_com_detalhes = []
        for acao in acoes:
            colaboradores_detalhes = [
                {
                    "nome": ac.colaborador.get_full_name() or ac.colaborador.username,
                    "horas": ac.horas_trabalhadas,
                    "atividade": ac.descricao_atividade
                }
                for ac in acao.acoes_colaboradores.all()
            ]

            acoes_com_detalhes.append({
                "acao": acao,
                "pecas": [
                    {"descricao": ap.peca.descricao, "quantidade": ap.quantidade}
                    for ap in acao.acoes_pecas.all()
                ],
                "colaboradores": colaboradores_detalhes
            })

        # Get all approved technicians and their current workload
        approved_technicians = User.objects.filter(
            groups__name='Técnico',
            username__in=CadastroPendente.objects.filter(is_approved=True, grupo='Técnico').values_list('username', flat=True)
        ).distinct()

        tecnicos_workload = approved_technicians.annotate(
            chamados_em_andamento=Count('tecnico_chamados', 
                filter=Q(tecnico_chamados__status='em_andamento'))
        ).order_by('username')

        # Print the technicians' workload information
        
        # print("Informação dos Técnicos Aprovados:")
        # for tecnico in tecnicos_workload:
            # print(f"Técnico: {tecnico.username}, Chamados em Andamento: {tecnico.chamados_em_andamento}")



        chamado = get_object_or_404(Chamado, id=chamado_id)
        if request.method == 'POST':
            form = FinalizarChamadoGestorForm(request.POST, instance=chamado, user=request.user)

            if form.is_valid():
                chamado = form.save()
                return redirect('tela_inicial')  # or redirect to wherever you want after edit
        else:
            form = FinalizarChamadoGestorForm(request.POST, instance=chamado, user=request.user)
            # print("Formulário inválido")

        context = {
            'form': form,
            'acoes': acoes,
            'chamado': chamado,
            'acoes_com_pecas': acoes_com_pecas,
            'acoes_com_detalhes': acoes_com_detalhes,
            'pecas': pecas,
            'tecnicos': tecnicos_workload,
        }

        return render(request, 'gerenciar_acoes_gestor.html', context)

@login_required
def finalizar_chamado(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)
    if request.method == 'POST':
        form = FinalizarChamadoForm(request.POST, instance=chamado, user=request.user)
        if form.is_valid():
            form.instance.status = 'finalizado'                    
            chamado = form.save()
            return redirect('tela_inicial')  # or redirect to wherever you want after edit
    else:
        form = FinalizarChamadoForm(instance=chamado, user=request.user)
    return render(request, 'finalizar_chamado.html', {'form': form, 'chamado': chamado})

@login_required
def historico_equipamento(request, equipamento_id):
    equipamento = get_object_or_404(Equipamento, id=equipamento_id)
    # Pegamos também o chamado_id da URL para usar no botão voltar
    chamado_id = request.GET.get('chamado_id')
    chamados = Chamado.objects.filter(equipamento=equipamento).order_by('-data_criacao')
    
    return render(request, 'historico_equipamento.html', {
        'equipamento': equipamento,
        'chamados': chamados,
        'chamado_id': chamado_id  # Passamos o chamado_id para o template
    })