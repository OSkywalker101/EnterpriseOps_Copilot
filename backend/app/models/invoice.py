import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Index, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    MATCHED = "matched"
    DISCREPANCY = "discrepancy"
    APPROVED = "approved"
    PAID = "paid"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PARTIAL = "partial"
    PAID = "paid"


class SupplierInvoice(Base):
    __tablename__ = "supplier_invoices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False, index=True)
    purchase_order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("purchase_orders.id"), nullable=True, index=True)
    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    invoice_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.UNPAID, nullable=False)
    paid_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    supplier: Mapped["Supplier"] = relationship(back_populates="invoices")
    purchase_order: Mapped[Optional["PurchaseOrder"]] = relationship(back_populates="invoices")
    lines: Mapped[List["SupplierInvoiceLine"]] = relationship(back_populates="invoice", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_invoice_supplier_date_status", "supplier_id", "invoice_date", "status"), Index("ix_invoice_due_date", "due_date"),)


class SupplierInvoiceLine(Base):
    __tablename__ = "supplier_invoice_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("supplier_invoices.id"), nullable=False, index=True)
    po_line_id: Mapped[Optional[int]] = mapped_column(ForeignKey("purchase_order_lines.id"), nullable=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_invoiced: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    line_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    invoice: Mapped["SupplierInvoice"] = relationship(back_populates="lines")
    po_line: Mapped[Optional["PurchaseOrderLine"]] = relationship(back_populates="invoice_lines")
    product: Mapped["Product"] = relationship(back_populates="invoice_lines")

    __table_args__ = (Index("ix_invoice_line_po_line", "po_line_id"),)
