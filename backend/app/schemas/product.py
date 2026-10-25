from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class WarehouseBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    address: Optional[str] = None
    is_active: bool = True


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    address: Optional[str] = None
    is_active: Optional[bool] = None


class WarehouseResponse(WarehouseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class ProductBase(BaseModel):
    sku: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    unit_of_measure: str = Field(default="EA", min_length=1, max_length=20)
    standard_cost: Optional[float] = Field(default=None, ge=0)
    reorder_level: int = Field(default=0, ge=0)
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    unit_of_measure: Optional[str] = Field(default=None, min_length=1, max_length=20)
    standard_cost: Optional[float] = Field(default=None, ge=0)
    reorder_level: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class ProductSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sku: str
    name: str
    unit_of_measure: str
    reorder_level: int