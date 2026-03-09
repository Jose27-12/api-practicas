import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()


class EmailService:

    def __init__(self):
        self.api_key = os.getenv("BREVO_API_KEY")

    def send_email(self, destinatario: str, asunto: str, mensaje: str, pdf_path: str):

        # convertir PDF a base64
        with open(pdf_path, "rb") as f:
            pdf_base64 = base64.b64encode(f.read()).decode()

        url = "https://api.brevo.com/v3/smtp/email"

        headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json"
        }

        data = {
            "sender": {
                "name": "Chatbot Report",
                "email": "fandino850@gmail.com"
            },
            "to": [
                {"email": destinatario}
            ],
            "subject": asunto,
            "htmlContent": f"<p>{mensaje}</p>",
            "attachment": [
                {
                    "content": pdf_base64,
                    "name": os.path.basename(pdf_path)
                }
            ]
        }

        response = requests.post(url, json=data, headers=headers)

        print("Status:", response.status_code)
        print("Response:", response.text)