from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.core.security import get_current_active_user, require_permission
from app.core.audit import log_audit_event
from app.schemas.procurement import (
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse,
    PurchaseRequisitionCreate, PurchaseRequisitionUpdate, PurchaseRequisitionResponse,
    ApprovalRecordCreate, ApprovalRecordResponse,
)
from app.schemas.common import PaginatedResponse, PaginationParams
from app.repositories import ProcurementRepository
from app.services import ProcurementService
from app.models.user import User
from app.models.procurement import PurchaseOrderStatus, RequisitionStatus

router = APIRouter(prefix="/purchase-orders", tags=["purchase-orders"])


@router.post("", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    data: PurchaseOrderCreate,
    current_user: User = Depends(require_permission("write:procurement")),
    db: AsyncSession = Depends(get_db),
):
    service = ProcurementService(db)
    po = await service.create_purchase_order(
        po_data=data.model_dump(exclude={"lines"}),
        lines_data=[line.model_dump() for line in data.lines],
        user_id=current_user.id,
    )
    return po


@router.get("", response_model=PaginatedResponse[PurchaseOrderResponse])
async def list_purchase_orders(
    status: Optional[str] = Query(None),
    supplier_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(PaginationParams),
):
    repo = ProcurementRepository(db)
    
    from app.models.procurement import PurchaseOrderStatus
    po_status = PurchaseOrderStatus(status) if status else None
    
    from datetime import datetime
    date_from_dt = datetime.fromisoformat(date_from) if date_from else None
    date_to_dt = datetime.fromisoformat(date_to) if date_to else None
    
    pos = await repo.search_pos(
        status=po_status,
        supplier_id=supplier_id,
        search=search,
        date_from=date_from_dt,
        date_to=date_to_dt,
        skip=pagination.offset,
        limit=pagination.limit,
    )
    total = await repo.count_pos(status=po_status, supplier_id=supplier_id, search=search)
    
    return PaginatedResponse(
        items=pos,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


@router.get("/pending-approvals", response_model=List[PurchaseOrderResponse])
async def get_pending_approvals(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProcurementService(db)
    return await service.get_pending_approvals()


@router.get("/overdue", response_model=List[PurchaseOrderResponse])
async def get_overdue_deliveries(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProcurementService(db)
    return await service.get_overdue_deliveries()


@router.get("/{po_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    po_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ProcurementRepository(db)
    po = await repo.get_po_with_details(po_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


@router.patch("/{po_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(
    po_id: int,
    data: PurchaseOrderUpdate,
    current_user: User = Depends(require_permission("write:procurement")),
    db: AsyncSession = Depends(get_db),
):
    repo = ProcurementRepository(db)
    po = await repo.update(po_id, data.model_dump(exclude_unset=True))
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    await log_audit_event(db, "update", "purchase_order", po_id, current_user.id, f"Updated PO")
    return po


@router.post("/{po_id}/approve", response_model=PurchaseOrderResponse)
async def approve_purchase_order(
    po_id: int,
    comments: Optional[str] = None,
    current_user: User = Depends(require_permission("write:approvals")),
    db: AsyncSession = Depends(get_db),
):
    service = ProcurementService(db)
    try:
        po = await service.approve_purchase_order(po_id, current_user.id, comments)
        return po
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{po_id}/reject", response_model=PurchaseOrderResponse)
async def reject_purchase_order(
    po_id: int,
    comments: str,
    current_user: User = Depends(require_permission("write:approvals")),
    db: AsyncSession = Depends(get_db),
):
    service = ProcurementService(db)
    try:
        po = await service.reject_purchase_order(po_id, current_user.id, comments)
        return po
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


requisition_router = APIRouter(prefix="/purchase-requisitions", tags=["purchase-requisitions"])


@requisition_router.post("", response_model=PurchaseRequisitionResponse, status_code=status.HTTP_201_CREATED)
async def create_requisition(
    data: PurchaseRequisitionCreate,
    current_user: User = Depends(require_permission("write:procurement")),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories import ProcurementRepository
    repo = ProcurementRepository(db)
    requisition = repo.model(**data.model_dump())
    created = await repo.create(requisition)
    await log_audit_event(db, "create", "purchase_requisition", created.id, current_user.id, f"Created requisition")
    return created


@requisition_router.get("", response_model=PaginatedResponse[PurchaseRequisitionResponse])
async def list_requisitions(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(PaginationParams),
):
    from sqlalchemy import select
    from app.models.procurement import PurchaseRequisition, RequisitionStatus
    
    query = select(PurchaseRequisition)
    if status:
        query = query.where(PurchaseRequisition.status == RequisitionStatus(status))
    query = query.offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    requisitions = list(result.scalars().all())
    
    return PaginatedResponse(
        items=requisitions,
        total=len(requisitions),
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=1,
    )


@requisition_router.get("/{requisition_id}", response_model=PurchaseRequisitionResponse)
async def get_requisition(
    requisition_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories import ProcurementRepository
    repo = ProcurementRepository(db)
    requisition = await repo.get_by_id(requisition_id)
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    return requisition