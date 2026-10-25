from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.core.security import get_current_active_user, require_permission
from app.core.audit import log_audit_event
from app.schemas.receipt import GoodsReceiptCreate, GoodsReceiptUpdate, GoodsReceiptResponse
from app.schemas.common import PaginatedResponse, PaginationParams
from app.services import ReceiptService
from app.models.user import User

router = APIRouter(prefix="/goods-receipts", tags=["goods-receipts"])


@router.post("", response_model=GoodsReceiptResponse, status_code=status.HTTP_201_CREATED)
async def create_goods_receipt(
    data: GoodsReceiptCreate,
    current_user: User = Depends(require_permission("write:inventory")),
    db: AsyncSession = Depends(get_db),
):
    service = ReceiptService(db)
    gr = await service.create_goods_receipt(
        gr_data=data.model_dump(exclude={"lines"}),
        lines_data=[line.model_dump() for line in data.lines],
        user_id=current_user.id,
    )
    return gr


@router.get("", response_model=PaginatedResponse[GoodsReceiptResponse])
async def list_goods_receipts(
    po_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    pagination: PaginationParams = Depends(PaginationParams),
):
    from sqlalchemy import select
    from app.models.receipt import GoodsReceipt
    
    query = select(GoodsReceipt)
    if po_id:
        query = query.where(GoodsReceipt.purchase_order_id == po_id)
    query = query.offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    receipts = list(result.scalars().all())
    
    return PaginatedResponse(
        items=receipts,
        total=len(receipts),
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=1,
    )


@router.get("/{gr_id}", response_model=GoodsReceiptResponse)
async def get_goods_receipt(
    gr_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories import ReceiptRepository
    repo = ReceiptRepository(db)
    gr = await repo.get_gr_with_details(gr_id)
    if not gr:
        raise HTTPException(status_code=404, detail="Goods receipt not found")
    return gr