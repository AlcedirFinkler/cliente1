# views.py do app GestaoPrev
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Count, Q
from .models import ManutencaoPreventiva, PecasManutencao
from .forms import ManutencaoPreventivaForm
from CadEquip.models import Equipamento
from cadEstoque.models import Pecas
from django.contrib import messages
from datetime import datetime, date, timedelta
import calendar
import json
from gestaoOS.models import Chamado, Setor
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Min, Max
from datetime import timedelta

def get_month_calendar(year, month):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    return {
        'calendar': cal,
        'month_name': month_name,
        'year': year,
        'month': month
    }

@login_required
def editar_manutencao(request, id):
    manutencao = get_object_or_404(ManutencaoPreventiva, id=id)
    
    if request.method == 'POST':
        form = ManutencaoPreventivaForm(request.POST, request.FILES, instance=manutencao)
        pecas_quantidade_str = request.POST.get('pecas_quantidade', '')
        
        if form.is_valid():
            manutencao_editada = form.save()
            
            # Processar peças e suas quantidades
            # Primeiro, remover todas as relações existentes
            PecasManutencao.objects.filter(manutencao=manutencao).delete()
            
            # Criar novas relações com as quantidades atualizadas
            for item in pecas_quantidade_str.split(','):
                if item:
                    try:
                        peca_id, quantidade = item.split(':')
                        PecasManutencao.objects.create(
                            manutencao=manutencao,
                            peca_id=int(peca_id),
                            quantidade=int(quantidade)
                        )
                    except ValueError as e:
                        print(f"Erro ao processar item: {item}, erro: {e}")

            messages.success(request, 'Manutenção preventiva atualizada com sucesso!')
            return redirect('listar_manutencoes')
    else:
        form = ManutencaoPreventivaForm(instance=manutencao)
        
    # Buscar dados para o template
    equipamentos = Equipamento.objects.all()
    pecas_disponiveis = Pecas.objects.all()
    
    # Buscar peças já associadas com suas quantidades
    pecas_selecionadas = PecasManutencao.objects.filter(manutencao=manutencao).select_related('peca')
    pecas_detalhadas = [
        {'id': item.peca.id, 'descricao': item.peca.descricao, 'quantidade': item.quantidade}
        for item in pecas_selecionadas
    ]

    return render(request, 'editar_manutencao.html', {
        'form': form,
        'manutencao': manutencao,
        'equipamentos': equipamentos,
        'pecas_disponiveis': pecas_disponiveis,
        'pecas_selecionadas': pecas_detalhadas,
    })

@login_required
def excluir_manutencao(request, id):
    manutencao = get_object_or_404(ManutencaoPreventiva, id=id)

    if request.method == "POST":
        manutencao.delete()  # Exclui a manutenção
        return redirect('listar_manutencoes')

    return render(request, 'excluir_manutencao.html', {'manutencao': manutencao})

@login_required
def criar_manutencao(request):
    if request.method == 'POST':
        form = ManutencaoPreventivaForm(request.POST, request.FILES)
        pecas_quantidade_str = request.POST.get('pecas_quantidade', '')
        
        # Imprimir dados do formulário enviados pelo POST
        # print("Dados recebidos do formulário:")
        # print(request.POST)

        if form.is_valid():
            manutencao = form.save(commit=False)
            manutencao.status = 'programada'

            # Exibir informações do formulário após validação
            # print("Equipamento selecionado:", form.cleaned_data['equipamento'])
            # print("Peças selecionadas:", form.cleaned_data['pecas'])
            # print("Outros campos:")
            # print({
            #     'descricao': form.cleaned_data['descricao'],
            #     'tipo_calculo': form.cleaned_data['tipo_calculo'],
            #     'requer_parada': form.cleaned_data['requer_parada'],
            #     'data_ultima_manutencao': form.cleaned_data['data_ultima_manutencao'],
            #     'horimetro_atual': form.cleaned_data['horimetro_atual'],
            #     'periodo_meses': form.cleaned_data['periodo_meses'],
            #     'horas_intervalo': form.cleaned_data['horas_intervalo'],
            # })

            # Validações específicas baseadas no tipo de cálculo
            tipo_calculo = form.cleaned_data['tipo_calculo']
            if tipo_calculo in ['horas', 'ambos'] and not form.cleaned_data['horas_intervalo']:
                messages.error(request, 'Para cálculo por horas, o intervalo de horas é obrigatório.')
                # print('Para cálculo por horas, o intervalo de horas é obrigatório.')
                return render(request, 'criar_manutencao.html', {'form': form})

            if tipo_calculo in ['meses', 'ambos'] and not form.cleaned_data['periodo_meses']:
                messages.error(request, 'Para cálculo por meses, o período em meses é obrigatório.')
                # print('Para cálculo por meses, o período em meses é obrigatório.')
                return render(request, 'criar_manutencao.html', {'form': form})

            # Salvar a manutenção
            manutencao.save()
            
            # Processar peças e quantidades
            for item in pecas_quantidade_str.split(','):
                if item:
                    try:
                        peca_id, quantidade = item.split(':')
                        PecasManutencao.objects.create(
                            manutencao=manutencao,
                            peca_id=int(peca_id),
                            quantidade=int(quantidade)
                        )
                    except ValueError:
                        print(f"Erro ao processar item: {item}")

            # Exibir debug após salvar a manutenção
            # print("Manutenção salva com sucesso:")
            # print(manutencao)

            # Salvando as peças relacionadas
            if form.cleaned_data['pecas']:
                manutencao.pecas.set(form.cleaned_data['pecas'])
                # print("Peças relacionadas salvas:", form.cleaned_data['pecas'])

            messages.success(request, 'Manutenção preventiva criada com sucesso!')
            return redirect('listar_manutencoes')
        else:
            # Exibir erros do formulário
            print("Erros do formulário:", form.errors)
    else:
        form = ManutencaoPreventivaForm()

    # Busca os equipamentos e peças
    equipamentos = Equipamento.objects.all()
    query = request.GET.get('q')
    if query:
        equipamentos = equipamentos.filter(
            Q(nome__icontains=query) | Q(tag__icontains=query)
        )

    pecas = Pecas.objects.all()
    query = request.GET.get('q')
    if query:
        pecas = pecas.filter(
            Q(nome__icontains=query) | Q(tag__icontains=query)
        )

    return render(request, 'criar_manutencao.html', {
        'form': form,
        'equipamentos': equipamentos,
        'pecas': pecas,
    })

