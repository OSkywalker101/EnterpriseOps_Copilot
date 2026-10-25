import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base


class Role(str, enum.Enum):
    EMPLOYEE = "employee"
    PROCUREMENT_SPECIALIST = "procurement_specialist"
    INVENTORY_MANAGER = "inventory_manager"
    APPROVER = "approver"
    ADMINISTRATOR = "administrator"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.EMPLOYEE, nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    warehouse_id: Mapped[Optional[int]] = mapped_column(ForeignKey("warehouses.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    warehouse: Mapped[Optional["Warehouse"]] = relationship(back_populates="users")
    conversations: Mapped[List["Conversation"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    approval_records: Mapped[List["ApprovalRecord"]] = relationship(back_populates="approver")
    audit_events: Mapped[List["AuditEvent"]] = relationship(back_populates="user")

    __table_args__ = (Index("ix_users_email_active", "email", "is_active"),)
