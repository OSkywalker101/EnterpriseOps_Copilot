from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.core.security import get_current_active_user, require_permission
from app.core.audit import log_audit_event
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse, SupplierSummary
from app.schemas.common import PaginatedResponse, PaginationParams
from app.services import SupplierService
from app.models.user import User, Role

router = APIRouter()


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    data: SupplierCreate,
    current_user: User = Depends(require_permission("write:procurement")),
    db: AsyncSession = Depends(get_db),
):
    service = SupplierService(db)
    supplier = await service.create_supplier(data.model_dump(), current_user.id)
    return supplier


@router.get("", response_model=PaginatedResponse[SupplierSummary])
async def list_suppliers(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(PaginationParams),
):
    service = SupplierService(db)
    suppliers = await service.search_suppliers(
        search=search,
        status=status,
        skip=pagination.offset,
        limit=pagination.limit,
    )
    total = await service.repo.count_search(search=search, status=status)
    
    return PaginatedResponse(
        items=suppliers,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=(total + pagination.page_size - 1) // pagination.page_size,
    )


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = SupplierService(db)
    supplier = await service.repo.get_by_id(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.patch("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    current_user: User = Depends(require_permission("write:procurement")),
    db: AsyncSession = Depends(get_db),
):
    service = SupplierService(db)
    supplier = await service.update_supplier(supplier_id, data.model_dump(exclude_unset=True), current_user.id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier