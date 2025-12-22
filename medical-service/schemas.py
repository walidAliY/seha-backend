from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List


# ============================================================================
# DOCTOR SCHEMAS
# ============================================================================

class DoctorBase(BaseModel):
    """Base schema with common doctor fields"""
    specialization: str = Field(..., max_length=100)
    license_number: str = Field(..., max_length=100)
    hospital_id: int
    qualifications: Optional[str] = None
    years_experience: Optional[int] = Field(None, ge=0)
    availability_schedule: Optional[str] = None
    is_available_online: bool = False


class DoctorCreate(DoctorBase):
    """Schema for creating a new doctor"""
    user_id: int  # Must provide user_id when creating doctor


class DoctorUpdate(BaseModel):
    """Schema for updating doctor information"""
    specialization: Optional[str] = Field(None, max_length=100)
    hospital_id: Optional[int] = None
    qualifications: Optional[str] = None
    years_experience: Optional[int] = Field(None, ge=0)
    availability_schedule: Optional[str] = None
    is_available_online: Optional[bool] = None
    profile_picture: Optional[str] = None


class DoctorResponse(DoctorBase):
    """Schema for doctor response"""
    doctor_id: int
    user_id: int
    profile_picture: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DoctorList(BaseModel):
    """Schema for listing multiple doctors"""
    total: int
    doctors: List[DoctorResponse]


# ============================================================================
# HOSPITAL SCHEMAS
# ============================================================================

class HospitalBase(BaseModel):
    """Base schema with common hospital fields"""
    name: str = Field(..., max_length=200)
    address: str
    city: str = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    departments: Optional[str] = None  # JSON string
    working_hours: Optional[str] = Field(None, max_length=200)
    has_emergency: bool = False
    is_government: bool = False


class HospitalCreate(HospitalBase):
    """Schema for creating a new hospital"""
    pass


class HospitalUpdate(BaseModel):
    """Schema for updating hospital information"""
    name: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image: Optional[str] = None
    logo: Optional[str] = None
    departments: Optional[str] = None
    working_hours: Optional[str] = Field(None, max_length=200)
    has_emergency: Optional[bool] = None
    is_government: Optional[bool] = None


class HospitalResponse(HospitalBase):
    """Schema for hospital response"""
    hospital_id: int
    image: Optional[str] = None
    logo: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class HospitalList(BaseModel):
    """Schema for listing multiple hospitals"""
    total: int
    hospitals: List[HospitalResponse]


# ============================================================================
# MEDICAL RECORD SCHEMAS
# ============================================================================

class MedicalRecordBase(BaseModel):
    """Base schema with common medical record fields"""
    diagnosis: str = Field(..., max_length=500)
    prescription: Optional[str] = None
    tests_ordered: Optional[str] = None
    doctor_notes: Optional[str] = None
    visit_date: datetime


class MedicalRecordCreate(MedicalRecordBase):
    """Schema for creating a new medical record"""
    user_id: int  # Patient ID
    appointment_id: Optional[int] = None
    doctor_id: int  # Doctor creating the record


class MedicalRecordUpdate(BaseModel):
    """Schema for updating medical record"""
    diagnosis: Optional[str] = Field(None, max_length=500)
    prescription: Optional[str] = None
    tests_ordered: Optional[str] = None
    doctor_notes: Optional[str] = None
    attachments: Optional[str] = None


class MedicalRecordResponse(MedicalRecordBase):
    """Schema for medical record response"""
    record_id: int
    user_id: int
    appointment_id: Optional[int] = None
    doctor_id: int
    attachments: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MedicalRecordList(BaseModel):
    """Schema for listing multiple medical records"""
    total: int
    records: List[MedicalRecordResponse]
