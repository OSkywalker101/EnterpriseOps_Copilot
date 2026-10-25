from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from app.models.audit import AuditEvent


async def log_audit_event(
    db: AsyncSession,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    user_id: Optional[int] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    event = AuditEvent(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.utcnow(),
    )
    db.add(event)
    await db.flush()