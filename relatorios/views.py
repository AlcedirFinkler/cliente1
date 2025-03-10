# reports/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, PageTemplate, BaseDocTemplate, Frame,  Spacer


from django.db.models import F, Q, Sum, Count
from django.db.models.functions import TruncMonth

from django.utils import timezone
from datetime import datetime, timedelta, date
from django.contrib.auth.models import User
from gestaoOS.models import Setor
from django import template

from CadEquip.models import Equipamento, HistoricoHorasMensais
from cadEstoque.models import Pecas, Fornecedor
from gestaoOS.models import Chamado, Acao, AcaoColaborador
from GestaoPrev.models import ManutencaoPreventiva, PecasManutencao
from gestaoUsuarios.models import CadastroPendente
from django.contrib.auth.decorators import login_required

import os

# Inseridos para gerar arquivo PDF
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import Image, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.units import cm
from reportlab.platypus import PageTemplate, BaseDocTemplate, NextPageTemplate
from reportlab.platypus.frames import Frame

# Inseridos para gerar arquivo excell
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

# Inseridos para geração de gráficos
import json
from collections import defaultdict
from django.db.models import Avg
from decimal import Decimal



# Configuração da margem direita
margem_direita = 36  # Margem direita configurada em pontos (1,27 cm)
margem_esquerda = 36
largura_total_pagina = A4[0]  # Largura total da página em pontos (A4)
posicao_x_direita = largura_total_pagina - margem_direita  # Posição final da margem direita
largura_disponivel = largura_total_pagina - margem_direita - margem_esquerda

@login_required
def relatorios_index(request):
    return render(request, 'relatorios/base_rel.html')

def gerar_excel_indicadores(indicadores):
    """
    Gera um arquivo Excel com os indicadores de manutenção
    """
    # Cria um novo workbook e seleciona a primeira planilha
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Indicadores de Manutenção"

    # Define estilos
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="007BFF", end_color="007BFF", fill_type="solid")
    border = Border(
        left=Side(style='thin'), 
        right=Side(style='thin'), 
        top=Side(style='thin'), 
        bottom=Side(style='thin')
    )

    # Cabeçalho
    headers = [
        "TAG", "Equipamento", "Classe", "Setor", 
        "Mês", "Ano", "Tempo Operação (h)", 
        "Chamados Corretivos", "Horas Paradas", 
        "MTBF (h)", "MTTR (h)", "Disponibilidade (%)"
    ]

    # Adiciona cabeçalho
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = Alignment(horizontal='center', vertical='center')

    # Adiciona dados
    for row, indicador in enumerate(indicadores, start=2):
        ws.cell(row=row, column=1, value=indicador['equipamento'].tag or '-')
        ws.cell(row=row, column=2, value=indicador['equipamento'].nome)
        ws.cell(row=row, column=3, value=indicador['equipamento'].classe or '-')
        ws.cell(row=row, column=4, value=str(indicador['equipamento'].setor))
        ws.cell(row=row, column=5, value=indicador['mes'])
        ws.cell(row=row, column=6, value=indicador['ano'])
        ws.cell(row=row, column=7, value=indicador['tempo_operacao'])
        ws.cell(row=row, column=8, value=indicador['chamados_corretivos'])
        ws.cell(row=row, column=9, value=indicador['horas_paradas'])
        ws.cell(row=row, column=10, value=indicador['mtbf'])
        ws.cell(row=row, column=11, value=indicador['mttr'])
        ws.cell(row=row, column=12, value=indicador['disponibilidade'])

    # Ajusta largura das colunas
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    return wb

