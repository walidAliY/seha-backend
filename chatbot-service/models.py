from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = "chat_session"
    
    session_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_title = Column(String(200), default="New Conversation")
    started_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

class ChatMessage(Base):
    __tablename__ = "chat_message"
    
    message_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_session.session_id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    attachments = Column(Text, nullable=True)  # JSON array of file URLs
    extra_info = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)