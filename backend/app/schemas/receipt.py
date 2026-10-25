from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class GoodsReceiptLineBase(BaseModel):
    po_line_id: int
    product_id: int
    quantity_received: int = Field(ge=1)
    quantity_accepted: int = Field(ge=0)
    quantity_rejected: int = Field(default=0, ge=0)
    notes: Optional[str] = None


class GoodsReceiptLineCreate(GoodsReceiptLineBase):
    pass


class GoodsReceiptLineResponse(GoodsReceiptLineBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    goods_receipt_id: int
    created_at: datetime


class GoodsReceiptBase(BaseModel):
    gr_number: str = Field(min_length=1, max_length=50)
    purchase_order_id: int
    warehouse_id: int
    received_by: int
    receipt_date: datetime
    notes: Optional[str] = None


class GoodsReceiptCreate(GoodsReceiptBase):
    lines: List[GoodsReceiptLineCreate] = Field(min_length=1)


class GoodsReceiptUpdate(BaseModel):
    notes: Optional[str] = None


class GoodsReceiptResponse(GoodsReceiptBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    lines: List[GoodsReceiptLineResponse] = []