@login_required
def listar_manutencoes(request):
    # Atualiza o status de todas as manutenções
    ManutencaoPreventiva.atualizar_todos_status()
    
    # Query base com related fields
    manutencoes = ManutencaoPreventiva.objects.select_related('equipamento')
    
    # Obtém os parâmetros do filtro
    nome_equipamento = request.GET.get('nome_equipamento', '')
    tag_equipamento = request.GET.get('tag_equipamento', '')
    classe_equipamento = request.GET.get('classe_equipamento', '')
    status_manutencao = request.GET.get('status', '')
    setor = request.GET.get('setor', '')
    data_filter = request.GET.get('date')

    # Aplica os filtros
    if nome_equipamento:
        manutencoes = manutencoes.filter(equipamento__nome__icontains=nome_equipamento)
    
    if tag_equipamento:
        manutencoes = manutencoes.filter(equipamento__tag__icontains=tag_equipamento)
        
    if classe_equipamento:
        manutencoes = manutencoes.filter(equipamento__classe__icontains=classe_equipamento)
        
    if status_manutencao:
        manutencoes = manutencoes.filter(status=status_manutencao)
        
    if setor:
        try:
            setor_id = int(setor)
            manutencoes = manutencoes.filter(equipamento__setor_id=setor_id)
        except ValueError:
            pass
        
    if data_filter:
        try:
            filter_date = datetime.strptime(data_filter, '%Y-%m-%d').date()
            manutencoes = manutencoes.filter(data_proxima_manutencao=filter_date)
        except ValueError:
            pass

    # Ordena por data_proxima_manutencao
    manutencoes = manutencoes.order_by('data_proxima_manutencao')

    # Imprime os filtros aplicados
    # print("Filtros aplicados:")
    # print(f"Nome Equipamento: {nome_equipamento}")
    # print(f"Tag Equipamento: {tag_equipamento}")
    # print(f"Classe Equipamento: {classe_equipamento}")
    # print(f"Status: {status_manutencao}")
    # print(f"Setor: {setor}")
    # print(f"Data: {data_filter}")

    # Prepara dados para os filtros dropdown
    equipamentos = Equipamento.objects.all()
    classes_equipamento = equipamentos.values_list('classe', flat=True).distinct()
    #setores = equipamentos.values_list('setor', flat=True).distinct().order_by('setor')
    # Obtém setores com id e nome
    setores = equipamentos.values('setor', 'setor__nome').distinct().order_by('setor__nome')
    status_choices = dict(ManutencaoPreventiva._meta.get_field('status').choices)
    
    # Prepara calendários para os próximos 6 meses
    today = date.today()
    calendars = []
    maintenance_dates = {}

    for i in range(12):
        target_date = today + timedelta(days=i*31)
        year = target_date.year
        month = target_date.month
        
        month_maintenances = ManutencaoPreventiva.objects.filter(
            data_proxima_manutencao__year=year,
            data_proxima_manutencao__month=month
        ).values_list('data_proxima_manutencao', flat=True)
        
        maintenance_dates[f"{year}-{month}"] = [
            date.strftime('%Y-%m-%d') for date in month_maintenances
        ]
        
        calendars.append(get_month_calendar(year, month))

    # print(setores)

    context = {
        'manutencoes': manutencoes,
        'calendars': calendars,
        'maintenance_dates': json.dumps(maintenance_dates),
        'today': today,
        # Adiciona dados dos filtros ao contexto
        'equipamentos': equipamentos,
        'classes_equipamento': classes_equipamento,
        'setores': setores,
        'status_choices': status_choices,
        # Mantém os filtros selecionados para o form
        'filtros': {
            'nome_equipamento': nome_equipamento,
            'tag_equipamento': tag_equipamento,
            'classe_equipamento': classe_equipamento,
            'status': status_manutencao,
            'setor': setor,
        }
    }
    
    return render(request, 'listar_manutencoes.html', context)

@login_required
def gerar_os_preventiva(request, manutencao_id):
    manutencao = get_object_or_404(ManutencaoPreventiva, id=manutencao_id)

    # Get all technicians and their current workload
    tecnicos_workload = User.objects.filter(groups__name='Técnico').annotate(
        chamados_em_andamento=Count('tecnico_chamados', 
            filter=Q(tecnico_chamados__status='em_andamento'))
    ).order_by('username')

    # Debug print
    # print("\nDados dos técnicos sendo enviados ao template:")
    # for tecnico in tecnicos_workload:
        #print(f"ID: {tecnico.id}, Username: {tecnico.username}, "
              # f"Chamados em andamento: {tecnico.chamados_em_andamento}")
    
    if request.method == "POST":
        tecnico_id = request.POST.get('tecnico')
        if not tecnico_id:
            messages.error(request, 'Por favor, selecione um técnico.')
            return redirect('gerar_os_preventiva', manutencao_id=manutencao_id)

        try:
            tecnico = User.objects.get(id=tecnico_id)
            # Criar o chamado com os dados da manutenção preventiva
            chamado = Chamado.objects.create(
                usuario=request.user,
                titulo=f"Manutenção Preventiva: {manutencao.equipamento.nome}",
                descricao=manutencao.descricao,
                status='em_andamento',
                setor=manutencao.equipamento.setor,
                equipamento=manutencao.equipamento,
                tipo_manutencao='preventiva',
                data_inicio_atendimento=timezone.now(),
                tecnico=tecnico
                )
            
            # Atualizar o status da manutenção preventiva
            manutencao.status = 'em_execucao'
            manutencao.save()
            
            messages.success(request, 'Ordem de serviço gerada com sucesso!')
            return redirect('listar_manutencoes')
            
        except Exception as e:
            messages.error(request, f'Erro ao gerar ordem de serviço: {str(e)}')
            return redirect('gerar_os_preventiva', manutencao_id=manutencao_id)
    
    context = {
        'manutencao': manutencao,
        'tecnicos': tecnicos_workload,
    }
    return render(request, 'gerar_os_preventiva.html', context)

@login_required
def gantt_manutencoes(request):
    # Atualiza os status das manutenções
    ManutencaoPreventiva.atualizar_todos_status()
    
    # Obtém todas as manutenções com relacionamentos
    manutencoes = ManutencaoPreventiva.objects.select_related(
        'equipamento__setor'
    ).order_by('equipamento__setor__nome', 'equipamento__nome')
    
    # Calcula o período total do timeline
    min_date = manutencoes.aggregate(Min('data_proxima_manutencao'))['data_proxima_manutencao__min']
    max_date = manutencoes.aggregate(Max('data_proxima_manutencao'))['data_proxima_manutencao__max']
    
    if not min_date or not max_date:
        return render(request, 'gantt_manutencoes.html', {
            'error': 'Nenhuma manutenção programada encontrada'
        })
    
    # Calcula o total de dias para posicionamento
    total_days = (max_date - min_date).days + 1  # +1 para incluir o último dia
    
    # Gera as semanas do timeline
    timeline = []
    current_date = min_date
    while current_date <= max_date:
        timeline.append({
            'week_start': current_date,
            'week_number': current_date.isocalendar()[1],
            'month': current_date.strftime('%b/%y')
        })
        current_date += timedelta(days=7)
    
    # Constrói a estrutura hierárquica
    estrutura = {}
    for manutencao in manutencoes:
        setor_nome = manutencao.equipamento.setor.nome if manutencao.equipamento.setor else 'Sem Setor'
        equipamento_nome = manutencao.equipamento.nome
        
        if setor_nome not in estrutura:
            estrutura[setor_nome] = {
                'equipamentos': {},
                'collapsed': False
            }
        
        if equipamento_nome not in estrutura[setor_nome]['equipamentos']:
            estrutura[setor_nome]['equipamentos'][equipamento_nome] = []
        
        estrutura[setor_nome]['equipamentos'][equipamento_nome].append(manutencao)
    
    context = {
        'estrutura': estrutura,
        'timeline': timeline,
        'min_date': min_date,
        'max_date': max_date,
        'total_days': total_days,
        'status_colors': {
            'programada': '#4CAF50',
            'atrasada': '#F44336',
            'em_execucao': '#2196F3'
        },
        'today': datetime.now().date()
    }
    
    return render(request, 'gantt_manutencoes.html', context)