from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from dotenv import load_dotenv

import models, schemas, crud
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================
# Synchronized with Medical/Scheduling services to prevent 401 errors
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database setup
DATABASE_URL = os.getenv("AUTH_DATABASE_URL", "sqlite:///./auth.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service", version="1.0.0")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# JWT FUNCTIONS
# ============================================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if email is None or user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email, user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# ============================================================================
# ROUTES
# ============================================================================

@app.get("/")
def read_root():
    return {
        "service": "Auth Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = crud.create_user(db, user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email, "user_id": new_user.user_id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }

@app.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.user_id},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    return current_user

# UPDATED: Changed from POST to GET to fix 405 Method Not Allowed errors
@app.get("/verify-token")
def verify_token(current_user: models.User = Depends(get_current_user)):
    """Endpoint for other services to verify JWT tokens"""
    return {
        "valid": True,
        "user_id": current_user.user_id,
        "email": current_user.email,
        "user_type": current_user.user_type
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)