def gerar_excel_relatorio_pecas(pecas_necessarias):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Relatório de Peças"

    headers = [
        "Peça",
        "Fornecedor",
        "Quantidade Necessária",
        "Quantidade em Estoque",
        "Estoque Mínimo",
        "Preço Unitário",
        "Data Primeira Demanda",
        "Quantidade Compra Recomendada",
        "Valor Total"
    ]
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="007BFF", end_color="007BFF", fill_type="solid")
    border = Border(
        left=Side(style='thin'), 
        right=Side(style='thin'), 
        top=Side(style='thin'), 
        bottom=Side(style='thin')
    )
    alignment = Alignment(horizontal='center', vertical='center')

    for col_index, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_index, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = alignment

    # Preenche os dados das peças
    row_number = 2
    for peca, dados in pecas_necessarias.items():
        ws.cell(row=row_number, column=1, value=peca.descricao)
        fornecedor = dados.get("fornecedor")
        ws.cell(
            row=row_number, 
            column=2, 
            value=str(fornecedor) if fornecedor else "Não especificado"
        )
        ws.cell(row=row_number, column=3, value=dados.get("quantidade_necessaria"))
        ws.cell(row=row_number, column=4, value=dados.get("quantidade_estoque"))
        ws.cell(row=row_number, column=5, value=dados.get("estoque_minimo"))
        ws.cell(row=row_number, column=6, value=dados.get("preco_unitario"))
        data_primeira_demanda = dados.get("data_primeira_demanda")
        ws.cell(
            row=row_number, 
            column=7, 
            value=str(data_primeira_demanda) if data_primeira_demanda else "N/A"
        )
        ws.cell(row=row_number, column=8, value=dados.get("quantidade_compra_recomendada"))
        ws.cell(row=row_number, column=9, value=dados.get("valor_total"))
        row_number += 1

    # Ajusta a largura das colunas com base no conteúdo
    for col in ws.columns:
        max_length = 0
        column_letter = col[0].column_letter
        for cell in col:
            try:
                if cell.value and len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column_letter].width = adjusted_width

    return wb

@login_required
def gerar_relatorio_pecas(request):
    prazo_dias = int(request.GET.get('prazo', 30))  # Padrão configurado para 30 dias
    
    if prazo_dias > 0:
        data_futura = date.today() + timedelta(days=prazo_dias)
    else:
        data_futura = None

    pecas_necessarias = {}

    # Manutenções futuras
    if data_futura:
        manutencoes = ManutencaoPreventiva.objects.filter(
            status__in=['programada', 'em_execucao'],
            data_proxima_manutencao__lte=data_futura
        )

        for manutencao in manutencoes:
            for pecas_manutencao in manutencao.pecas_necessarias.all():
                peca = pecas_manutencao.peca
                quantidade_necessaria = pecas_manutencao.quantidade

                if peca not in pecas_necessarias:
                    pecas_necessarias[peca] = {
                        "fornecedor": peca.fornecedor,
                        'quantidade_necessaria': 0,
                        'quantidade_estoque': peca.estoque_atual,
                        'estoque_minimo': peca.estoque_minimo,
                        'preco_unitario': peca.preco,
                        'data_primeira_demanda': manutencao.data_proxima_manutencao
                    }

                pecas_necessarias[peca]['quantidade_necessaria'] += quantidade_necessaria
                if manutencao.data_proxima_manutencao < pecas_necessarias[peca]['data_primeira_demanda']:
                    pecas_necessarias[peca]['data_primeira_demanda'] = manutencao.data_proxima_manutencao

    # Peças com estoque abaixo do mínimo
    pecas_baixo_estoque = Pecas.objects.filter(estoque_atual__lt=F('estoque_minimo'))
    for peca in pecas_baixo_estoque:
        if peca not in pecas_necessarias:
            pecas_necessarias[peca] = {
                'quantidade_necessaria': 0,
                'quantidade_estoque': peca.estoque_atual,
                'estoque_minimo': peca.estoque_minimo,
                'preco_unitario': peca.preco,
                'data_primeira_demanda': None
            }

    # Calcula quantidade recomendada e valor total
    valor_total_compra = 0
    for peca, dados in pecas_necessarias.items():
        if dados['quantidade_estoque'] < dados['estoque_minimo']:
            dados['quantidade_compra_recomendada'] = dados['estoque_minimo'] - dados['quantidade_estoque']
        else:
            estoque_faltante = dados['quantidade_necessaria'] - (dados['quantidade_estoque'] - dados['estoque_minimo'])
            dados['quantidade_compra_recomendada'] = max(estoque_faltante, 0)
        
        dados['valor_total'] = dados['quantidade_compra_recomendada'] * dados['preco_unitario']
        valor_total_compra += dados['valor_total']

    if request.GET.get('imprimir'):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relatorio_pecas.pdf"'

        # Configuração de margens
        doc = BaseDocTemplate(
            response, pagesize=landscape(A4),
            leftMargin=margem_esquerda, rightMargin=margem_direita,
            topMargin=36, bottomMargin=36
        )

        def cabecalho(canvas, doc):
            canvas.saveState()
            
            # Título centralizado para página paisagem
            canvas.setFont("Helvetica-Bold", 14)
            canvas.drawCentredString(landscape(A4)[0] / 2, landscape(A4)[1] - 50, "Relatório de peças para comprar")

            # Data no canto inferior direito
            data_atual = datetime.now().strftime("%d/%m/%Y")
            canvas.setFont("Helvetica", 8)
            canvas.drawRightString(landscape(A4)[0] - doc.rightMargin, landscape(A4)[1] - 60, data_atual)

            # Número da página
            canvas.drawRightString(landscape(A4)[0] - doc.rightMargin, landscape(A4)[1] - 30, f"Página {doc.page}")

            canvas.restoreState()

        # Configuração do frame e template para paisagem
        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height - 50,
            id='normal'
        )
        template = PageTemplate(id='pagina1', frames=frame, onPage=cabecalho)
        doc.addPageTemplates([template])

        # Estilos e elementos do PDF
        styles = getSampleStyleSheet()
        elementos = []

        styles = getSampleStyleSheet()
        style = styles['Normal']
        style.fontSize = 10
        style.alignment = 1  # 1 é para centralizar o texto
        
        # Dados da tabela
        data = [
            [
                Paragraph('<b>Peça</b>', style),
                Paragraph('<b>Quantidade Necessária (Para Preventiva)</b>', style),
                Paragraph('<b>Quantidade em Estoque</b>', style),
                Paragraph('<b>Quantidade Mínima</b>', style),
                Paragraph('<b>Preço Unitário</b>', style),
                Paragraph('<b>Data Primeira Demanda</b>', style),
                Paragraph('<b>Quantidade Compra Recomendada</b>', style),
                Paragraph('<b>Valor Total</b>', style)
            ]
        ]

        for peca, dados in pecas_necessarias.items():
            data.append([
                Paragraph(peca.descricao, style),
                Paragraph(str(dados['quantidade_necessaria']), style),
                Paragraph(str(dados['quantidade_estoque']), style),
                Paragraph(str(dados['estoque_minimo']), style),
                Paragraph(f"R$ {dados['preco_unitario']:.2f}", style),
                Paragraph(str(dados['data_primeira_demanda']) if dados['data_primeira_demanda'] else 'N/A', style),
                Paragraph(str(dados['quantidade_compra_recomendada']), style),
                Paragraph(f"R$ {dados['valor_total']:.2f}", style)
            ])
            
        # Calcula larguras das colunas em função da largura disponível
        colWidths_table = [
            largura_disponivel * 0.3,  # Peça
            largura_disponivel * 0.15,  # Quantidade Necessária
            largura_disponivel * 0.15,  # Quantidade em Estoque
            largura_disponivel * 0.15,  # Quantidade Mínima
            largura_disponivel * 0.15,  # Preço Unitário
            largura_disponivel * 0.15,  # Data Primeira Demanda
            largura_disponivel * 0.15,  # Quantidade Compra Recomendada
            largura_disponivel * 0.15   # Valor Total
        ]

        # Cria a tabela com as larguras definidas
        table = Table(data, colWidths=colWidths_table)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        # Adiciona a tabela ao documento
        elementos.append(table)

        # Constrói o documento
        doc.build(elementos)
        return response

    elif request.GET.get('exportar_excel'):
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="relatorio_pecas.xlsx"'
        
        wb = gerar_excel_relatorio_pecas(pecas_necessarias)
        wb.save(response)
        return response

    return render(request, 'relatorios/pecas.html', {
        'pecas_necessarias': pecas_necessarias,
        'data_futura': data_futura,
        'prazo_dias': prazo_dias,
        'valor_total_compra': valor_total_compra
    })

@login_required
def gerar_relatorio_tecnicos(request):
    # Get query parameters
    nome_tecnico = request.GET.get('nome_tecnico', '').strip()
    is_active = request.GET.get('is_active')
    
    # Base query for technicians
    tecnicos = User.objects.filter(groups__name='Técnico')
    
    # Apply filters
    if nome_tecnico:
        tecnicos = tecnicos.filter(username__icontains=nome_tecnico)
    if is_active is not None:
        is_active = is_active == 'true'
        tecnicos = tecnicos.filter(is_active=is_active)
    
    # Calculate worked hours for last 12 months
    now = timezone.now()
    twelve_months_ago = now - timedelta(days=365)
    
    # Get all actions with technician hours for the last 12 months
    horas_por_mes = AcaoColaborador.objects.filter(
        colaborador__in=tecnicos,
        acao__chamado__data_criacao__gte=twelve_months_ago
    ).annotate(
        mes=TruncMonth('acao__chamado__data_criacao')
    ).values('colaborador', 'mes').annotate(
        total_horas=Sum('horas_trabalhadas')
    ).order_by('colaborador', 'mes')
    
    # Organize data by technician and month
    horas_dict = {}
    for hora in horas_por_mes:
        colaborador = hora['colaborador']
        mes_ano = hora['mes'].strftime('%Y-%m')
        if colaborador not in horas_dict:
            horas_dict[colaborador] = {}
        horas_dict[colaborador][mes_ano] = float(hora['total_horas'] or 0)
    
    # Generate months list for last 12 months
    meses = []
    for i in range(11, -1, -1):
        mes_data = now - timedelta(days=i*30)
        meses.append({
            'nome': mes_data.strftime('%b/%Y'),
            'valor': mes_data.strftime('%Y-%m')
        })

    if request.GET.get('imprimir'):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relatorio_tecnicos.pdf"'

        # Configure margins
        doc = BaseDocTemplate(
            response, pagesize=landscape(A4),
            leftMargin=36, rightMargin=36,
            topMargin=36, bottomMargin=36
        )

        def cabecalho(canvas, doc):
            canvas.saveState()
            
            # Title centered for landscape page
            canvas.setFont("Helvetica-Bold", 14)
            canvas.drawCentredString(landscape(A4)[0] / 2, landscape(A4)[1] - 50, "Relatório de Horas Trabalhadas por Técnico")

            # Date in bottom right
            data_atual = datetime.now().strftime("%d/%m/%Y")
            canvas.setFont("Helvetica", 8)
            canvas.drawRightString(landscape(A4)[0] - doc.rightMargin, landscape(A4)[1] - 60, data_atual)

            # Page number
            canvas.drawRightString(landscape(A4)[0] - doc.rightMargin, landscape(A4)[1] - 30, f"Página {doc.page}")

            canvas.restoreState()

        # Frame and template configuration for landscape
        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height - 50,
            id='normal'
        )
        template = PageTemplate(id='pagina1', frames=frame, onPage=cabecalho)
        doc.addPageTemplates([template])

        # Styles and PDF elements
        styles = getSampleStyleSheet()
        elementos = []

        # Add applied filters
        filtros = []
        if nome_tecnico:
            filtros.append(f"Nome: {nome_tecnico}")
        if is_active is not None:
            filtros.append(f"Ativo: {'Sim' if is_active else 'Não'}")
        if filtros:
            elementos.append(Paragraph("Filtros aplicados: " + ", ".join(filtros), styles['Normal']))
            elementos.append(Spacer(1, 20))

        # Table data
        data = [['Técnico', 'Status'] + [mes['nome'] for mes in meses]]
        
        for tecnico in tecnicos:
            row = [
                tecnico.username,
                'Ativo' if tecnico.is_active else 'Inativo'
            ]
            for mes in meses:
                horas = horas_dict.get(tecnico.id, {}).get(mes['valor'], 0)
                row.append(f"{horas:.1f}")
            data.append(row)

        # Calculate column widths
        largura_disponivel = doc.width
        col_widths = [
            largura_disponivel * 0.15,  # Técnico
            largura_disponivel * 0.08,  # Status
        ] + [largura_disponivel * 0.064] * 12  # 12 months

        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elementos.append(table)
        doc.build(elementos)
        return response

    context = {
        'tecnicos': tecnicos,
        'horas_dict': horas_dict,
        'meses': meses,
        'filtros': {
            'nome_tecnico': nome_tecnico,
            'is_active': is_active
        }
    }
    return render(request, 'relatorios/tecnicos.html', context)

@login_required
def gerar_relatorio_indicadores(request):
    # Obtém o primeiro dia do mês atual
    hoje = timezone.now()
    meses_analise = [
    (hoje.year if hoje.month > i else hoje.year - 1, (hoje.month - i) % 12 or 12)
    for i in range(12)
][::-1]

    
    # Debug dos meses sendo analisados
    # print("\nMeses em análise:")
    # for ano, mes in meses_analise:
        # print(f"- {mes}/{ano}")
    
    # Filtros
    tag = request.GET.get('tag', '').strip()
    nome_equipamento = request.GET.get('nome_equipamento', '').strip()
    classe = request.GET.get('classe', '').strip()
    setor = request.GET.get('setor', '').strip()

    filtros = [
        f"TAG: {tag}" if tag else None,
        f"Nome Equipamento: {nome_equipamento}" if nome_equipamento else None,
        f"Classe: {classe}" if classe else None,
        f"Setor: {setor}" if setor else None
    ]
    filtros = ", ".join(filter(None, filtros))  # Geração da string de filtros

    # Debug dos filtros aplicados
    # print("\nFiltros aplicados:")
    # print(f"TAG: {tag if tag else 'Nenhum'}")
    # print(f"Nome: {nome_equipamento if nome_equipamento else 'Nenhum'}")
    # print(f"Classe: {classe if classe else 'Nenhuma'}")
    # print(f"Setor: {setor if setor else 'Nenhum'}")

    # Obtenção dos equipamentos com base nos filtros
    equipamentos = Equipamento.objects.all()
    if tag:
        equipamentos = equipamentos.filter(tag__icontains=tag)
    if nome_equipamento:
        equipamentos = equipamentos.filter(nome__icontains=nome_equipamento)
    if classe:
        equipamentos = equipamentos.filter(classe=classe)
    if setor:
        equipamentos = equipamentos.filter(setor__nome=setor)

    # Lista para armazenar os indicadores
    indicadores = []
    # Dicionários para armazenar os indicadores por setor e classe
    dados_por_setor = defaultdict(lambda: defaultdict(list))
    dados_por_classe = defaultdict(lambda: defaultdict(list))

    # Processamento por equipamento e por mês
    for equipamento in equipamentos:
        # print(f"\nProcessando equipamento: {equipamento.tag} - {equipamento.nome}")
        
        for ano, mes in meses_analise:
            # print(f"\nProcessando mês {mes}/{ano}")
            
            primeiro_dia = timezone.datetime(ano, mes, 1)
            ultimo_dia = (primeiro_dia.replace(month=mes % 12 + 1, day=1) - timedelta(days=1)) if mes != 12 else primeiro_dia.replace(year=ano + 1, month=1, day=1) - timedelta(days=1)


            # Obtém histórico de horas do mês
            historico_horas = HistoricoHorasMensais.objects.filter(
                equipamento=equipamento,
                ano=ano,
                mes=mes
            ).first()

            tempo_operacao = float(historico_horas.horas_trabalhadas) if historico_horas else 0.0

            # Obtém chamados corretivos do mês
            chamados_corretivos = Chamado.objects.filter(
                equipamento=equipamento,
                tipo_manutencao='corretiva',
                data_criacao__gte=primeiro_dia,
                data_criacao__lte=ultimo_dia
            )
            
            chamados_count = chamados_corretivos.count()
            
            # Cálculo do tempo total de parada
            tempo_parada_total = 0.0
            for chamado in chamados_corretivos:
                acoes_tempo = Acao.objects.filter(chamado=chamado).aggregate(
                    total_downtime=Sum('duracao'))['total_downtime'] or 0
                tempo_parada_total += float(acoes_tempo)

            # Debug dos valores intermediários
            # print(f"Tempo de operação: {tempo_operacao:.2f}h")
            # print(f"Número de chamados corretivos: {chamados_count}")
            # print(f"Tempo total de parada: {tempo_parada_total:.2f}h")

            # Cálculo de MTBF, MTTR e disponibilidade
            if chamados_count > 0:
                mtbf = tempo_operacao / chamados_count
                mttr = tempo_parada_total / chamados_count
            else:
                mtbf = tempo_operacao if tempo_operacao > 0 else 0.0
                mttr = 0.0

            disponibilidade = (mtbf / (mtbf + mttr) * 100) if (mtbf + mttr) > 0 else 100.0

            # Debug dos indicadores calculados
            # print(f"MTBF calculado: {mtbf:.2f}h")
            # print(f"MTTR calculado: {mttr:.2f}h")
            # print(f"Disponibilidade calculada: {disponibilidade:.2f}%")

            # Adiciona aos indicadores
            indicadores.append({
                'equipamento': equipamento,
                'ano': ano,
                'mes': mes,
                'tempo_operacao': round(tempo_operacao, 2),
                'chamados_corretivos': chamados_count,
                'horas_paradas': round(tempo_parada_total, 2),
                'mtbf': round(mtbf, 2),
                'mttr': round(mttr, 2),
                'disponibilidade': round(disponibilidade, 2)
            })

            setor = equipamento.setor.nome
            classe = equipamento.classe

            dados_por_setor[setor]['mtbf'].append(mtbf)
            dados_por_setor[setor]['mttr'].append(mttr)
            dados_por_setor[setor]['disponibilidade'].append(disponibilidade)

            dados_por_classe[classe]['mtbf'].append(mtbf)
            dados_por_classe[classe]['mttr'].append(mttr)
            dados_por_classe[classe]['disponibilidade'].append(disponibilidade)

    meses_labels = [f"{mes}/{ano}" for ano, mes in meses_analise]

    if not request.GET.get('exportar_excel') and not request.GET.get('imprimir'):
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        paginator = Paginator(indicadores, 25)  # 25 items por página
        page = request.GET.get('page')
        try:
            indicadores_page = paginator.page(page)
        except PageNotAnInteger:
            indicadores_page = paginator.page(1)
        except EmptyPage:
            indicadores_page = paginator.page(paginator.num_pages)
        indicadores = indicadores_page
        is_paginated = paginator.num_pages > 1
    else:
        is_paginated = False

    if request.GET.get('exportar_excel'):
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="relatorio_indicadores.xlsx"'
        
        wb = gerar_excel_indicadores(indicadores)
        wb.save(response)
        return response
    
    elif request.GET.get('imprimir'):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="relatorio_indicadores.pdf"'

        # Configuração de margens
        margem_esquerda = margem_direita = margem_superior = margem_inferior = 36
        doc = BaseDocTemplate(
            response, pagesize=A4,
            leftMargin=margem_esquerda, rightMargin=margem_direita,
            topMargin=margem_superior, bottomMargin=margem_inferior
        )

        def cabecalho(canvas, doc):
            canvas.saveState()
            
            # Título centralizado - removida dependência do logo
            canvas.setFont("Helvetica-Bold", 14)
            canvas.drawCentredString(A4[0] / 2, A4[1] - 50, "Relatório de Indicadores")

            # Data no canto inferior direito
            data_atual = datetime.now().strftime("%d/%m/%Y")
            canvas.setFont("Helvetica", 8)
            canvas.drawRightString(A4[0] - doc.rightMargin, A4[1] - 60, data_atual)

            # Número da página
            canvas.drawRightString(A4[0] - doc.rightMargin, A4[1] - 30, f"Página {doc.page}")

            canvas.restoreState()

        # Configuração do frame e template
        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height - 50,
            id='normal'
        )
        template = PageTemplate(id='pagina1', frames=frame, onPage=cabecalho)
        doc.addPageTemplates([template])

        # Estilos e elementos do PDF
        styles = getSampleStyleSheet()
        elementos = []

        # Adiciona filtros aplicados
        if filtros:
            elementos.append(Paragraph(f"Filtros aplicados: {filtros}", styles['Normal']))
            elementos.append(Spacer(1, 20))

        # Processa cada indicador
        for indicador in indicadores:
            # Seção 1: Informações do equipamento
            data_section_1 = [
                ["TAG", "Nome", "Classe", "Setor"],
                [
                    indicador['equipamento'].tag,
                    indicador['equipamento'].nome,
                    indicador['equipamento'].classe,
                    str(indicador['equipamento'].setor)
                ]
            ]

            # Calcula larguras das colunas
            largura_disponivel = doc.width
            colWidths_section1 = [
                largura_disponivel * 0.1,
                largura_disponivel * 0.6,
                largura_disponivel * 0.15,
                largura_disponivel * 0.15
            ]

            # Cria tabela da seção 1
            table_section_1 = Table(data_section_1, colWidths=colWidths_section1)
            table_section_1.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
                ('ALIGN', (0, 1), (-1, 1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, 1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 2),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            # Seção 2: Dados dos indicadores
            data_section_2 = [
                [
                    "Ano", "Mês", "Operação (Hrs)", 
                    "Nº Chamados (Cor.)", "Horas de parada",
                    "MTBF(hr)", "MTTR(hr)", "Disponibilidade"
                ],
                [
                    indicador['ano'],
                    indicador['mes'],
                    f"{indicador['tempo_operacao']}h",
                    indicador['chamados_corretivos'],
                    f"{indicador['horas_paradas']}h",
                    indicador['mtbf'],
                    indicador['mttr'],
                    f"{indicador['disponibilidade']}%"
                ]
            ]

            # Calcula larguras das colunas para seção 2
            colWidths_section2 = [
                largura_disponivel * 0.05,  # Ano
                largura_disponivel * 0.05,  # Mês
                largura_disponivel * 0.14,  # Operação
                largura_disponivel * 0.16,  # Chamados
                largura_disponivel * 0.14,  # Horas parada
                largura_disponivel * 0.10,  # MTBF
                largura_disponivel * 0.10,  # MTTR
                largura_disponivel * 0.13   # Disponibilidade
            ]

            # Cria tabela da seção 2
            table_section_2 = Table(data_section_2, colWidths=colWidths_section2)
            table_section_2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
                ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, 1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 2),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            # Adiciona as tabelas ao documento
            elementos.append(table_section_1)
            #elementos.append(Spacer(1, 10))
            elementos.append(table_section_2)
            elementos.append(Spacer(1, 20))

        # Constrói o documento
        doc.build(elementos)
        return response
     
    equipamentos_selecionados = equipamentos.filter(
        Q(nome__icontains=nome_equipamento) | Q(tag__icontains=tag)
    )

    dados_equip_selecionados = {}

    for equipamento in equipamentos_selecionados:
        dados_equip_selecionados[equipamento.nome] = {
            'mtbf': [],
            'mttr': [],
            'disponibilidade': []
        }
        for ano, mes in meses_analise:
            historico_horas = HistoricoHorasMensais.objects.filter(
                equipamento=equipamento, ano=ano, mes=mes
            ).first()
            tempo_operacao = float(historico_horas.horas_trabalhadas) if historico_horas else 0.0

            chamados_corretivos = Chamado.objects.filter(
                equipamento=equipamento, tipo_manutencao='corretiva',
                data_criacao__year=ano, data_criacao__month=mes
            )
            chamados_count = chamados_corretivos.count()
            tempo_parada_total = sum(
                Acao.objects.filter(chamado=chamado).aggregate(Sum('duracao'))['duracao__sum'] or 0
                for chamado in chamados_corretivos
            )

            # Convert both values to Decimal explicitly
            tempo_operacao = Decimal(str(tempo_operacao))
            tempo_parada_total = Decimal(str(tempo_parada_total))

            # Convert both to Decimal for consistent arithmetic
            mtbf = Decimal(str(mtbf))  # Convert float to string then to Decimal
            mttr = Decimal(str(mttr))  # Assuming mttr might already be Decimal, but we ensure

            if chamados_count > 0:
                mtbf = tempo_operacao / chamados_count
                mttr = tempo_parada_total / chamados_count
            else:
                mtbf = Decimal(tempo_operacao) if tempo_operacao > 0 else Decimal('0.0')
                mttr = Decimal('0.0')

            disponibilidade = (mtbf / (mtbf + mttr) * Decimal('100.0')) if (mtbf + mttr) > 0 else Decimal('100.0')

            dados_equip_selecionados[equipamento.nome]['mtbf'].append(round(mtbf, 2))
            dados_equip_selecionados[equipamento.nome]['mttr'].append(round(mttr, 2))
            dados_equip_selecionados[equipamento.nome]['disponibilidade'].append(round(disponibilidade, 2))

    dados_mtbf_equip = {k: list(map(float, v['mtbf'])) for k, v in dados_equip_selecionados.items()}
    dados_mttr_equip = {k: list(map(float, v['mttr'])) for k, v in dados_equip_selecionados.items()}
    dados_disp_equip = {k: list(map(float, v['disponibilidade'])) for k, v in dados_equip_selecionados.items()}
        
    context = {
        'page_obj': indicadores,  # replace 'indicadores' with the paginated object
        'is_paginated': is_paginated,
        'indicadores': indicadores,
        'setores': Setor.objects.all(),
        'classes': list(set(Equipamento.objects.values_list('classe', flat=True).distinct())),
        'meses_analise': meses_analise,
        'meses_labels': json.dumps(meses_labels),
        'dados_mtbf_setor': json.dumps({k: v['mtbf'] for k, v in dados_por_setor.items()}, default=list),
        'dados_mttr_setor': json.dumps({k: v['mttr'] for k, v in dados_por_setor.items()}, default=list),
        'dados_disp_setor': json.dumps({k: v['disponibilidade'] for k, v in dados_por_setor.items()}, default=list),
        'dados_mtbf_classe': json.dumps({k: v['mtbf'] for k, v in dados_por_classe.items()}, default=list),
        'dados_mttr_classe': json.dumps({k: v['mttr'] for k, v in dados_por_classe.items()}, default=list),
        'dados_disp_classe': json.dumps({k: v['disponibilidade'] for k, v in dados_por_classe.items()}, default=list),
        'dados_mtbf_equip': json.dumps(dados_mtbf_equip),
        'dados_mttr_equip': json.dumps(dados_mttr_equip),
        'dados_disp_equip': json.dumps(dados_disp_equip),
        'equipamentos_selecionados': list(dados_equip_selecionados.keys()),  # Lista dos equipamentos filtrados
        }
    
    return render(request, 'relatorios/indicadores.html', context)

    

register = template.Library()

@register.filter
def get_month_name(value):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    try:
        return months[int(value) - 1]
    except (ValueError, IndexError):
        return value