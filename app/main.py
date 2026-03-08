from fastapi import FastAPI, Depends, HTTPException
from app.database import SessionLocal
from app.schemas import ConversationCreate, MessageCreate
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from app.ml.chatbot import chat_practicas
from pydantic import BaseModel
from app.services.report_service import ReportService
from app.utils.email_service import EmailService
from app.schemas import ReportRequest
from app.services.pdf_service import PDFService
from app.services.message_service import MessageService

app = FastAPI()

# ───────────── CORS ─────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────── DB DEPENDENCY ─────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ───────────── ROOT ─────────────

@app.get("/")
def home():
    return {"mensaje": "API funcionando correctamente"}

# ───────────── CONVERSACIONES ─────────────

@app.get("/conversations")
def get_conversations(user_id: int, db=Depends(get_db)):
    service = ConversationService(db)
    conversations = service.get_active_conversations_by_user(user_id)
    return conversations


@app.get("/conversations/history")
def get_closed_conversations(user_id: int, db=Depends(get_db)):
    service = ConversationService(db)
    conversations = service.get_closed_conversations_by_user(user_id)
    return conversations


@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: int, db=Depends(get_db)):
    service = ConversationService(db)
    conversation = service.get_conversation_by_id(conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    return conversation


@app.post("/conversations")
def create_conversation(data: ConversationCreate, db=Depends(get_db)):
    service = ConversationService(db)
    conversation = service.create_conversation(data.user_id)
    return dict(conversation._mapping)


@app.put("/conversations/{conversation_id}/close")
def close_conversation(conversation_id: int, db=Depends(get_db)):
    service = ConversationService(db)
    conversation = service.close_conversation(conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    return dict(conversation._mapping)

# ───────────── MENSAJES ─────────────

@app.get("/messages")
def get_messages(conversation_id: Optional[int] = None, db=Depends(get_db)):
    service = MessageService(db)
    messages = service.get_messages(conversation_id)
    return [dict(row._mapping) for row in messages]


@app.post("/messages")
def create_message(data: MessageCreate, db=Depends(get_db)):
    service = MessageService(db)
    message = service.create_message(data.dict())
    return dict(message._mapping)

# ───────────── CHATBOT ─────────────

class ChatRequest(BaseModel):
    conversation_id: int
    message: str
    sender: str = "user"


@app.post("/chatbot")
def chatbot(data: ChatRequest, db=Depends(get_db)):

    message_service = MessageService(db)

    # 1️⃣ Guardar mensaje del usuario
    message_service.create_message({
        "conversation_id": data.conversation_id,
        "sender": "user",
        "message": data.message
    })

    # 2️⃣ Obtener respuesta del modelo IA
    respuesta = chat_practicas(data.message)

    # 3️⃣ Guardar respuesta del bot
    message_service.create_message({
        "conversation_id": data.conversation_id,
        "sender": "bot",
        "message": respuesta
    })

    return {
        "response": respuesta
    }

# ───────────── REPORTE NLP ─────────────
@app.post("/conversations/{conversation_id}/report")
def generate_report(conversation_id: int, data: ReportRequest, db=Depends(get_db)):

    conversation_service = ConversationService(db)
    message_service = MessageService(db)
    report_service = ReportService()
    pdf_service = PDFService()
    email_service = EmailService()

    conversation = conversation_service.get_conversation_by_id(conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")

    # 🔥 obtener mensajes correctamente
    mensajes = message_service.get_messages(conversation_id)

    reporte = report_service.generar_reporte(mensajes)

    pdf_path = pdf_service.generar_pdf(
        conversation_id,
        mensajes,
        reporte
    )

    mensaje_email = "Adjunto encontrarás el reporte de la conversación."

    email_service.send_email(
        data.email,
        "Reporte de conversación",
        mensaje_email,
        pdf_path
    )

    return {
        "mensaje": "Reporte enviado con PDF",
        "email": data.email
    }