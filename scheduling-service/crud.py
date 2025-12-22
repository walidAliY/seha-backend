from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import Optional, List
import models
import schemas


def create_appointment(db: Session, appointment: schemas.AppointmentCreate, user_id: int):
    """
    Create a new appointment
    
    Args:
        db: Database session
        appointment: Appointment data from request
        user_id: ID of the user creating the appointment
    
    Returns:
        Created appointment object
    """
    db_appointment = models.Appointment(
        user_id=user_id,
        doctor_id=appointment.doctor_id,
        hospital_id=appointment.hospital_id,
        appointment_datetime=appointment.appointment_datetime,
        reason_for_visit=appointment.reason_for_visit,
        patient_notes=appointment.patient_notes,
        status="scheduled"
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def get_appointment_by_id(db: Session, appointment_id: int, user_id: int):
    """
    Get a specific appointment by ID
    Only returns if it belongs to the user
    
    Args:
        db: Database session
        appointment_id: ID of the appointment
        user_id: ID of the user requesting
    
    Returns:
        Appointment object or None
    """
    return db.query(models.Appointment).filter(
        and_(
            models.Appointment.appointment_id == appointment_id,
            models.Appointment.user_id == user_id
        )
    ).first()


def get_user_appointments(
    db: Session, 
    user_id: int, 
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Get all appointments for a user with optional filtering
    
    Args:
        db: Database session
        user_id: ID of the user
        status: Optional filter by status (scheduled/completed/cancelled)
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
    
    Returns:
        List of appointments
    """
    query = db.query(models.Appointment).filter(models.Appointment.user_id == user_id)
    
    # Apply status filter if provided
    if status:
        query = query.filter(models.Appointment.status == status)
    
    # Order by appointment date (newest first)
    query = query.order_by(models.Appointment.appointment_datetime.desc())
    
    return query.offset(skip).limit(limit).all()


def get_doctor_appointments(
    db: Session,
    doctor_id: int,
    date: Optional[datetime] = None,
    status: Optional[str] = None
):
    """
    Get all appointments for a specific doctor
    Used by doctors to see their schedule
    
    Args:
        db: Database session
        doctor_id: ID of the doctor
        date: Optional filter by specific date
        status: Optional filter by status
    
    Returns:
        List of appointments
    """
    query = db.query(models.Appointment).filter(models.Appointment.doctor_id == doctor_id)
    
    # Filter by date if provided
    if date:
        query = query.filter(
            and_(
                models.Appointment.appointment_datetime >= date,
                models.Appointment.appointment_datetime < date.replace(hour=23, minute=59, second=59)
            )
        )
    
    # Filter by status if provided
    if status:
        query = query.filter(models.Appointment.status == status)
    
    return query.order_by(models.Appointment.appointment_datetime.asc()).all()


def update_appointment(
    db: Session,
    appointment_id: int,
    user_id: int,
    appointment_update: schemas.AppointmentUpdate
):
    """
    Update an existing appointment
    
    Args:
        db: Database session
        appointment_id: ID of the appointment to update
        user_id: ID of the user (for authorization)
        appointment_update: New appointment data
    
    Returns:
        Updated appointment or None if not found
    """
    db_appointment = get_appointment_by_id(db, appointment_id, user_id)
    
    if not db_appointment:
        return None
    
    # Update only provided fields
    update_data = appointment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_appointment, field, value)
    
    db_appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def cancel_appointment(db: Session, appointment_id: int, user_id: int):
    """
    Cancel an appointment (soft delete - changes status to cancelled)
    
    Args:
        db: Database session
        appointment_id: ID of the appointment
        user_id: ID of the user
    
    Returns:
        Updated appointment or None
    """
    db_appointment = get_appointment_by_id(db, appointment_id, user_id)
    
    if not db_appointment:
        return None
    
    db_appointment.status = "cancelled"
    db_appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def delete_appointment(db: Session, appointment_id: int, user_id: int):
    """
    Permanently delete an appointment
    
    Args:
        db: Database session
        appointment_id: ID of the appointment
        user_id: ID of the user
    
    Returns:
        True if deleted, False if not found
    """
    db_appointment = get_appointment_by_id(db, appointment_id, user_id)
    
    if not db_appointment:
        return False
    
    db.delete(db_appointment)
    db.commit()
    return True


def count_user_appointments(db: Session, user_id: int, status: Optional[str] = None):
    """
    Count total appointments for a user
    
    Args:
        db: Database session
        user_id: ID of the user
        status: Optional filter by status
    
    Returns:
        Count of appointments
    """
    query = db.query(models.Appointment).filter(models.Appointment.user_id == user_id)
    
    if status:
        query = query.filter(models.Appointment.status == status)
    
    return query.count()