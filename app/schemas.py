from pydantic import BaseModel

class ConversationCreate(BaseModel):
    user_id: int

class MessageCreate(BaseModel):
    conversation_id: int
    sender: str
    message: str
    
class ReportRequest(BaseModel):
    email: str