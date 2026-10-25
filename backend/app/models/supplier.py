import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, Enum, Integer, Index, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


class SupplierStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_HOLD = "on_hold"


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    supplier_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[SupplierStatus] = mapped_column(Enum(SupplierStatus), default=SupplierStatus.ACTIVE, nullable=False)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    payment_terms_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    purchase_orders: Mapped[List["PurchaseOrder"]] = relationship(back_populates="supplier")
    invoices: Mapped[List["SupplierInvoice"]] = relationship(back_populates="supplier")

    __table_args__ = (Index("ix_suppliers_status_code", "status", "supplier_code"),)
