from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.repositories import (
    SupplierRepository,
    ProductRepository,
    WarehouseRepository,
    InventoryRepository,
    ProcurementRepository,
    ReceiptRepository,
    InvoiceRepository,
)
from app.models import (
    Supplier,
    Product,
    Warehouse,
    InventoryBalance,
    InventoryMovement,
    MovementType,
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseOrderStatus,
    PurchaseRequisition,
    RequisitionStatus,
    ApprovalRecord,
    GoodsReceipt,
    GoodsReceiptLine,
    SupplierInvoice,
    SupplierInvoiceLine,
    InvoiceStatus,
)
from app.core.audit import log_audit_event


class SupplierService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SupplierRepository(db)

    async def create_supplier(self, data: dict, user_id: int) -> Supplier:
        supplier = Supplier(**data)
        result = await self.repo.create(supplier)
        await log_audit_event(self.db, "create", "supplier", result.id, user_id, f"Created supplier {result.supplier_code}")
        return result

    async def update_supplier(self, supplier_id: int, data: dict, user_id: int) -> Optional[Supplier]:
        result = await self.repo.update(supplier_id, data)
        if result:
            await log_audit_event(self.db, "update", "supplier", supplier_id, user_id, f"Updated supplier {result.supplier_code}")
        return result

    async def search_suppliers(self, **filters) -> List[Supplier]:
        return await self.repo.search(**filters)


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProductRepository(db)
        self.warehouse_repo = WarehouseRepository(db)

    async def create_product(self, data: dict, user_id: int) -> Product:
        product = Product(**data)
        result = await self.repo.create(product)
        await log_audit_event(self.db, "create", "product", result.id, user_id, f"Created product {result.sku}")
        return result

    async def get_product_with_balances(self, product_id: int) -> Optional[Product]:
        result = await self.db.execute(
            select(Product)
            .where(Product.id == product_id)
            .options(
                selectinload(Product.inventory_balances).selectinload(InventoryBalance.warehouse)
            )
        )
        return result.scalar_one_or_none()


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = InventoryRepository(db)
        self.product_repo = ProductRepository(db)
        self.warehouse_repo = WarehouseRepository(db)

    async def get_available_quantity(self, product_id: int, warehouse_id: int) -> int:
        balance = await self.repo.get_balance(product_id, warehouse_id)
        return balance.available_quantity if balance else 0

    async def get_all_balances(self, product_id: int) -> List[InventoryBalance]:
        return await self.repo.get_balances_by_product(product_id)

    async def get_low_stock(self, warehouse_id: Optional[int] = None) -> List[InventoryBalance]:
        return await self.repo.get_low_stock(warehouse_id)

    async def record_receipt(
        self,
        product_id: int,
        warehouse_id: int,
        quantity: int,
        reference_type: str,
        reference_id: int,
        notes: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> InventoryMovement:
        balance = await self.repo.get_balance(product_id, warehouse_id)
        if not balance:
            balance = InventoryBalance(product_id=product_id, warehouse_id=warehouse_id)
            self.db.add(balance)
            await self.db.flush()
        
        balance.quantity_on_hand += quantity
        balance.last_movement_date = datetime.utcnow()
        
        movement = await self.repo.create_movement(
            product_id=product_id,
            warehouse_id=warehouse_id,
            movement_type=MovementType.RECEIPT,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            created_by=created_by,
        )
        return movement

    async def record_issue(
        self,
        product_id: int,
        warehouse_id: int,
        quantity: int,
        reference_type: str,
        reference_id: int,
        notes: Optional[str] = None,
        created_by: Optional[int] = None,
    ) -> InventoryMovement:
        balance = await self.repo.get_balance(product_id, warehouse_id)
        if not balance or balance.available_quantity < quantity:
            raise ValueError("Insufficient available stock")
        
        balance.quantity_on_hand -= quantity
        balance.last_movement_date = datetime.utcnow()
        
        movement = await self.repo.create_movement(
            product_id=product_id,
            warehouse_id=warehouse_id,
            movement_type=MovementType.ISSUE,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            created_by=created_by,
        )
        return movement


class ProcurementService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProcurementRepository(db)
        self.inventory_service = InventoryService(db)

    async def create_purchase_order(
        self,
        po_data: dict,
        lines_data: List[dict],
        user_id: int,
    ) -> PurchaseOrder:
        total_amount = sum(Decimal(str(line["quantity_ordered"])) * Decimal(str(line["unit_price"])) for line in lines_data)
        po_data["total_amount"] = float(total_amount)
        po_data["created_by"] = user_id
        
        po = PurchaseOrder(**po_data)
        lines = [PurchaseOrderLine(**line, line_total=Decimal(str(line["quantity_ordered"])) * Decimal(str(line["unit_price"]))) for line in lines_data]
        
        result = await self.repo.create_po(po, lines)
        await log_audit_event(self.db, "create", "purchase_order", result.id, user_id, f"Created PO {result.po_number}")
        return result

    async def approve_purchase_order(self, po_id: int, approver_id: int, comments: Optional[str] = None) -> PurchaseOrder:
        po = await self.repo.get_po_with_details(po_id)
        if not po:
            raise ValueError("Purchase order not found")
        if po.status != PurchaseOrderStatus.PENDING_APPROVAL:
            raise ValueError("PO is not pending approval")
        
        po.status = PurchaseOrderStatus.APPROVED
        po.approved_by = approver_id
        po.approved_at = datetime.utcnow()
        
        approval = ApprovalRecord(
            purchase_order_id=po_id,
            approver_id=approver_id,
            action="approved",
            comments=comments,
        )
        self.db.add(approval)
        await self.db.flush()
        
        await log_audit_event(self.db, "approve", "purchase_order", po_id, approver_id, f"Approved PO {po.po_number}")
        return po

    async def reject_purchase_order(self, po_id: int, approver_id: int, comments: str) -> PurchaseOrder:
        po = await self.repo.get_po_with_details(po_id)
        if not po:
            raise ValueError("Purchase order not found")
        if po.status != PurchaseOrderStatus.PENDING_APPROVAL:
            raise ValueError("PO is not pending approval")
        
        po.status = PurchaseOrderStatus.CANCELLED
        
        approval = ApprovalRecord(
            purchase_order_id=po_id,
            approver_id=approver_id,
            action="rejected",
            comments=comments,
        )
        self.db.add(approval)
        await self.db.flush()
        
        await log_audit_event(self.db, "reject", "purchase_order", po_id, approver_id, f"Rejected PO {po.po_number}")
        return po

    async def get_pending_approvals(self, user_id: Optional[int] = None) -> List[PurchaseOrder]:
        return await self.repo.get_pending_approvals(user_id)

    async def get_overdue_deliveries(self) -> List[PurchaseOrder]:
        return await self.repo.get_overdue_deliveries()


class ReceiptService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ReceiptRepository(db)
        self.procurement_repo = ProcurementRepository(db)
        self.inventory_service = InventoryService(db)

    async def create_goods_receipt(
        self,
        gr_data: dict,
        lines_data: List[dict],
        user_id: int,
    ) -> GoodsReceipt:
        gr = GoodsReceipt(**gr_data, received_by=user_id)
        self.db.add(gr)
        await self.db.flush()
        
        po = await self.procurement_repo.get_po_with_details(gr_data["purchase_order_id"])
        if not po:
            raise ValueError("Purchase order not found")
        
        for line_data in lines_data:
            line = GoodsReceiptLine(**line_data, goods_receipt_id=gr.id)
            self.db.add(line)
            
            po_line = next((l for l in po.lines if l.id == line_data["po_line_id"]), None)
            if po_line:
                po_line.quantity_received += line_data["quantity_accepted"]
            
            await self.inventory_service.record_receipt(
                product_id=line_data["product_id"],
                warehouse_id=gr_data["warehouse_id"],
                quantity=line_data["quantity_accepted"],
                reference_type="goods_receipt",
                reference_id=gr.id,
                notes=line_data.get("notes"),
                created_by=user_id,
            )
        
        received_total = sum(l.quantity_received for l in po.lines)
        ordered_total = sum(l.quantity_ordered for l in po.lines)
        
        if received_total == 0:
            po.status = PurchaseOrderStatus.ORDERED
        elif received_total >= ordered_total:
            po.status = PurchaseOrderStatus.RECEIVED
            po.actual_delivery_date = datetime.utcnow()
        else:
            po.status = PurchaseOrderStatus.PARTIALLY_RECEIVED
        
        await self.db.flush()
        await log_audit_event(self.db, "create", "goods_receipt", gr.id, user_id, f"Created GR {gr.gr_number} for PO {po.po_number}")
        return gr


class InvoiceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = InvoiceRepository(db)
        self.procurement_repo = ProcurementRepository(db)

    async def create_invoice(
        self,
        invoice_data: dict,
        lines_data: List[dict],
        user_id: int,
    ) -> SupplierInvoice:
        total_amount = sum(Decimal(str(line["quantity_invoiced"])) * Decimal(str(line["unit_price"])) for line in lines_data)
        invoice_data["total_amount"] = float(total_amount)
        
        invoice = SupplierInvoice(**invoice_data)
        self.db.add(invoice)
        await self.db.flush()
        
        for line_data in lines_data:
            line = SupplierInvoiceLine(**line_data, invoice_id=invoice.id, line_total=Decimal(str(line_data["quantity_invoiced"])) * Decimal(str(line_data["unit_price"])))
            self.db.add(line)
        
        await self.db.flush()
        await log_audit_event(self.db, "create", "supplier_invoice", invoice.id, user_id, f"Created invoice {invoice.invoice_number}")
        return invoice

    async def three_way_match(self, invoice_id: int) -> Dict[str, Any]:
        invoice = await self.repo.get_invoice_with_details(invoice_id)
        if not invoice or not invoice.purchase_order_id:
            return {"matched": False, "reason": "Invoice not linked to PO"}
        
        po = await self.procurement_repo.get_po_with_details(invoice.purchase_order_id)
        if not po:
            return {"matched": False, "reason": "Purchase order not found"}
        
        grs = await self.repo.get_grs_for_po(po.id)
        
        gr_quantities = {}
        for gr in grs:
            for gr_line in gr.lines:
                key = gr_line.po_line_id
                gr_quantities[key] = gr_quantities.get(key, 0) + gr_line.quantity_accepted
        
        discrepancies = []
        tolerance = 0.02
        
        for inv_line in invoice.lines:
            po_line = next((l for l in po.lines if l.id == inv_line.po_line_id), None)
            if not po_line:
                discrepancies.append(f"Invoice line {inv_line.line_number}: No matching PO line")
                continue
            
            gr_qty = gr_quantities.get(inv_line.po_line_id, 0)
            po_qty = po_line.quantity_ordered
            inv_qty = inv_line.quantity_invoiced
            
            qty_diff = abs(inv_qty - gr_qty)
            if qty_diff > gr_qty * tolerance and gr_qty > 0:
                discrepancies.append(
                    f"Line {inv_line.line_number}: Invoiced qty {inv_qty} vs Received qty {gr_qty}"
                )
            
            po_line_total = po_line.quantity_ordered * po_line.unit_price
            inv_line_total = inv_line.quantity_invoiced * inv_line.unit_price
            amt_diff = abs(inv_line_total - po_line_total)
            if amt_diff > po_line_total * tolerance and po_line_total > 0:
                discrepancies.append(
                    f"Line {inv_line.line_number}: Invoiced amount {inv_line_total:.2f} vs PO amount {po_line_total:.2f}"
                )
        
        matched = len(discrepancies) == 0
        if matched:
            invoice.status = InvoiceStatus.MATCHED
        else:
            invoice.status = InvoiceStatus.DISCREPANCY
        
        await self.db.flush()
        
        return {
            "matched": matched,
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "po_number": po.po_number,
            "discrepancies": discrepancies,
            "tolerance_applied": tolerance,
        }