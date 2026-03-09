import os
import re
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

client = InferenceClient(api_key=HF_TOKEN)


def chat_practicas(pregunta: str):

    try:

        completion = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": """
Eres un asistente virtual especializado en una plataforma de gestión de prácticas académicas universitarias.

Tu función es ayudar a estudiantes, docentes y empresas con información clara, puntual y concisa sobre:

- registro de empresas
- seguimiento de prácticas académicas
- informes de avance
- evaluación final de prácticas
- tutor académico y tutor empresarial
- finalización de prácticas

Responde en máximo 3 o 4 líneas.

Si la pregunta no está relacionada con prácticas académicas responde:
"Este asistente solo responde preguntas sobre la plataforma de gestión de prácticas académicas."

Si el usuario escribe "finalizar", "salir" o "terminar conversación":
"La conversación ha finalizado. Gracias por usar el asistente de prácticas académicas."
"""
                },
                {
                    "role": "user",
                    "content": pregunta
                }
            ],
            max_tokens=120,
            temperature=0.3
        )

        respuesta = completion.choices[0].message.content

        respuesta = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ0-9.,¿?¡! ]', '', respuesta)

        return respuesta.strip()

    except Exception as e:
        print("ERROR:", e)
        return "Error al consultar el modelo."