from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

# Explicitly setting the bcrypt backend to avoid the '__about__' attribute error
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Hashes the password using Bcrypt. 
    Note: Bcrypt has a 72-character limit, so we truncate to ensure it never crashes.
    """
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies the plain password against the stored hash.
    """
    return pwd_context.verify(plain_password[:72], hashed_password)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        full_name=user.full_name,
        phone=user.phone,
        date_of_birth=user.date_of_birth,
        gender=user.gender,
        address=user.address,
        user_type=user.user_type
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    # model_dump is used for Pydantic v2 compatibility
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user