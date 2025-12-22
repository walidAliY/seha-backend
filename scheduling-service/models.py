from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Create base class for declarative models
Base = declarative_base()

# Database URL from environment variable or default to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./scheduling.db")

# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency function to get database session
    Automatically closes session after request
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Appointment(Base):
    """
    Appointment Model - Stores all appointment bookings
    
    Relationships:
    - Belongs to a USER (user_id)
    - Belongs to a DOCTOR (doctor_id)
    - Belongs to a HOSPITAL (hospital_id)
    
    Status Values: 'scheduled', 'completed', 'cancelled'
    """
    __tablename__ = "appointments"

    # Primary Key
    appointment_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys (references to other services)
    user_id = Column(Integer, nullable=False, index=True)  # Patient who booked
    doctor_id = Column(Integer, nullable=False, index=True)  # Doctor assigned
    hospital_id = Column(Integer, nullable=False, index=True)  # Hospital location
    
    # Appointment Details
    appointment_datetime = Column(DateTime, nullable=False)  # When the appointment is scheduled
    status = Column(String(50), default="scheduled")  # scheduled/completed/cancelled
    reason_for_visit = Column(String(200))  # Why patient is visiting
    patient_notes = Column(Text)  # Additional notes from patient
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)  # When appointment was created
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update
