from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime


class PDFService:

    def generar_pdf(self, conversation_id, mensajes, reporte):

        filename = f"reporte_conversacion_{conversation_id}.pdf"

        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        # 🎨 estilos personalizados
        titulo_style = ParagraphStyle(
            'Titulo',
            parent=styles['Title'],
            textColor=colors.HexColor("#1E3A8A"),
            fontSize=24
        )

        seccion_style = ParagraphStyle(
            'Seccion',
            parent=styles['Heading2'],
            textColor=colors.HexColor("#1E3A8A")
        )

        texto_style = ParagraphStyle(
            'Texto',
            parent=styles['Normal'],
            fontSize=11,
            leading=15
        )

        elementos = []

        # Título
        elementos.append(
            Paragraph("Reporte de Conversación del Chatbot", titulo_style)
        )

        elementos.append(Spacer(1, 15))

        elementos.append(
            Paragraph(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", texto_style)
        )

        elementos.append(Spacer(1, 25))

        # --- ANALISIS NLP ---
        elementos.append(
            Paragraph("Análisis NLP", seccion_style)
        )

        elementos.append(Spacer(1, 10))

        data = [
            ["Sentimiento", reporte["sentimiento"]],
            ["Palabras clave", ", ".join(reporte["palabras_clave"])],
            ["Resumen", reporte["resumen"]],
        ]

        tabla = Table(data, colWidths=[150, 350])

        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR",(0,0),(0,-1),colors.white),

            ("BACKGROUND",(1,0),(1,-1),colors.whitesmoke),

            ("GRID",(0,0),(-1,-1),1,colors.HexColor("#CBD5F5")),

            ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
        ]))

        elementos.append(tabla)

        elementos.append(Spacer(1, 30))

        # --- CONVERSACION ---
        elementos.append(
            Paragraph("Conversación", seccion_style)
        )

        elementos.append(Spacer(1, 15))

        for m in mensajes:

            sender = m.get("sender", "usuario")
            contenido = m.get("message", "")

            if sender.lower() in ["user", "usuario"]:
                etiqueta = "<font color='#22D3EE'><b>Usuario:</b></font>"
            else:
                etiqueta = "<font color='#1E3A8A'><b>Asistente:</b></font>"

            texto = f"{etiqueta} {contenido}"

            elementos.append(Paragraph(texto, texto_style))
            elementos.append(Spacer(1, 8))

        doc.build(elementos)

        return filename