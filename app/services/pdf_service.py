from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
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

        elementos = []

        # Título
        titulo = Paragraph(
            "<b>Reporte de Conversación del Chatbot</b>",
            styles['Title']
        )

        elementos.append(titulo)
        elementos.append(Spacer(1, 20))

        # Fecha
        fecha = Paragraph(
            f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles['Normal']
        )

        elementos.append(fecha)
        elementos.append(Spacer(1, 20))

        # --- ANÁLISIS ---
        elementos.append(Paragraph("<b>Análisis de la Conversación</b>", styles['Heading2']))
        elementos.append(Spacer(1, 10))

        data = [
            ["Sentimiento", reporte["sentimiento"]],
            ["Palabras clave", ", ".join(reporte["palabras_clave"])],
            ["Resumen", reporte["resumen"]],
        ]

        tabla = Table(data, colWidths=[150, 350])

        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
            ("TEXTCOLOR",(0,0),(-1,-1),colors.black),

            ("GRID",(0,0),(-1,-1),1,colors.grey),

            ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),

            ("VALIGN",(0,0),(-1,-1),"TOP"),
        ]))

        elementos.append(tabla)
        elementos.append(Spacer(1, 30))

        # --- CONVERSACIÓN ---
        elementos.append(Paragraph("<b>Conversación</b>", styles['Heading2']))
        elementos.append(Spacer(1, 15))

        for m in mensajes:

            sender = m.get("sender", "usuario")
            contenido = m.get("message", "")

            if sender.lower() in ["user", "usuario"]:
                etiqueta = "<b>Usuario:</b>"
            else:
                etiqueta = "<b>Bot:</b>"

            texto = f"{etiqueta} {contenido}"

            p = Paragraph(texto, styles['Normal'])

            elementos.append(p)
            elementos.append(Spacer(1, 10))

        doc.build(elementos)

        return filename