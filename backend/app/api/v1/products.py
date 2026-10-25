from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.core.security import get_current_active_user, require_permission
from app.core.audit import log_audit_event
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductSummary,
    WarehouseCreate, WarehouseUpdate, WarehouseResponse,
)
from app.schemas.common import PaginatedResponse, PaginationParams
from app.repositories import ProductRepository, WarehouseRepository
from app.models.user import User

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    current_user: User = Depends(require_permission("write:catalog")),
    db: AsyncSession = Depends(get_db),
):
    repo = ProductRepository(db)
    existing = await repo.get_by_sku(data.sku)
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    product = repo.model(**data.model_dump())
    created = await repo.create(product)
    await log_audit_event(db, "create", "product", created.id, current_user.id, f"Created product {created.sku}")
    return created


@router.get("", response_model=PaginatedResponse[ProductSummary])
async def list_products(
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(PaginationParams),
):
    repo = ProductRepository(db)
    products = await repo.search(
        search=search,
        is_active=is_active,
        skip=pagination.offset,
        limit=pagination.limit,
    )
    return PaginatedResponse(
        items=products,
        total=len(products),
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=1,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ProductRepository(db)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    current_user: User = Depends(require_permission("write:catalog")),
    db: AsyncSession = Depends(get_db),
):
    repo = ProductRepository(db)
    product = await repo.update(product_id, data.model_dump(exclude_unset=True))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await log_audit_event(db, "update", "product", product_id, current_user.id, f"Updated product")
    return product


warehouse_router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@warehouse_router.post("", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    data: WarehouseCreate,
    current_user: User = Depends(require_permission("write:catalog")),
    db: AsyncSession = Depends(get_db),
):
    repo = WarehouseRepository(db)
    existing = await repo.get_by_code(data.code)
    if existing:
        raise HTTPException(status_code=400, detail="Warehouse code already exists")
    
    warehouse = repo.model(**data.model_dump())
    created = await repo.create(warehouse)
    await log_audit_event(db, "create", "warehouse", created.id, current_user.id, f"Created warehouse {created.code}")
    return created


@warehouse_router.get("", response_model=List[WarehouseResponse])
async def list_warehouses(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repo = WarehouseRepository(db)
    return await repo.get_active()


@warehouse_router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    repo = WarehouseRepository(db)
    warehouse = await repo.get_by_id(warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse