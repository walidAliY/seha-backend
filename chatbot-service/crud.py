from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from models import ChatSession, ChatMessage
from schemas import SessionCreate, MessageCreate

# ==================== CHAT SESSION CRUD ====================

def create_session(db: Session, user_id: int, session_data: SessionCreate) -> ChatSession:
    """Create a new chat session"""
    new_session = ChatSession(
        user_id=user_id,
        session_title=session_data.session_title
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def get_user_sessions(db: Session, user_id: int) -> List[ChatSession]:
    """Get all active sessions for a user"""
    return db.query(ChatSession).filter(
        ChatSession.user_id == user_id,
        ChatSession.is_active == True
    ).order_by(ChatSession.last_message_at.desc()).all()

def get_session_by_id(db: Session, session_id: int, user_id: int) -> Optional[ChatSession]:
    """Get a specific session by ID"""
    return db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == user_id
    ).first()

def delete_session(db: Session, session_id: int, user_id: int) -> bool:
    """Soft delete a session"""
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == user_id
    ).first()
    
    if not session:
        return False
    
    session.is_active = False
    db.commit()
    return True

def update_session_last_message(db: Session, session_id: int):
    """Update the last message timestamp"""
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).first()
    
    if session:
        session.last_message_at = datetime.utcnow()
        db.commit()

def update_session_title(db: Session, session_id: int, title: str):
    """Update session title"""
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).first()
    
    if session:
        session.session_title = title
        db.commit()

# ==================== CHAT MESSAGE CRUD ====================

def create_message(
    db: Session, 
    session_id: int, 
    role: str, 
    content: str,
    attachments: Optional[List[str]] = None,
    metadata: Optional[str] = None
) -> ChatMessage:
    """Create a new chat message"""
    new_message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        attachments=str(attachments) if attachments else None,
        metadata=metadata
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_session_messages(db: Session, session_id: int) -> List[ChatMessage]:
    """Get all messages in a session"""
    return db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()

def get_conversation_history(db: Session, session_id: int) -> List[dict]:
    """Get conversation history formatted for chatbot"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]

def count_session_messages(db: Session, session_id: int) -> int:
    """Count messages in a session"""
    return db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).count()