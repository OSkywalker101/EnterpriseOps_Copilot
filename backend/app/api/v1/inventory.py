from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.core.security import get_current_active_user, require_permission
from app.core.audit import log_audit_event
from app.schemas.inventory import InventoryBalanceResponse, InventoryMovementResponse, LowStockItem
from app.schemas.common import PaginatedResponse, PaginationParams
from app.repositories import InventoryRepository
from app.models.user import User
from app.models.inventory import MovementType

router = APIRouter()


@router.get("/balances", response_model=PaginatedResponse[InventoryBalanceResponse])
async def list_inventory_balances(
    product_id: Optional[int] = Query(None),
    warehouse_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(PaginationParams),
):
    repo = InventoryRepository(db)
    
    if product_id:
        balances = await repo.get_balances_by_product(product_id)
    else:
        from sqlalchemy import select
        from app.models.inventory import InventoryBalance
        result = await db.execute(
            select(InventoryBalance)
            .offset(pagination.offset)
            .limit(pagination.limit)
        )
        balances = list(result.scalars().all())
    
    return PaginatedResponse(
        items=balances,
        total=len(balances),
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=1,
    )


@router.get("/balances/{product_id}/{warehouse_id}", response_model=InventoryBalanceResponse)
async def get_inventory_balance(
    product_id: int,
    warehouse_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repo = InventoryRepository(db)
    balance = await repo.get_balance(product_id, warehouse_id)
    if not balance:
        raise HTTPException(status_code=404, detail="Inventory balance not found")
    return balance


@router.get("/low-stock", response_model=List[LowStockItem])
async def list_low_stock(
    warehouse_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repo = InventoryRepository(db)
    balances = await repo.get_low_stock(warehouse_id=warehouse_id)
    
    result = []
    for b in balances:
        result.append(LowStockItem(
            product_id=b.product_id,
            product_sku=b.product.sku if b.product else "",
            product_name=b.product.name if b.product else "",
            warehouse_id=b.warehouse_id,
            warehouse_code=b.warehouse.code if b.warehouse else "",
            quantity_on_hand=b.quantity_on_hand,
            reserved_quantity=b.reserved_quantity,
            available_quantity=b.available_quantity,
            reorder_level=b.product.reorder_level if b.product else 0,
        ))
    return result


@router.get("/movements", response_model=PaginatedResponse[InventoryMovementResponse])
async def list_inventory_movements(
    product_id: Optional[int] = Query(None),
    warehouse_id: Optional[int] = Query(None),
    movement_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(PaginationParams),
):
    repo = InventoryRepository(db)
    mv_type = MovementType(movement_type) if movement_type else None
    
    movements = await repo.get_movements(
        product_id=product_id,
        warehouse_id=warehouse_id,
        movement_type=mv_type,
        skip=pagination.offset,
        limit=pagination.limit,
    )
    
    return PaginatedResponse(
        items=movements,
        total=len(movements),
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=1,
    )