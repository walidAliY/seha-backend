from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
from typing import Optional, List
import models
import schemas


# ============================================================================
# DOCTOR CRUD OPERATIONS
# ============================================================================

def create_doctor(db: Session, doctor: schemas.DoctorCreate):
    """Create a new doctor"""
    db_doctor = models.Doctor(
        user_id=doctor.user_id,
        specialization=doctor.specialization,
        license_number=doctor.license_number,
        hospital_id=doctor.hospital_id,
        qualifications=doctor.qualifications,
        years_experience=doctor.years_experience,
        availability_schedule=doctor.availability_schedule,
        is_available_online=doctor.is_available_online
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def get_doctor_by_id(db: Session, doctor_id: int):
    """Get doctor by ID"""
    return db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()


def get_doctor_by_user_id(db: Session, user_id: int):
    """Get doctor by user ID"""
    return db.query(models.Doctor).filter(models.Doctor.user_id == user_id).first()


def get_doctors(
    db: Session,
    specialization: Optional[str] = None,
    hospital_id: Optional[int] = None,
    is_available_online: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get list of doctors with optional filters"""
    query = db.query(models.Doctor)
    
    if specialization:
        query = query.filter(models.Doctor.specialization.ilike(f"%{specialization}%"))
    
    if hospital_id:
        query = query.filter(models.Doctor.hospital_id == hospital_id)
    
    if is_available_online is not None:
        query = query.filter(models.Doctor.is_available_online == is_available_online)
    
    return query.offset(skip).limit(limit).all()


def update_doctor(db: Session, doctor_id: int, doctor_update: schemas.DoctorUpdate):
    """Update doctor information"""
    db_doctor = get_doctor_by_id(db, doctor_id)
    
    if not db_doctor:
        return None
    
    update_data = doctor_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_doctor, field, value)
    
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def delete_doctor(db: Session, doctor_id: int):
    """Delete a doctor"""
    db_doctor = get_doctor_by_id(db, doctor_id)
    
    if not db_doctor:
        return False
    
    db.delete(db_doctor)
    db.commit()
    return True


def count_doctors(
    db: Session,
    specialization: Optional[str] = None,
    hospital_id: Optional[int] = None
):
    """Count doctors with optional filters"""
    query = db.query(models.Doctor)
    
    if specialization:
        query = query.filter(models.Doctor.specialization.ilike(f"%{specialization}%"))
    
    if hospital_id:
        query = query.filter(models.Doctor.hospital_id == hospital_id)
    
    return query.count()


# ============================================================================
# HOSPITAL CRUD OPERATIONS
# ============================================================================

def create_hospital(db: Session, hospital: schemas.HospitalCreate):
    """Create a new hospital"""
    db_hospital = models.Hospital(
        name=hospital.name,
        address=hospital.address,
        city=hospital.city,
        phone=hospital.phone,
        latitude=hospital.latitude,
        longitude=hospital.longitude,
        departments=hospital.departments,
        working_hours=hospital.working_hours,
        has_emergency=hospital.has_emergency,
        is_government=hospital.is_government
    )
    db.add(db_hospital)
    db.commit()
    db.refresh(db_hospital)
    return db_hospital


def get_hospital_by_id(db: Session, hospital_id: int):
    """Get hospital by ID"""
    return db.query(models.Hospital).filter(models.Hospital.hospital_id == hospital_id).first()


def get_hospitals(
    db: Session,
    city: Optional[str] = None,
    has_emergency: Optional[bool] = None,
    is_government: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get list of hospitals with optional filters"""
    query = db.query(models.Hospital)
    
    if city:
        query = query.filter(models.Hospital.city.ilike(f"%{city}%"))
    
    if has_emergency is not None:
        query = query.filter(models.Hospital.has_emergency == has_emergency)
    
    if is_government is not None:
        query = query.filter(models.Hospital.is_government == is_government)
    
    return query.offset(skip).limit(limit).all()


def search_hospitals_by_name(db: Session, name: str):
    """Search hospitals by name"""
    return db.query(models.Hospital).filter(
        models.Hospital.name.ilike(f"%{name}%")
    ).all()


def update_hospital(db: Session, hospital_id: int, hospital_update: schemas.HospitalUpdate):
    """Update hospital information"""
    db_hospital = get_hospital_by_id(db, hospital_id)
    
    if not db_hospital:
        return None
    
    update_data = hospital_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_hospital, field, value)
    
    db.commit()
    db.refresh(db_hospital)
    return db_hospital


def delete_hospital(db: Session, hospital_id: int):
    """Delete a hospital"""
    db_hospital = get_hospital_by_id(db, hospital_id)
    
    if not db_hospital:
        return False
    
    db.delete(db_hospital)
    db.commit()
    return True


def count_hospitals(
    db: Session,
    city: Optional[str] = None,
    has_emergency: Optional[bool] = None
):
    """Count hospitals with optional filters"""
    query = db.query(models.Hospital)
    
    if city:
        query = query.filter(models.Hospital.city.ilike(f"%{city}%"))
    
    if has_emergency is not None:
        query = query.filter(models.Hospital.has_emergency == has_emergency)
    
    return query.count()


# ============================================================================
# MEDICAL RECORD CRUD OPERATIONS
# ============================================================================

def create_medical_record(db: Session, record: schemas.MedicalRecordCreate):
    """Create a new medical record"""
    db_record = models.MedicalRecord(
        user_id=record.user_id,
        appointment_id=record.appointment_id,
        doctor_id=record.doctor_id,
        diagnosis=record.diagnosis,
        prescription=record.prescription,
        tests_ordered=record.tests_ordered,
        doctor_notes=record.doctor_notes,
        visit_date=record.visit_date
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def get_medical_record_by_id(db: Session, record_id: int, user_id: int):
    """Get medical record by ID (only if belongs to user)"""
    return db.query(models.MedicalRecord).filter(
        and_(
            models.MedicalRecord.record_id == record_id,
            models.MedicalRecord.user_id == user_id
        )
    ).first()


def get_user_medical_records(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
):
    """Get all medical records for a specific user"""
    return db.query(models.MedicalRecord).filter(
        models.MedicalRecord.user_id == user_id
    ).order_by(models.MedicalRecord.visit_date.desc()).offset(skip).limit(limit).all()


def get_doctor_medical_records(
    db: Session,
    doctor_id: int,
    skip: int = 0,
    limit: int = 100
):
    """Get all medical records created by a specific doctor"""
    return db.query(models.MedicalRecord).filter(
        models.MedicalRecord.doctor_id == doctor_id
    ).order_by(models.MedicalRecord.visit_date.desc()).offset(skip).limit(limit).all()


def update_medical_record(
    db: Session,
    record_id: int,
    doctor_id: int,
    record_update: schemas.MedicalRecordUpdate
):
    """Update medical record (only by the doctor who created it)"""
    db_record = db.query(models.MedicalRecord).filter(
        and_(
            models.MedicalRecord.record_id == record_id,
            models.MedicalRecord.doctor_id == doctor_id
        )
    ).first()
    
    if not db_record:
        return None
    
    update_data = record_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record


def delete_medical_record(db: Session, record_id: int, doctor_id: int):
    """Delete medical record (only by the doctor who created it)"""
    db_record = db.query(models.MedicalRecord).filter(
        and_(
            models.MedicalRecord.record_id == record_id,
            models.MedicalRecord.doctor_id == doctor_id
        )
    ).first()
    
    if not db_record:
        return False
    
    db.delete(db_record)
    db.commit()
    return True


def count_user_medical_records(db: Session, user_id: int):
    """Count medical records for a user"""
    return db.query(models.MedicalRecord).filter(
        models.MedicalRecord.user_id == user_id
    ).count()
