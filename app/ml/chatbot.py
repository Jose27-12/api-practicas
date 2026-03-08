from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch
import re

BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
LORA_MODEL = "JoseFand/modelo-practicas-academicas"

print("Cargando modelo IA...")

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float32
)

model = PeftModel.from_pretrained(base_model, LORA_MODEL)

print("Modelo cargado correctamente")

def chat_practicas(pregunta: str):

    prompt = f"""
Eres un asistente virtual especializado en prácticas académicas universitarias.

Reglas:
- Responde siempre en español.
- Máximo 2 frases.
- No uses inglés.
- Usa palabras simples.

Usuario: {pregunta}
Asistente:
"""

    inputs = tokenizer(prompt, return_tensors="pt")

    output = model.generate(
        **inputs,
        max_new_tokens=110,
        do_sample=True,
        temperature=0.3,
        top_p=0.6,
        repetition_penalty=1.4,
        no_repeat_ngram_size=3,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id
    )

    respuesta = tokenizer.decode(output[0], skip_special_tokens=True)
    respuesta = respuesta.split("Asistente:")[-1].strip()

    # eliminar caracteres raros
    respuesta = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ0-9.,¿?¡! ]', '', respuesta)

    # eliminar palabras en inglés comunes
    ingles = ["the","and","for","with","you","your","this","that","from","if"]
    palabras = respuesta.split()
    palabras = [p for p in palabras if p.lower() not in ingles]

    respuesta = " ".join(palabras)

    return respuesta