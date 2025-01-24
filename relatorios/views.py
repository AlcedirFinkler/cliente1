# reports/views.py
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from django.utils import timezone
from CadEquip.models import Equipamento
from cadEstoque.models import Pecas
from gestaoOS.models import Chamado
from GestaoPrev.models import ManutencaoPreventiva

def criar_pdf_base(response, title):
    # Registrar fonte personalizada
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
    
    def cabecalho_rodape(canvas, doc):
        canvas.saveState()
        canvas.setFont('Arial', 9)
        canvas.drawString(inch, doc.height + doc.topMargin + inch, title)
        canvas.drawRightString(doc.width + doc.leftMargin + inch, 
                               doc.height + doc.topMargin + inch, 
                               f"Página {canvas.getPageNumber()}")
        canvas.line(inch, doc.height + doc.topMargin + 0.5*inch, 
                    doc.width + doc.leftMargin + inch, 
                    doc.height + doc.topMargin + 0.5*inch)
        canvas.restoreState()

    doc = SimpleDocTemplate(
        response, 
        pagesize=letter, 
        topMargin=1*inch, 
        bottomMargin=1*inch,
        onFirstPage=cabecalho_rodape,
        onLaterPages=cabecalho_rodape
    )
    
    estilos = getSampleStyleSheet()
    
    # Estilo personalizado com sublinhado
    estilo_campo = ParagraphStyle(
        'CampoSublinhado',
        parent=estilos['Normal'],
        textColor=colors.black,
        borderColor=colors.black,
        borderWidth=1,
        borderPadding=3,
        borderRadius=0,
        textDecoration='underline'
    )
    
    return doc, estilo_campo, estilos

def gerar_relatorio_equipamentos(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_equipamentos.pdf"'
    
    doc, estilo_campo, estilos = criar_pdf_base(response, "Relatório de Equipamentos")
    elementos = []
    
    # Dados dos equipamentos
    equipamentos = Equipamento.objects.all().select_related('setor')
    
    # Preparar dados com campos sublinhados
    dados = [
        [
            Paragraph('Nome', estilos['Heading4']), 
            Paragraph('Tag', estilos['Heading4']), 
            Paragraph('Modelo', estilos['Heading4']), 
            Paragraph('Fabricante', estilos['Heading4']), 
            Paragraph('Setor', estilos['Heading4']),
            Paragraph('Ano Fabricação', estilos['Heading4'])
        ]
    ]
    
    for equip in equipamentos:
        dados.append([
            Paragraph(str(equip.nome), estilo_campo), 
            Paragraph(str(equip.tag), estilo_campo), 
            Paragraph(str(equip.modelo), estilo_campo), 
            Paragraph(str(equip.fabricante), estilo_campo), 
            Paragraph(str(equip.setor.nome), estilo_campo), 
            Paragraph(str(equip.ano_fabricacao or 'Não informado'), estilo_campo)
        ])
    
    # Criar tabela com campos sublinhados
    tabela = Table(dados, repeatRows=1, colWidths=[100]*6)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    
    elementos.append(tabela)
    
    # Gerar PDF
    doc.build(elementos)
    return response