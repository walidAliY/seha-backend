from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MessageCreate(BaseModel):
    content: str
    attachments: Optional[List[str]] = None

class MessageResponse(BaseModel):
    message_id: int
    session_id: int
    role: str
    content: str
    attachments: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SessionCreate(BaseModel):
    session_title: Optional[str] = "New Conversation"

class SessionResponse(BaseModel):
    session_id: int
    user_id: int
    session_title: str
    started_at: datetime
    last_message_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
