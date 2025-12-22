from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, create_engine, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Create base class for declarative models
Base = declarative_base()

# Database URL from environment variable or default to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medical.db")

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


class Doctor(Base):
    """
    Doctor Model - Stores doctor information
    
    Relationships:
    - Belongs to a USER (user_id) from auth-service
    - Belongs to a HOSPITAL (hospital_id)
    """
    __tablename__ = "doctors"

    # Primary Key
    doctor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key to User
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    
    # Doctor Information
    specialization = Column(String(100), nullable=False, index=True)
    license_number = Column(String(100), unique=True, nullable=False)
    hospital_id = Column(Integer, nullable=False, index=True)
    qualifications = Column(Text)  # Degrees, certifications
    years_experience = Column(Integer)
    profile_picture = Column(String(500))  # MinIO URL
    availability_schedule = Column(Text)  # JSON string of schedule
    is_available_online = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class Hospital(Base):
    """
    Hospital Model - Stores hospital/clinic information
    """
    __tablename__ = "hospitals"

    # Primary Key
    hospital_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Hospital Information
    name = Column(String(200), nullable=False, index=True)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False, index=True)
    phone = Column(String(20))
    
    # Location
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Media
    image = Column(String(500))  # MinIO URL for hospital image
    logo = Column(String(500))  # MinIO URL for logo
    
    # Hospital Details
    departments = Column(Text)  # JSON string of departments list
    working_hours = Column(String(200))  # e.g., "Mon-Fri: 8AM-8PM"
    has_emergency = Column(Boolean, default=False)
    is_government = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class MedicalRecord(Base):
    """
    Medical Record Model - Stores patient medical records
    
    Relationships:
    - Belongs to a USER/Patient (user_id)
    - Created by a DOCTOR (doctor_id)
    - Related to an APPOINTMENT (appointment_id)
    """
    __tablename__ = "medical_records"

    # Primary Key
    record_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(Integer, nullable=False, index=True)  # Patient
    appointment_id = Column(Integer, index=True)  # Optional - can be null
    doctor_id = Column(Integer, nullable=False, index=True)  # Doctor who created
    
    # Medical Information
    diagnosis = Column(String(500), nullable=False)
    prescription = Column(Text)  # Medications prescribed
    tests_ordered = Column(Text)  # Lab tests, imaging, etc.
    doctor_notes = Column(Text)  # Additional notes from doctor
    attachments = Column(Text)  # JSON array of file URLs in MinIO
    
    # Date Information
    visit_date = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)