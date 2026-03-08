from sqlalchemy import text
from datetime import datetime

class MessageService:

    def __init__(self, db):
        self.db = db

    def get_messages(self, conversation_id=None):

        query = "SELECT * FROM messages WHERE 1=1"
        params = {}

        if conversation_id:
            query += " AND conversation_id = :conversation_id"
            params["conversation_id"] = conversation_id

        query += " ORDER BY created_at ASC"

        result = self.db.execute(text(query), params)

        return [dict(row._mapping) for row in result.fetchall()]

    # ✅ Método dentro de la clase
    def create_message(self, data: dict):

        query = """
            INSERT INTO messages (conversation_id, sender, message)
            VALUES (:conversation_id, :sender, :message)
            RETURNING *
        """

        result = self.db.execute(text(query), data)

        # actualizar actividad de la conversación
        self.db.execute(
            text("""
                UPDATE conversations
                SET last_activity_at = :now
                WHERE id = :conversation_id
            """),
            {
                "now": datetime.utcnow(),
                "conversation_id": data["conversation_id"]
            }
        )

        self.db.commit()

        return result.fetchone()