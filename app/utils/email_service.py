import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


class EmailService:

    def __init__(self):
        self.email_user = os.getenv("EMAIL_USER")
        self.email_pass = os.getenv("EMAIL_PASS")

    def send_email(self, destinatario: str, asunto: str, mensaje: str, pdf_path: str):

        msg = EmailMessage()

        msg["Subject"] = asunto
        msg["From"] = self.email_user
        msg["To"] = destinatario

        msg.set_content(mensaje)

        # Adjuntar el PDF
        with open(pdf_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename=os.path.basename(pdf_path)
            )

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(self.email_user, self.email_pass)
            server.send_message(msg)