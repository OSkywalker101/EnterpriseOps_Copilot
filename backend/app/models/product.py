from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    users: Mapped[List["User"]] = relationship(back_populates="warehouse")
    inventory_balances: Mapped[List["InventoryBalance"]] = relationship(back_populates="warehouse")
    inventory_movements: Mapped[List["InventoryMovement"]] = relationship(back_populates="warehouse")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unit_of_measure: Mapped[str] = mapped_column(String(20), default="EA", nullable=False)
    standard_cost: Mapped[Optional[float]] = mapped_column(Numeric(12, 4), nullable=True)
    reorder_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    inventory_balances: Mapped[List["InventoryBalance"]] = relationship(back_populates="product")
    inventory_movements: Mapped[List["InventoryMovement"]] = relationship(back_populates="product")
    po_lines: Mapped[List["PurchaseOrderLine"]] = relationship(back_populates="product")
    gr_lines: Mapped[List["GoodsReceiptLine"]] = relationship(back_populates="product")
    invoice_lines: Mapped[List["SupplierInvoiceLine"]] = relationship(back_populates="product")

    __table_args__ = (Index("ix_products_sku_active", "sku", "is_active"),)
