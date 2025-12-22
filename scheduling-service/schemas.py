from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AppointmentBase(BaseModel):
    """Base schema with common appointment fields"""
    doctor_id: int = Field(..., description="ID of the doctor")
    hospital_id: int = Field(..., description="ID of the hospital")
    appointment_datetime: datetime = Field(..., description="Date and time of appointment")
    reason_for_visit: Optional[str] = Field(None, max_length=200, description="Reason for visit")
    patient_notes: Optional[str] = Field(None, description="Additional notes from patient")


class AppointmentCreate(AppointmentBase):
    """Schema for creating a new appointment"""
    pass


class AppointmentUpdate(BaseModel):
    """Schema for updating an existing appointment"""
    appointment_datetime: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(scheduled|completed|cancelled)$")
    reason_for_visit: Optional[str] = Field(None, max_length=200)
    patient_notes: Optional[str] = None


class AppointmentResponse(AppointmentBase):
    """Schema for appointment response (includes all fields)"""
    appointment_id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allows ORM model to dict conversion


class AppointmentList(BaseModel):
    """Schema for listing multiple appointments"""
    total: int
    appointments: list[AppointmentResponse]
