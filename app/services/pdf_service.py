from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime


class PDFService:

    def generar_pdf(self, conversation_id, mensajes, reporte):

        filename = f"reporte_conversacion_{conversation_id}.pdf"

        c = canvas.Canvas(filename, pagesize=letter)

        y = 750

        # Título
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, y, "Reporte de Conversación")

        # Fecha
        y -= 30
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # Información del análisis
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Análisis de la conversación")

        y -= 20
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Sentimiento: {reporte['sentimiento']}")

        y -= 20
        c.drawString(50, y, f"Palabras clave: {', '.join(reporte['palabras_clave'])}")

        y -= 20
        c.drawString(50, y, f"Resumen: {reporte['resumen']}")

        # Conversación
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Conversación")

        y -= 25
        c.setFont("Helvetica", 11)

        for m in mensajes:

            sender = m.get("sender", "usuario")
            contenido = m.get("message", "")

            if sender.lower() == "user" or sender.lower() == "usuario":
                etiqueta = "Usuario"
            else:
                etiqueta = "Bot"

            texto = f"{etiqueta}: {contenido}"

            # dividir texto largo
            lineas = self.wrap_text(texto, 80)

            for linea in lineas:

                c.drawString(60, y, linea)

                y -= 18

                if y < 50:
                    c.showPage()
                    y = 750
                    c.setFont("Helvetica", 11)

        c.save()

        return filename

    def wrap_text(self, text, max_chars):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line + " " + word) <= max_chars:
                current_line += " " + word
            else:
                lines.append(current_line.strip())
                current_line = word

        lines.append(current_line.strip())

        return lines