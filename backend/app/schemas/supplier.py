from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.supplier import SupplierStatus


class SupplierBase(BaseModel):
    supplier_code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    contact_name: Optional[str] = Field(default=None, max_length=255)
    contact_email: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    status: SupplierStatus = SupplierStatus.ACTIVE
    lead_time_days: int = Field(default=0, ge=0)
    payment_terms_days: int = Field(default=30, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    notes: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    contact_name: Optional[str] = Field(default=None, max_length=255)
    contact_email: Optional[str] = Field(default=None, max_length=255)
    contact_phone: Optional[str] = Field(default=None, max_length=50)
    address: Optional[str] = None
    status: Optional[SupplierStatus] = None
    lead_time_days: Optional[int] = Field(default=None, ge=0)
    payment_terms_days: Optional[int] = Field(default=None, ge=0)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=3)
    notes: Optional[str] = None


class SupplierResponse(SupplierBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class SupplierSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    supplier_code: str
    name: str
    status: SupplierStatus
    lead_time_days: int