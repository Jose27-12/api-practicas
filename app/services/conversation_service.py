from sqlalchemy import text
from datetime import datetime, timedelta

class ConversationService:

    def __init__(self, db):
        self.db = db

    def create_conversation(self, user_id: int):
        result = self.db.execute(
            text("""
                INSERT INTO conversations(user_id)
                VALUES (:user_id)
                RETURNING *
            """),
            {"user_id": user_id}
        )
        self.db.commit()
        return result.fetchone()

    def close_conversation(self, conversation_id: int):
        result = self.db.execute(
            text("""
                UPDATE conversations
                SET status='cerrada',
                    ended_at=:ended_at
                WHERE id=:id
                RETURNING *
            """),
            {
                "id": conversation_id,
                "ended_at": datetime.utcnow()
            }
        )
        
        print("Filas afectadas:", result.rowcount)
        self.db.commit()
        return result.fetchone()
    
    def get_active_conversations_by_user(self, user_id):
        query = """
            SELECT *
            FROM conversations
            WHERE user_id = :user_id
            AND status = 'activa'
            ORDER BY started_at DESC
        """
        result = self.db.execute(text(query), {"user_id": user_id})
        rows = result.fetchall()

        return [
            {
                "id": row.id,
                "estado": row.status,
                "fecha_inicio": row.started_at,
                "fecha_fin": row.ended_at,
            }
            for row in rows
        ]
        
    
    def get_closed_conversations_by_user(self, user_id):
        query = """
            SELECT c.*
            FROM conversations c
            WHERE c.user_id = :user_id
            AND c.status = 'cerrada'
            AND EXISTS (
                SELECT 1
                FROM messages m
                WHERE m.conversation_id = c.id
            )
            ORDER BY c.started_at DESC
        """

        result = self.db.execute(text(query), {"user_id": user_id})
        rows = result.fetchall()

        return [
            {
                "id": row.id,
                "estado": row.status,
                "fecha_inicio": row.started_at,
                "fecha_fin": row.ended_at,
            }
            for row in rows
        ]
        
    def get_conversation_by_id(self, conversation_id):
        # Traer conversación
        conversation = self.db.execute(
            text("SELECT * FROM conversations WHERE id = :conversation_id"),
            {"conversation_id": conversation_id}
        ).fetchone()

        if not conversation:
            return None

        # Traer mensajes asociados
        messages = self.db.execute(
            text("""
                SELECT id, conversation_id, sender, message, created_at
                FROM messages
                WHERE conversation_id = :conversation_id
                ORDER BY created_at ASC
            """),
            {"conversation_id": conversation_id}
        ).fetchall()

        # Formatear respuesta como espera el frontend
        return {
            "id": conversation.id,
            "estado": conversation.status,
            "fecha_inicio": conversation.started_at,
            "fecha_fin": conversation.ended_at,
            "mensajes": [
                {
                    "rol": "user" if m.sender.lower() in ["usuario", "user"] else "assistant",
                    "contenido": m.message,
                    "hora": m.created_at
                }
                for m in messages
            ]
        }
    
    def auto_close_if_inactive(self, conversation_id):
        conversation = self.db.execute(
            text("SELECT * FROM conversations WHERE id = :id"),
            {"id": conversation_id}
        ).fetchone()

        if not conversation or conversation.status == "cerrada":
            return

        last_message = self.db.execute(
            text("""
                SELECT created_at
                FROM messages
                WHERE conversation_id = :id
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"id": conversation_id}
        ).fetchone()

        if not last_message:
            return

        diff = datetime.utcnow() - last_message.created_at

        if diff > timedelta(minutes=5):
            self.close_conversation(conversation_id)
    
    