from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.user import User, Role
from app.models.supplier import Supplier, SupplierStatus
from app.models.product import Product, Warehouse
from app.models.inventory import InventoryBalance, InventoryMovement, MovementType
from app.models.procurement import (
    PurchaseRequisition,
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseOrderStatus,
    RequisitionStatus,
    ApprovalRecord,
)
from app.models.receipt import GoodsReceipt, GoodsReceiptLine
from app.models.invoice import SupplierInvoice, SupplierInvoiceLine, InvoiceStatus


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_role(self, role: Role) -> List[User]:
        result = await self.db.execute(select(User).where(User.role == role, User.is_active == True))
        return list(result.scalars().all())


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, db: AsyncSession):
        super().__init__(Supplier, db)

    async def get_by_code(self, code: str) -> Optional[Supplier]:
        result = await self.db.execute(select(Supplier).where(Supplier.supplier_code == code))
        return result.scalar_one_or_none()

    async def search(
        self,
        search: Optional[str] = None,
        status: Optional[SupplierStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Supplier]:
        query = select(Supplier)
        conditions = []
        if search:
            conditions.append(
                or_(
                    Supplier.name.ilike(f"%{search}%"),
                    Supplier.supplier_code.ilike(f"%{search}%"),
                )
            )
        if status:
            conditions.append(Supplier.status == status)
        if conditions:
            query = query.where(and_(*conditions))
        query = query.offset(skip).limit(limit).order_by(Supplier.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_search(
        self,
        search: Optional[str] = None,
        status: Optional[SupplierStatus] = None,
    ) -> int:
        query = select(func.count()).select_from(Supplier)
        conditions = []
        if search:
            conditions.append(
                or_(
                    Supplier.name.ilike(f"%{search}%"),
                    Supplier.supplier_code.ilike(f"%{search}%"),
                )
            )
        if status:
            conditions.append(Supplier.status == status)
        if conditions:
            query = query.where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one()


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        result = await self.db.execute(select(Product).where(Product.sku == sku))
        return result.scalar_one_or_none()

    async def search(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Product]:
        query = select(Product)
        conditions = []
        if search:
            conditions.append(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%"),
                )
            )
        if is_active is not None:
            conditions.append(Product.is_active == is_active)
        if conditions:
            query = query.where(and_(*conditions))
        query = query.offset(skip).limit(limit).order_by(Product.sku)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class WarehouseRepository(BaseRepository[Warehouse]):
    def __init__(self, db: AsyncSession):
        super().__init__(Warehouse, db)

    async def get_by_code(self, code: str) -> Optional[Warehouse]:
        result = await self.db.execute(select(Warehouse).where(Warehouse.code == code))
        return result.scalar_one_or_none()

    async def get_active(self) -> List[Warehouse]:
        result = await self.db.execute(select(Warehouse).where(Warehouse.is_active == True))
        return list(result.scalars().all())


class InventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_balance(self, product_id: int, warehouse_id: int) -> Optional[InventoryBalance]:
        result = await self.db.execute(
            select(InventoryBalance).where(
                InventoryBalance.product_id == product_id,
                InventoryBalance.warehouse_id == warehouse_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_balances_by_product(self, product_id: int) -> List[InventoryBalance]:
        result = await self.db.execute(
            select(InventoryBalance)
            .where(InventoryBalance.product_id == product_id)
            .options(selectinload(InventoryBalance.warehouse))
        )
        return list(result.scalars().all())

    async def get_low_stock(
        self,
        warehouse_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[InventoryBalance]:
        query = (
            select(InventoryBalance)
            .join(Product)
            .where(InventoryBalance.available_quantity <= Product.reorder_level)
            .options(selectinload(InventoryBalance.product), selectinload(InventoryBalance.warehouse))
        )
        if warehouse_id:
            query = query.where(InventoryBalance.warehouse_id == warehouse_id)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_movement(
        self,
        product_id: int,
        warehouse_id: int,
        movement_type: MovementType,
        quantity: int,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        notes: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> InventoryMovement:
        movement = InventoryMovement(
            product_id=product_id,
            warehouse_id=warehouse_id,
            movement_type=movement_type,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            created_by=created_by,
        )
        self.db.add(movement)
        await self.db.flush()
        return movement

    async def get_movements(
        self,
        product_id: Optional[int] = None,
        warehouse_id: Optional[int] = None,
        movement_type: Optional[MovementType] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[InventoryMovement]:
        query = select(InventoryMovement).options(
            selectinload(InventoryMovement.product),
            selectinload(InventoryMovement.warehouse),
        )
        conditions = []
        if product_id:
            conditions.append(InventoryMovement.product_id == product_id)
        if warehouse_id:
            conditions.append(InventoryMovement.warehouse_id == warehouse_id)
        if movement_type:
            conditions.append(InventoryMovement.movement_type == movement_type)
        if conditions:
            query = query.where(and_(*conditions))
        query = query.order_by(InventoryMovement.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class ProcurementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_po_with_details(self, po_id: int) -> Optional[PurchaseOrder]:
        result = await self.db.execute(
            select(PurchaseOrder)
            .where(PurchaseOrder.id == po_id)
            .options(
                selectinload(PurchaseOrder.supplier),
                selectinload(PurchaseOrder.lines).selectinload(PurchaseOrderLine.product),
                selectinload(PurchaseOrder.receipts).selectinload(GoodsReceipt.lines),
                selectinload(PurchaseOrder.invoices).selectinload(SupplierInvoice.lines),
            )
        )
        return result.scalar_one_or_none()

    async def search_pos(
        self,
        status: Optional[PurchaseOrderStatus] = None,
        supplier_id: Optional[int] = None,
        search: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[PurchaseOrder]:
        query = (
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.supplier), selectinload(PurchaseOrder.lines))
        )
        conditions = []
        if status:
            conditions.append(PurchaseOrder.status == status)
        if supplier_id:
            conditions.append(PurchaseOrder.supplier_id == supplier_id)
        if search:
            conditions.append(
                or_(
                    PurchaseOrder.po_number.ilike(f"%{search}%"),
                    Supplier.name.ilike(f"%{search}%"),
                )
            )
        if date_from:
            conditions.append(PurchaseOrder.order_date >= date_from)
        if date_to:
            conditions.append(PurchaseOrder.order_date <= date_to)
        if conditions:
            query = query.where(and_(*conditions))
        query = query.order_by(PurchaseOrder.order_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_pos(
        self,
        status: Optional[PurchaseOrderStatus] = None,
        supplier_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> int:
        query = select(func.count()).select_from(PurchaseOrder)
        conditions = []
        if status:
            conditions.append(PurchaseOrder.status == status)
        if supplier_id:
            conditions.append(PurchaseOrder.supplier_id == supplier_id)
        if search:
            conditions.append(PurchaseOrder.po_number.ilike(f"%{search}%"))
        if conditions:
            query = query.where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_pending_approvals(self, user_id: Optional[int] = None) -> List[PurchaseOrder]:
        query = (
            select(PurchaseOrder)
            .where(PurchaseOrder.status == PurchaseOrderStatus.PENDING_APPROVAL)
            .options(selectinload(PurchaseOrder.supplier), selectinload(PurchaseOrder.lines))
        )
        if user_id:
            query = query.where(PurchaseOrder.approved_by == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_overdue_deliveries(self) -> List[PurchaseOrder]:
        now = datetime.utcnow()
        result = await self.db.execute(
            select(PurchaseOrder)
            .where(
                PurchaseOrder.expected_delivery_date < now,
                PurchaseOrder.status.in_([
                    PurchaseOrderStatus.APPROVED,
                    PurchaseOrderStatus.ORDERED,
                    PurchaseOrderStatus.PARTIALLY_RECEIVED,
                ]),
            )
            .options(selectinload(PurchaseOrder.supplier), selectinload(PurchaseOrder.lines))
        )
        return list(result.scalars().all())

    async def create_po(self, po: PurchaseOrder, lines: List[PurchaseOrderLine]) -> PurchaseOrder:
        self.db.add(po)
        await self.db.flush()
        for line in lines:
            line.purchase_order_id = po.id
            self.db.add(line)
        await self.db.flush()
        return po


class ReceiptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_gr_with_details(self, gr_id: int) -> Optional[GoodsReceipt]:
        result = await self.db.execute(
            select(GoodsReceipt)
            .where(GoodsReceipt.id == gr_id)
            .options(
                selectinload(GoodsReceipt.purchase_order),
                selectinload(GoodsReceipt.lines).selectinload(GoodsReceiptLine.product),
            )
        )
        return result.scalar_one_or_none()

    async def get_grs_for_po(self, po_id: int) -> List[GoodsReceipt]:
        result = await self.db.execute(
            select(GoodsReceipt)
            .where(GoodsReceipt.purchase_order_id == po_id)
            .options(selectinload(GoodsReceipt.lines))
        )
        return list(result.scalars().all())


class InvoiceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_invoice_with_details(self, invoice_id: int) -> Optional[SupplierInvoice]:
        result = await self.db.execute(
            select(SupplierInvoice)
            .where(SupplierInvoice.id == invoice_id)
            .options(
                selectinload(SupplierInvoice.supplier),
                selectinload(SupplierInvoice.purchase_order),
                selectinload(SupplierInvoice.lines).selectinload(SupplierInvoiceLine.product),
            )
        )
        return result.scalar_one_or_none()

    async def search_invoices(
        self,
        status: Optional[InvoiceStatus] = None,
        supplier_id: Optional[int] = None,
        po_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[SupplierInvoice]:
        query = select(SupplierInvoice).options(
            selectinload(SupplierInvoice.supplier),
            selectinload(SupplierInvoice.lines),
        )
        conditions = []
        if status:
            conditions.append(SupplierInvoice.status == status)
        if supplier_id:
            conditions.append(SupplierInvoice.supplier_id == supplier_id)
        if po_id:
            conditions.append(SupplierInvoice.purchase_order_id == po_id)
        if conditions:
            query = query.where(and_(*conditions))
        query = query.order_by(SupplierInvoice.invoice_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())