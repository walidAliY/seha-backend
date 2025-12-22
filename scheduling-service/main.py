from fastapi import FastAPI, Depends, HTTPException, Query, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import jwt
import os

import models
import schemas
import crud

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Verify JWT token and extract user information
    This should match the implementation in ../shared/auth.py
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user_id(token_payload: dict = Security(verify_token)) -> int:
    """Extract user ID from verified token"""
    user_id = token_payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return user_id


# Create FastAPI application
app = FastAPI(
    title="Scheduling Service",
    description="Appointment booking and management service",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():
    """Initialize database on application startup"""
    models.Base.metadata.create_all(bind=models.engine)
    print("✅ Scheduling Service started successfully")


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "service": "Scheduling Service",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/appointments", response_model=schemas.AppointmentResponse, status_code=201)
def create_appointment(
    appointment: schemas.AppointmentCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    """
    Create a new appointment
    
    - **doctor_id**: ID of the doctor to book with
    - **hospital_id**: ID of the hospital location
    - **appointment_datetime**: Date and time of appointment
    - **reason_for_visit**: Optional reason for visit
    - **patient_notes**: Optional notes from patient
    """
    # Check if appointment datetime is in the future
    if appointment.appointment_datetime < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Appointment datetime must be in the future"
        )
    
    # Create appointment
    db_appointment = crud.create_appointment(db, appointment, current_user_id)
    return db_appointment


@app.get("/appointments", response_model=schemas.AppointmentList)
def list_appointments(
    status: Optional[str] = Query(None, description="Filter by status (scheduled/completed/cancelled)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    """
    Get all appointments for the current user
    
    - **status**: Optional filter by appointment status
    - **skip**: Pagination offset
    - **limit**: Maximum number of results
    """
    # Validate status if provided
    if status and status not in ["scheduled", "completed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Must be: scheduled, completed, or cancelled"
        )
    
    # Get appointments
    appointments = crud.get_user_appointments(db, current_user_id, status, skip, limit)
    total = crud.count_user_appointments(db, current_user_id, status)
    
    return {
        "total": total,
        "appointments": appointments
    }


@app.get("/appointments/{appointment_id}", response_model=schemas.AppointmentResponse)
def get_appointment(
    appointment_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    """
    Get a specific appointment by ID
    
    - **appointment_id**: ID of the appointment to retrieve
    """
    appointment = crud.get_appointment_by_id(db, appointment_id, current_user_id)
    
    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    return appointment


@app.put("/appointments/{appointment_id}", response_model=schemas.AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_update: schemas.AppointmentUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    """
    Update an existing appointment
    
    - **appointment_id**: ID of the appointment to update
    - Only provided fields will be updated
    """
    # Validate status if provided
    if appointment_update.status and appointment_update.status not in ["scheduled", "completed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid status. Must be: scheduled, completed, or cancelled"
        )
    
    # Check if appointment datetime is in the future (if being updated)
    if appointment_update.appointment_datetime:
        if appointment_update.appointment_datetime < datetime.utcnow():
            raise HTTPException(
                status_code=400,
                detail="Appointment datetime must be in the future"
            )
    
    # Update appointment
    updated_appointment = crud.update_appointment(
        db, appointment_id, current_user_id, appointment_update
    )
    
    if not updated_appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    return updated_appointment


@app.patch("/appointments/{appointment_id}/cancel", response_model=schemas.AppointmentResponse)
def cancel_appointment(
    appointment_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    """
    Cancel an appointment (changes status to cancelled)
    
    - **appointment_id**: ID of the appointment to cancel
    """
    cancelled_appointment = crud.cancel_appointment(db, appointment_id, current_user_id)
    
    if not cancelled_appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    return cancelled_appointment


@app.delete("/appointments/{appointment_id}", status_code=204)
def delete_appointment(
    appointment_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    """
    Permanently delete an appointment
    
    - **appointment_id**: ID of the appointment to delete
    """
    deleted = crud.delete_appointment(db, appointment_id, current_user_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )
    
    return None


@app.get("/doctors/{doctor_id}/appointments", response_model=List[schemas.AppointmentResponse])
def get_doctor_appointments(
    doctor_id: int,
    date: Optional[datetime] = Query(None, description="Filter by specific date"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    """
    Get all appointments for a specific doctor
    Useful for doctors to view their schedule
    
    - **doctor_id**: ID of the doctor
    - **date**: Optional filter by specific date
    - **status**: Optional filter by status
    """
    appointments = crud.get_doctor_appointments(db, doctor_id, date, status)
    return appointments


@app.get("/appointments/upcoming/count")
def count_upcoming_appointments(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    """
    Get count of upcoming scheduled appointments for current user
    """
    count = crud.count_user_appointments(db, current_user_id, status="scheduled")
    return {"upcoming_appointments": count}

