import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Index, Numeric, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


class PurchaseOrderStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ORDERED = "ordered"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class RequisitionStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED_TO_PO = "converted_to_po"


class PurchaseRequisition(Base):
    __tablename__ = "purchase_requisitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    requisition_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    requested_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[RequisitionStatus] = mapped_column(Enum(RequisitionStatus), default=RequisitionStatus.DRAFT, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    lines: Mapped[List["PurchaseOrderLine"]] = relationship(back_populates="requisition")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    po_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False, index=True)
    requisition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("purchase_requisitions.id"), nullable=True)
    status: Mapped[PurchaseOrderStatus] = mapped_column(Enum(PurchaseOrderStatus), default=PurchaseOrderStatus.DRAFT, nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    expected_delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_delivery_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    supplier: Mapped["Supplier"] = relationship(back_populates="purchase_orders")
    lines: Mapped[List["PurchaseOrderLine"]] = relationship(back_populates="purchase_order", cascade="all, delete-orphan")
    receipts: Mapped[List["GoodsReceipt"]] = relationship(back_populates="purchase_order")
    invoices: Mapped[List["SupplierInvoice"]] = relationship(back_populates="purchase_order")
    approval_records: Mapped[List["ApprovalRecord"]] = relationship(back_populates="purchase_order")
    requisition: Mapped[Optional["PurchaseRequisition"]] = relationship()

    __table_args__ = (Index("ix_po_status_supplier_date", "status", "supplier_id", "order_date"), Index("ix_po_expected_delivery", "expected_delivery_date"),)


class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    purchase_order_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False, index=True)
    requisition_id: Mapped[Optional[int]] = mapped_column(ForeignKey("purchase_requisitions.id"), nullable=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_ordered: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_received: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    line_total: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    purchase_order: Mapped["PurchaseOrder"] = relationship(back_populates="lines")
    product: Mapped["Product"] = relationship(back_populates="po_lines")
    requisition: Mapped[Optional["PurchaseRequisition"]] = relationship(back_populates="lines")
    gr_lines: Mapped[List["GoodsReceiptLine"]] = relationship(back_populates="po_line")
    invoice_lines: Mapped[List["SupplierInvoiceLine"]] = relationship(back_populates="po_line")

    __table_args__ = (UniqueConstraint("purchase_order_id", "line_number", name="uq_po_line_number"),)


class ApprovalRecord(Base):
    __tablename__ = "approval_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    purchase_order_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False, index=True)
    approver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # approved, rejected, requested_changes
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    purchase_order: Mapped["PurchaseOrder"] = relationship(back_populates="approval_records")
    approver: Mapped["User"] = relationship(back_populates="approval_records")

    __table_args__ = (Index("ix_approval_po_approver", "purchase_order_id", "approver_id"),)
