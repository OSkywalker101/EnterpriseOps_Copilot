from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.procurement import PurchaseOrderStatus, RequisitionStatus, PurchaseRequisition


class PurchaseRequisitionBase(BaseModel):
    requisition_number: str = Field(min_length=1, max_length=50)
    requested_by: int
    status: RequisitionStatus = RequisitionStatus.DRAFT
    description: Optional[str] = None
    required_date: Optional[datetime] = None


class PurchaseRequisitionCreate(PurchaseRequisitionBase):
    pass


class PurchaseRequisitionUpdate(BaseModel):
    status: Optional[RequisitionStatus] = None
    description: Optional[str] = None
    required_date: Optional[datetime] = None


class PurchaseRequisitionResponse(PurchaseRequisitionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class PurchaseOrderLineBase(BaseModel):
    product_id: int
    line_number: int = Field(ge=1)
    quantity_ordered: int = Field(ge=1)
    unit_price: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    notes: Optional[str] = None


class PurchaseOrderLineCreate(PurchaseOrderLineBase):
    pass


class PurchaseOrderLineUpdate(BaseModel):
    quantity_ordered: Optional[int] = Field(default=None, ge=1)
    unit_price: Optional[float] = Field(default=None, gt=0)
    notes: Optional[str] = None


class PurchaseOrderLineResponse(PurchaseOrderLineBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    purchase_order_id: int
    requisition_id: Optional[int] = None
    quantity_received: int
    line_total: float
    created_at: datetime
    updated_at: datetime


class PurchaseOrderBase(BaseModel):
    po_number: str = Field(min_length=1, max_length=50)
    supplier_id: int
    requisition_id: Optional[int] = None
    status: PurchaseOrderStatus = PurchaseOrderStatus.DRAFT
    expected_delivery_date: Optional[datetime] = None
    currency: str = Field(default="USD", min_length=3, max_length=3)
    notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    lines: List[PurchaseOrderLineCreate] = Field(min_length=1)


class PurchaseOrderUpdate(BaseModel):
    status: Optional[PurchaseOrderStatus] = None
    expected_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None


class PurchaseOrderResponse(PurchaseOrderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_date: datetime
    actual_delivery_date: Optional[datetime] = None
    total_amount: float
    created_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    lines: List[PurchaseOrderLineResponse] = []


class ApprovalRecordBase(BaseModel):
    purchase_order_id: int
    approver_id: int
    action: str
    comments: Optional[str] = None


class ApprovalRecordCreate(ApprovalRecordBase):
    pass


class ApprovalRecordResponse(ApprovalRecordBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime