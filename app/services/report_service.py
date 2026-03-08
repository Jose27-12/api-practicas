class ReportService:

    def generar_reporte(self, mensajes):

        if not mensajes:
            return {
                "sentimiento": "neutral",
                "palabras_clave": [],
                "resumen": "No hay mensajes"
            }

        textos = []

        for m in mensajes:

            contenido = (
                m.get("message") or
                m.get("contenido") or
                m.get("text") or
                ""
            )

            textos.append(contenido)

        texto = " ".join(textos).lower()

        palabras = texto.split()

        keywords = list(set(palabras))[:5]

        sentimiento = "positivo"

        if "problema" in palabras or "error" in palabras:
            sentimiento = "negativo"

        return {
            "sentimiento": sentimiento,
            "palabras_clave": keywords,
            "resumen": f"Conversación con {len(mensajes)} mensajes."
        }