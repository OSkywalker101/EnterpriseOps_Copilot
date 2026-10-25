from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.core.security import get_current_active_user, require_permission
from app.core.audit import log_audit_event
from app.schemas.invoice import SupplierInvoiceCreate, SupplierInvoiceUpdate, SupplierInvoiceResponse, InvoiceMatchResult
from app.schemas.common import PaginatedResponse, PaginationParams
from app.services import InvoiceService
from app.models.user import User
from app.models.invoice import InvoiceStatus

router = APIRouter(prefix="/supplier-invoices", tags=["supplier-invoices"])


@router.post("", response_model=SupplierInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    data: SupplierInvoiceCreate,
    current_user: User = Depends(require_permission("write:procurement")),
    db: AsyncSession = Depends(get_db),
):
    service = InvoiceService(db)
    invoice = await service.create_invoice(
        invoice_data=data.model_dump(exclude={"lines"}),
        lines_data=[line.model_dump() for line in data.lines],
        user_id=current_user.id,
    )
    return invoice


@router.get("", response_model=PaginatedResponse[SupplierInvoiceResponse])
async def list_invoices(
    status: Optional[str] = Query(None),
    supplier_id: Optional[int] = Query(None),
    po_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(PaginationParams),
):
    service = InvoiceService(db)
    inv_status = InvoiceStatus(status) if status else None
    
    invoices = await service.repo.search_invoices(
        status=inv_status,
        supplier_id=supplier_id,
        po_id=po_id,
        skip=pagination.offset,
        limit=pagination.limit,
    )
    
    return PaginatedResponse(
        items=invoices,
        total=len(invoices),
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=1,
    )


@router.get("/{invoice_id}", response_model=SupplierInvoiceResponse)
async def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = InvoiceService(db)
    invoice = await service.repo.get_invoice_with_details(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("/{invoice_id}/match-po", response_model=InvoiceMatchResult)
async def match_invoice_po(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = InvoiceService(db)
    result = await service.three_way_match(invoice_id)
    return result


@router.post("/{invoice_id}/match-gr", response_model=InvoiceMatchResult)
async def match_invoice_gr(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = InvoiceService(db)
    result = await service.three_way_match(invoice_id)
    return result