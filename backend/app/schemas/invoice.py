from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.invoice import InvoiceStatus, PaymentStatus


class SupplierInvoiceLineBase(BaseModel):
    po_line_id: Optional[int] = None
    product_id: int
    line_number: int = Field(ge=1)
    quantity_invoiced: int = Field(ge=1)
    unit_price: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    notes: Optional[str] = None


class SupplierInvoiceLineCreate(SupplierInvoiceLineBase):
    pass


class SupplierInvoiceLineResponse(SupplierInvoiceLineBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    invoice_id: int
    line_total: float
    created_at: datetime


class SupplierInvoiceBase(BaseModel):
    invoice_number: str = Field(min_length=1, max_length=50)
    supplier_id: int
    purchase_order_id: Optional[int] = None
    status: InvoiceStatus = InvoiceStatus.DRAFT
    invoice_date: datetime
    due_date: Optional[datetime] = None
    currency: str = Field(default="USD", min_length=3, max_length=3)
    notes: Optional[str] = None


class SupplierInvoiceCreate(SupplierInvoiceBase):
    lines: List[SupplierInvoiceLineCreate] = Field(min_length=1)


class SupplierInvoiceUpdate(BaseModel):
    status: Optional[InvoiceStatus] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class SupplierInvoiceResponse(SupplierInvoiceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    total_amount: float
    payment_status: PaymentStatus
    paid_amount: float
    created_at: datetime
    updated_at: datetime
    lines: List[SupplierInvoiceLineResponse] = []


class InvoiceMatchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    invoice_id: int
    invoice_number: str
    po_number: Optional[str] = None
    gr_number: Optional[str] = None
    quantity_match: bool
    amount_match: bool
    discrepancies: List[str] = []
    tolerance_applied: float = 0.0