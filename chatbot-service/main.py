from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
import requests

from models import Base, ChatSession, ChatMessage
from schemas import SessionCreate, SessionResponse, MessageCreate, MessageResponse, ChatResponse
from crud import (
    create_session, get_user_sessions, get_session_by_id, delete_session,
    create_message, get_session_messages, get_conversation_history,
    update_session_last_message, update_session_title, count_session_messages
)
from chatbot_engine import ChatbotEngine

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Healthcare Chatbot Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot engine
chatbot_engine = ChatbotEngine()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth dependency
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split(" ")[1]
    
    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/verify-token",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth verification failed: {str(e)}")

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "service": "Healthcare Chatbot Service",
        "version": "1.0.0",
        "status": "operational"
    }

@app.post("/sessions", response_model=SessionResponse)
async def create_chat_session(
    session_data: SessionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    session = create_session(db, current_user["user_id"], session_data)
    return session

@app.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all chat sessions for current user"""
    sessions = get_user_sessions(db, current_user["user_id"])
    return sessions

@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat session"""
    session = get_session_by_id(db, session_id, current_user["user_id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    success = delete_session(db, session_id, current_user["user_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}

@app.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: int,
    message: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message and get chatbot response"""
    # Verify session
    session = get_session_by_id(db, session_id, current_user["user_id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Save user message
    user_message = create_message(
        db, session_id, "user", message.content, message.attachments
    )
    
    # Get conversation history
    history = get_conversation_history(db, session_id)
    
    # Get chatbot response
    try:
        bot_response = chatbot_engine.get_response(
            user_message=message.content,
            conversation_history=history,
            user_context={
                "user_id": current_user["user_id"],
                "user_type": current_user.get("user_type", "patient")
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")
    
    # Save assistant message
    assistant_message = create_message(db, session_id, "assistant", bot_response)
    
    # Update session
    update_session_last_message(db, session_id)
    
    # Auto-generate title from first message
    if session.session_title == "New Conversation" and count_session_messages(db, session_id) == 2:
        title = message.content[:50] + ("..." if len(message.content) > 50 else "")
        update_session_title(db, session_id, title)
    
    return {
        "user_message": user_message,
        "assistant_message": assistant_message
    }

@app.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages in a chat session"""
    session = get_session_by_id(db, session_id, current_user["user_id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = get_session_messages(db, session_id)
    return messages

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chatbot-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
