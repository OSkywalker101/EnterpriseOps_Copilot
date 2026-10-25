from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.inventory import MovementType


class InventoryBalanceBase(BaseModel):
    product_id: int
    warehouse_id: int
    quantity_on_hand: int = Field(default=0, ge=0)
    reserved_quantity: int = Field(default=0, ge=0)


class InventoryBalanceCreate(InventoryBalanceBase):
    pass


class InventoryBalanceUpdate(BaseModel):
    quantity_on_hand: Optional[int] = Field(default=None, ge=0)
    reserved_quantity: Optional[int] = Field(default=None, ge=0)


class InventoryBalanceResponse(InventoryBalanceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    last_movement_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    available_quantity: int


class InventoryMovementBase(BaseModel):
    product_id: int
    warehouse_id: int
    movement_type: MovementType
    quantity: int = Field(ge=1)
    reference_type: Optional[str] = Field(default=None, max_length=50)
    reference_id: Optional[int] = None
    notes: Optional[str] = None


class InventoryMovementCreate(InventoryMovementBase):
    pass


class InventoryMovementResponse(InventoryMovementBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    created_by: Optional[int] = None


class LowStockItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    product_sku: str
    product_name: str
    warehouse_id: int
    warehouse_code: str
    quantity_on_hand: int
    reserved_quantity: int
    available_quantity: int
    reorder_level: int