import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Index, Numeric, Text, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


class MovementType(str, enum.Enum):
    RECEIPT = "receipt"
    ISSUE = "issue"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    ADJUSTMENT = "adjustment"
    RESERVATION = "reservation"
    RELEASE = "release"


class InventoryBalance(Base):
    __tablename__ = "inventory_balances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False, index=True)
    quantity_on_hand: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_movement_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    product: Mapped["Product"] = relationship(back_populates="inventory_balances")
    warehouse: Mapped["Warehouse"] = relationship(back_populates="inventory_balances")

    __table_args__ = (UniqueConstraint("product_id", "warehouse_id", name="uq_product_warehouse"),)

    @property
    def available_quantity(self) -> int:
        return self.quantity_on_hand - self.reserved_quantity


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False, index=True)
    movement_type: Mapped[MovementType] = mapped_column(Enum(MovementType), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reference_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    product: Mapped["Product"] = relationship(back_populates="inventory_movements")
    warehouse: Mapped["Warehouse"] = relationship(back_populates="inventory_movements")

    __table_args__ = (Index("ix_movements_product_date", "product_id", "created_at"), Index("ix_movements_reference", "reference_type", "reference_id"),)
