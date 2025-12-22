from fastapi import FastAPI, Depends, HTTPException, Query, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, List
import jwt
import os

import models
import schemas
import crud

# ============================================================================
# CONFIGURATION & AUTHENTICATION
# ============================================================================

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Verify JWT token and extract user information"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user_id(token_payload: dict = Depends(verify_token)) -> int:
    """Extract user ID from verified token"""
    user_id = token_payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return user_id

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Medical Service",
    description="API for managing Doctors, Hospitals, and Medical Records",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    """Initialize database on application startup"""
    models.Base.metadata.create_all(bind=models.engine)
    print("✅ Medical Service started successfully")

@app.get("/")
def health_check():
    return {"service": "Medical Service", "status": "running"}

# ============================================================================
# DOCTOR ENDPOINTS
# ============================================================================

@app.post("/doctors", response_model=schemas.DoctorResponse, status_code=201)
def create_doctor(
    doctor: schemas.DoctorCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    # Check if doctor profile already exists
    if crud.get_doctor_by_user_id(db, doctor.user_id):
        raise HTTPException(status_code=400, detail="Doctor profile already exists")
    
    # Ensure user is creating their own profile
    if doctor.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only create your own profile")
    
    return crud.create_doctor(db, doctor)

@app.get("/doctors", response_model=schemas.DoctorList)
def list_doctors(
    specialization: Optional[str] = None,
    hospital_id: Optional[int] = None,
    is_available_online: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(models.get_db)
):
    doctors = crud.get_doctors(db, specialization, hospital_id, is_available_online, skip, limit)
    total = crud.count_doctors(db, specialization, hospital_id)
    return {"total": total, "doctors": doctors}

@app.get("/doctors/{doctor_id}", response_model=schemas.DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(models.get_db)):
    doctor = crud.get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@app.put("/doctors/{doctor_id}", response_model=schemas.DoctorResponse)
def update_doctor(
    doctor_id: int,
    doctor_update: schemas.DoctorUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    doctor = crud.get_doctor_by_id(db, doctor_id)
    if not doctor or doctor.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    return crud.update_doctor(db, doctor_id, doctor_update)

# ============================================================================
# HOSPITAL ENDPOINTS
# ============================================================================

@app.post("/hospitals", response_model=schemas.HospitalResponse, status_code=201)
def create_hospital(hospital: schemas.HospitalCreate, db: Session = Depends(models.get_db)):
    return crud.create_hospital(db, hospital)

@app.get("/hospitals", response_model=schemas.HospitalList)
def list_hospitals(
    city: Optional[str] = None,
    has_emergency: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(models.get_db)
):
    hospitals = crud.get_hospitals(db, city, has_emergency, skip=skip, limit=limit)
    total = crud.count_hospitals(db, city, has_emergency)
    return {"total": total, "hospitals": hospitals}

@app.get("/hospitals/{hospital_id}", response_model=schemas.HospitalResponse)
def get_hospital(hospital_id: int, db: Session = Depends(models.get_db)):
    hospital = crud.get_hospital_by_id(db, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital

# ============================================================================
# MEDICAL RECORD ENDPOINTS
# ============================================================================

@app.post("/medical-records", response_model=schemas.MedicalRecordResponse, status_code=201)
def create_medical_record(
    record: schemas.MedicalRecordCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    # Verify current user is a doctor
    doctor_profile = crud.get_doctor_by_user_id(db, current_user_id)
    if not doctor_profile or record.doctor_id != doctor_profile.doctor_id:
        raise HTTPException(status_code=403, detail="Only the attending doctor can create this record")
    
    return crud.create_medical_record(db, record)

@app.get("/medical-records/my-records", response_model=schemas.MedicalRecordList)
def get_my_records(
    current_user_id: int = Depends(get_current_user_id),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(models.get_db)
):
    records = crud.get_user_medical_records(db, current_user_id, skip, limit)
    total = crud.count_user_medical_records(db, current_user_id)
    return {"total": total, "records": records}

@app.get("/medical-records/{record_id}", response_model=schemas.MedicalRecordResponse)
def get_record(
    record_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    # Users can only see their own records
    record = crud.get_medical_record_by_id(db, record_id, current_user_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found or access denied")
    return record

@app.put("/medical-records/{record_id}", response_model=schemas.MedicalRecordResponse)
def update_medical_record(
    record_id: int,
    record_update: schemas.MedicalRecordUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    doctor_profile = crud.get_doctor_by_user_id(db, current_user_id)
    if not doctor_profile:
        raise HTTPException(status_code=403, detail="Only doctors can update records")
        
    updated = crud.update_medical_record(db, record_id, doctor_profile.doctor_id, record_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Record not found or unauthorized")
    return updated

@app.delete("/medical-records/{record_id}", status_code=204)
def delete_medical_record(
    record_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(models.get_db)
):
    doctor_profile = crud.get_doctor_by_user_id(db, current_user_id)
    if not doctor_profile:
        raise HTTPException(status_code=403, detail="Action forbidden")
        
    if not crud.delete_medical_record(db, record_id, doctor_profile.doctor_id):
        raise HTTPException(status_code=404, detail="Record not found")
    return None