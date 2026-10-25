from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    gr_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    purchase_order_id: Mapped[int] = mapped_column(ForeignKey("purchase_orders.id"), nullable=False, index=True)
    receipt_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)
    received_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    purchase_order: Mapped["PurchaseOrder"] = relationship(back_populates="receipts")
    lines: Mapped[List["GoodsReceiptLine"]] = relationship(back_populates="goods_receipt", cascade="all, delete-orphan")


class GoodsReceiptLine(Base):
    __tablename__ = "goods_receipt_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    goods_receipt_id: Mapped[int] = mapped_column(ForeignKey("goods_receipts.id"), nullable=False, index=True)
    po_line_id: Mapped[int] = mapped_column(ForeignKey("purchase_order_lines.id"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity_received: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_accepted: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_rejected: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    goods_receipt: Mapped["GoodsReceipt"] = relationship(back_populates="lines")
    po_line: Mapped["PurchaseOrderLine"] = relationship(back_populates="gr_lines")
    product: Mapped["Product"] = relationship(back_populates="gr_lines")

    __table_args__ = (Index("ix_gr_line_po_line", "po_line_id"),)
