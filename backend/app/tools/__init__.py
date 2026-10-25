from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

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
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseOrderStatus,
    Supplier,
    Product,
    InventoryBalance,
    InventoryMovement,
    MovementType,
    GoodsReceipt,
    SupplierInvoice,
    InvoiceStatus,
)
from app.core.security import get_current_user
from app.db.base import get_db


class ToolResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    citations: List[Dict[str, Any]] = []


class ToolContext:
    def __init__(self, db: AsyncSession, user_id: int):
        self.db = db
        self.user_id = user_id
        self.supplier_repo = SupplierRepository(db)
        self.product_repo = ProductRepository(db)
        self.warehouse_repo = WarehouseRepository(db)
        self.inventory_repo = InventoryRepository(db)
        self.procurement_repo = ProcurementRepository(db)
        self.receipt_repo = ReceiptRepository(db)
        self.invoice_repo = InvoiceRepository(db)


async def search_purchase_orders(
    ctx: ToolContext,
    status: Optional[str] = None,
    supplier_id: Optional[int] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> ToolResult:
    try:
        po_status = PurchaseOrderStatus(status) if status else None
        date_from_dt = datetime.fromisoformat(date_from) if date_from else None
        date_to_dt = datetime.fromisoformat(date_to) if date_to else None
        
        pos = await ctx.procurement_repo.search_pos(
            status=po_status,
            supplier_id=supplier_id,
            search=search,
            date_from=date_from_dt,
            date_to=date_to_dt,
            skip=(page - 1) * page_size,
            limit=page_size,
        )
        total = await ctx.procurement_repo.count_pos(status=po_status, supplier_id=supplier_id, search=search)
        
        data = [
            {
                "id": po.id,
                "po_number": po.po_number,
                "supplier_id": po.supplier_id,
                "supplier_name": po.supplier.name if po.supplier else None,
                "status": po.status.value,
                "order_date": po.order_date.isoformat(),
                "expected_delivery_date": po.expected_delivery_date.isoformat() if po.expected_delivery_date else None,
                "total_amount": float(po.total_amount),
                "currency": po.currency,
            }
            for po in pos
        ]
        
        citations = [{"type": "purchase_order", "id": po.id, "reference": po.po_number} for po in pos]
        
        return ToolResult(success=True, data={"items": data, "total": total, "page": page, "page_size": page_size}, citations=citations)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def get_purchase_order_details(ctx: ToolContext, po_id: int) -> ToolResult:
    try:
        po = await ctx.procurement_repo.get_po_with_details(po_id)
        if not po:
            return ToolResult(success=False, error="Purchase order not found")
        
        data = {
            "id": po.id,
            "po_number": po.po_number,
            "supplier": {"id": po.supplier.id, "name": po.supplier.name, "supplier_code": po.supplier.supplier_code} if po.supplier else None,
            "status": po.status.value,
            "order_date": po.order_date.isoformat(),
            "expected_delivery_date": po.expected_delivery_date.isoformat() if po.expected_delivery_date else None,
            "actual_delivery_date": po.actual_delivery_date.isoformat() if po.actual_delivery_date else None,
            "currency": po.currency,
            "total_amount": float(po.total_amount),
            "notes": po.notes,
            "lines": [
                {
                    "id": line.id,
                    "line_number": line.line_number,
                    "product_id": line.product_id,
                    "product_sku": line.product.sku if line.product else None,
                    "product_name": line.product.name if line.product else None,
                    "quantity_ordered": line.quantity_ordered,
                    "quantity_received": line.quantity_received,
                    "unit_price": float(line.unit_price),
                    "line_total": float(line.line_total),
                    "currency": line.currency,
                }
                for line in po.lines
            ],
        }
        
        citations = [{"type": "purchase_order", "id": po.id, "reference": po.po_number}]
        return ToolResult(success=True, data=data, citations=citations)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def list_pending_approvals(ctx: ToolContext) -> ToolResult:
    try:
        pos = await ctx.procurement_repo.get_pending_approvals()
        data = [
            {
                "id": po.id,
                "po_number": po.po_number,
                "supplier_name": po.supplier.name if po.supplier else None,
                "order_date": po.order_date.isoformat(),
                "expected_delivery_date": po.expected_delivery_date.isoformat() if po.expected_delivery_date else None,
                "total_amount": float(po.total_amount),
                "currency": po.currency,
            }
            for po in pos
        ]
        citations = [{"type": "purchase_order", "id": po.id, "reference": po.po_number} for po in pos]
        return ToolResult(success=True, data={"items": data}, citations=citations)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def search_suppliers(
    ctx: ToolContext,
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> ToolResult:
    try:
        from app.models.supplier import SupplierStatus
        supplier_status = SupplierStatus(status) if status else None
        
        suppliers = await ctx.supplier_repo.search(
            search=search,
            status=supplier_status,
            skip=(page - 1) * page_size,
            limit=page_size,
        )
        total = await ctx.supplier_repo.count_search(search=search, status=supplier_status)
        
        data = [
            {
                "id": s.id,
                "supplier_code": s.supplier_code,
                "name": s.name,
                "contact_name": s.contact_name,
                "contact_email": s.contact_email,
                "status": s.status.value,
                "lead_time_days": s.lead_time_days,
                "currency": s.currency,
            }
            for s in suppliers
        ]
        
        citations = [{"type": "supplier", "id": s.id, "reference": s.supplier_code} for s in suppliers]
        return ToolResult(success=True, data={"items": data, "total": total, "page": page, "page_size": page_size}, citations=citations)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def get_supplier_delivery_summary(ctx: ToolContext, supplier_id: int) -> ToolResult:
    try:
        supplier = await ctx.supplier_repo.get_by_id(supplier_id)
        if not supplier:
            return ToolResult(success=False, error="Supplier not found")
        
        pos = await ctx.procurement_repo.search_pos(supplier_id=supplier_id, limit=100)
        
        total_pos = len(pos)
        on_time = 0
        late = 0
        pending = 0
        
        for po in pos:
            if po.actual_delivery_date and po.expected_delivery_date:
                if po.actual_delivery_date <= po.expected_delivery_date:
                    on_time += 1
                else:
                    late += 1
            elif po.expected_delivery_date and po.expected_delivery_date < datetime.utcnow():
                pending += 1
        
        on_time_rate = on_time / max(1, total_pos) * 100
        
        data = {
            "supplier_id": supplier.id,
            "supplier_code": supplier.supplier_code,
            "supplier_name": supplier.name,
            "total_purchase_orders": total_pos,
            "on_time_deliveries": on_time,
            "late_deliveries": late,
            "pending_deliveries": pending,
            "on_time_rate_percent": round(on_time_rate, 2),
            "lead_time_days": supplier.lead_time_days,
        }
        
        citations = [{"type": "supplier", "id": supplier.id, "reference": supplier.supplier_code}]
        return ToolResult(success=True, data=data, citations=citations)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def get_inventory_balance(
    ctx: ToolContext,
    product_id: Optional[int] = None,
    sku: Optional[str] = None,
    warehouse_id: Optional[int] = None,
) -> ToolResult:
    try:
        if sku:
            product = await ctx.product_repo.get_by_sku(sku)
            if not product:
                return ToolResult(success=False, error="Product not found")
            product_id = product.id
        
        if not product_id:
            return ToolResult(success=False, error="Product ID or SKU required")
        
        if warehouse_id:
            balance = await ctx.inventory_repo.get_balance(product_id, warehouse_id)
            balances = [balance] if balance else []
        else:
            balances = await ctx.inventory_repo.get_balances_by_product(product_id)
        
        data = [
            {
                "product_id": b.product_id,
                "product_sku": b.product.sku if b.product else None,
                "product_name": b.product.name if b.product else None,
                "warehouse_id": b.warehouse_id,
                "warehouse_code": b.warehouse.code if b.warehouse else None,
                "quantity_on_hand": b.quantity_on_hand,
                "reserved_quantity": b.reserved_quantity,
                "available_quantity": b.available_quantity,
                "reorder_level": b.product.reorder_level if b.product else 0,
                "last_movement_date": b.last_movement_date.isoformat() if b.last_movement_date else None,
            }
            for b in balances
        ]
        
        citations = [{"type": "inventory_balance", "product_id": b.product_id, "warehouse_id": b.warehouse_id} for b in balances]
        return ToolResult(success=True, data={"items": data}, citations=citations)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def get_inventory_movements(
    ctx: ToolContext,
    product_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    movement_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
) -> ToolResult:
    try:
        from app.models.inventory import MovementType
        mv_type = MovementType(movement_type) if movement_type else None
        
        movements = await ctx.inventory_repo.get_movements(
            product_id=product_id,
            warehouse_id=warehouse_id,
            movement_type=mv_type,
            skip=(page - 1) * page_size,
            limit=page_size,
        )
        
        data = [
            {
                "id": m.id,
                "product_id": m.product_id,
                "product_sku": m.product.sku if m.product else None,
                "warehouse_id": m.warehouse_id,
                "warehouse_code": m.warehouse.code if m.warehouse else None,
                "movement_type": m.movement_type.value,
                "quantity": m.quantity,
                "reference_type": m.reference_type,
                "reference_id": m.reference_id,
                "notes": m.notes,
                "created_at": m.created_at.isoformat(),
                "created_by": m.created_by,
            }
            for m in movements
        ]
        
        citations = [{"type": "inventory_movement", "id": m.id} for m in movements]
        return ToolResult(success=True, data={"items": data}, citations=citations)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def list_low_stock_products(ctx: ToolContext, warehouse_id: Optional[int] = None) -> ToolResult:
    try:
        balances = await ctx.inventory_repo.get_low_stock(warehouse_id=warehouse_id)
        
        data = [
            {
                "product_id": b.product_id,
                "product_sku": b.product.sku if b.product else None,
                "product_name": b.product.name if b.product else None,
                "warehouse_id": b.warehouse_id,
                "warehouse_code": b.warehouse.code if b.warehouse else None,
                "quantity_on_hand": b.quantity_on_hand,
                "reserved_quantity": b.reserved_quantity,
                "available_quantity": b.available_quantity,
                "reorder_level": b.product.reorder_level if b.product else 0,
            }
            for b in balances
        ]
        
        citations = [{"type": "inventory_balance", "product_id": b.product_id, "warehouse_id": b.warehouse_id} for b in balances]
        return ToolResult(success=True, data={"items": data}, citations=citations)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def get_invoice_details(ctx: ToolContext, invoice_id: int) -> ToolResult:
    try:
        invoice = await ctx.invoice_repo.get_invoice_with_details(invoice_id)
        if not invoice:
            return ToolResult(success=False, error="Invoice not found")
        
        data = {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "supplier": {"id": invoice.supplier.id, "name": invoice.supplier.name} if invoice.supplier else None,
            "purchase_order_id": invoice.purchase_order_id,
            "status": invoice.status.value,
            "invoice_date": invoice.invoice_date.isoformat(),
            "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
            "currency": invoice.currency,
            "total_amount": float(invoice.total_amount),
            "payment_status": invoice.payment_status.value,
            "paid_amount": float(invoice.paid_amount),
            "lines": [
                {
                    "id": line.id,
                    "line_number": line.line_number,
                    "product_id": line.product_id,
                    "product_sku": line.product.sku if line.product else None,
                    "quantity_invoiced": line.quantity_invoiced,
                    "unit_price": float(line.unit_price),
                    "line_total": float(line.line_total),
                }
                for line in invoice.lines
            ],
        }
        
        citations = [{"type": "supplier_invoice", "id": invoice.id, "reference": invoice.invoice_number}]
        return ToolResult(success=True, data=data, citations=citations)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def compare_invoice_with_purchase_order(ctx: ToolContext, invoice_id: int) -> ToolResult:
    try:
        invoice = await ctx.invoice_repo.get_invoice_with_details(invoice_id)
        if not invoice or not invoice.purchase_order_id:
            return ToolResult(success=False, error="Invoice not linked to a purchase order")
        
        po = await ctx.procurement_repo.get_po_with_details(invoice.purchase_order_id)
        if not po:
            return ToolResult(success=False, error="Purchase order not found")
        
        discrepancies = []
        tolerance = 0.02
        
        for inv_line in invoice.lines:
            po_line = next((l for l in po.lines if l.id == inv_line.po_line_id), None)
            if not po_line:
                discrepancies.append(f"Invoice line {inv_line.line_number}: No matching PO line")
                continue
            
            po_line_total = po_line.quantity_ordered * po_line.unit_price
            inv_line_total = inv_line.quantity_invoiced * inv_line.unit_price
            amt_diff = abs(inv_line_total - po_line_total)
            if amt_diff > po_line_total * tolerance and po_line_total > 0:
                discrepancies.append(
                    f"Line {inv_line.line_number}: Amount mismatch - Invoice {inv_line_total:.2f} vs PO {po_line_total:.2f}"
                )
        
        data = {
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "po_number": po.po_number,
            "matched": len(discrepancies) == 0,
            "discrepancies": discrepancies,
        }
        
        citations = [
            {"type": "supplier_invoice", "id": invoice.id, "reference": invoice.invoice_number},
            {"type": "purchase_order", "id": po.id, "reference": po.po_number},
        ]
        return ToolResult(success=True, data=data, citations=citations)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def compare_invoice_with_goods_receipt(ctx: ToolContext, invoice_id: int) -> ToolResult:
    try:
        invoice = await ctx.invoice_repo.get_invoice_with_details(invoice_id)
        if not invoice or not invoice.purchase_order_id:
            return ToolResult(success=False, error="Invoice not linked to a purchase order")
        
        po = await ctx.procurement_repo.get_po_with_details(invoice.purchase_order_id)
        if not po:
            return ToolResult(success=False, error="Purchase order not found")
        
        grs = await ctx.receipt_repo.get_grs_for_po(po.id)
        
        gr_quantities = {}
        for gr in grs:
            for gr_line in gr.lines:
                key = gr_line.po_line_id
                gr_quantities[key] = gr_quantities.get(key, 0) + gr_line.quantity_accepted
        
        discrepancies = []
        tolerance = 0.02
        
        for inv_line in invoice.lines:
            gr_qty = gr_quantities.get(inv_line.po_line_id, 0)
            inv_qty = inv_line.quantity_invoiced
            
            if gr_qty > 0:
                qty_diff = abs(inv_qty - gr_qty)
                if qty_diff > gr_qty * tolerance:
                    discrepancies.append(
                        f"Line {inv_line.line_number}: Invoiced qty {inv_qty} vs Received qty {gr_qty}"
                    )
            elif inv_qty > 0:
                discrepancies.append(
                    f"Line {inv_line.line_number}: Invoiced qty {inv_qty} but no goods receipt found"
                )
        
        data = {
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "po_number": po.po_number,
            "matched": len(discrepancies) == 0,
            "discrepancies": discrepancies,
        }
        
        citations = [
            {"type": "supplier_invoice", "id": invoice.id, "reference": invoice.invoice_number},
            {"type": "purchase_order", "id": po.id, "reference": po.po_number},
        ]
        return ToolResult(success=True, data=data, citations=citations)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def summarize_procurement_exceptions(ctx: ToolContext) -> ToolResult:
    try:
        overdue = await ctx.procurement_repo.get_overdue_deliveries()
        pending_approvals = await ctx.procurement_repo.get_pending_approvals()
        
        invoices = await ctx.invoice_repo.search_invoices(status=InvoiceStatus.DISCREPANCY, limit=50)
        
        low_stock = await ctx.inventory_repo.get_low_stock(limit=20)
        
        data = {
            "overdue_deliveries": len(overdue),
            "overdue_details": [
                {"po_number": po.po_number, "supplier": po.supplier.name if po.supplier else None, "expected_date": po.expected_delivery_date.isoformat() if po.expected_delivery_date else None}
                for po in overdue[:10]
            ],
            "pending_approvals": len(pending_approvals),
            "invoice_discrepancies": len(invoices),
            "low_stock_products": len(low_stock),
            "generated_at": datetime.utcnow().isoformat(),
        }
        
        citations = []
        for po in overdue[:5]:
            citations.append({"type": "purchase_order", "id": po.id, "reference": po.po_number})
        for inv in invoices[:5]:
            citations.append({"type": "supplier_invoice", "id": inv.id, "reference": inv.invoice_number})
        for b in low_stock[:5]:
            citations.append({"type": "inventory_balance", "product_id": b.product_id, "warehouse_id": b.warehouse_id})
        
        return ToolResult(success=True, data=data, citations=citations)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


async def get_approved_business_policy(ctx: ToolContext, policy_name: str) -> ToolResult:
    policies = {
        "invoice_matching_tolerance": {
            "name": "invoice_matching_tolerance",
            "description": "Tolerance percentage for invoice matching",
            "value": "2%",
            "details": "Quantities and amounts within 2% of PO/GR values are considered matched",
        },
        "reorder_level_policy": {
            "name": "reorder_level_policy",
            "description": "When available stock falls below reorder level, flag for replenishment",
            "value": "reorder_level",
            "details": "Available quantity = quantity_on_hand - reserved_quantity",
        },
        "po_approval_threshold": {
            "name": "po_approval_threshold",
            "description": "Purchase orders above $10,000 require manager approval",
            "value": "10000",
            "details": "Amount in USD",
        },
        "payment_terms": {
            "name": "payment_terms",
            "description": "Standard payment terms for suppliers",
            "value": "Net 30",
            "details": "Payment due 30 days from invoice date",
        },
    }
    
    policy = policies.get(policy_name)
    if not policy:
        return ToolResult(success=False, error=f"Policy '{policy_name}' not found")
    
    return ToolResult(success=True, data=policy, citations=[{"type": "business_policy", "reference": policy_name}])


TOOLS = {
    "search_purchase_orders": search_purchase_orders,
    "get_purchase_order_details": get_purchase_order_details,
    "list_pending_approvals": list_pending_approvals,
    "search_suppliers": search_suppliers,
    "get_supplier_delivery_summary": get_supplier_delivery_summary,
    "get_inventory_balance": get_inventory_balance,
    "get_inventory_movements": get_inventory_movements,
    "list_low_stock_products": list_low_stock_products,
    "get_invoice_details": get_invoice_details,
    "compare_invoice_with_purchase_order": compare_invoice_with_purchase_order,
    "compare_invoice_with_goods_receipt": compare_invoice_with_goods_receipt,
    "summarize_procurement_exceptions": summarize_procurement_exceptions,
    "get_approved_business_policy": get_approved_business_policy,
}


TOOL_SCHEMAS = {
    "search_purchase_orders": {
        "name": "search_purchase_orders",
        "description": "Search purchase orders with filters",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": [s.value for s in PurchaseOrderStatus]},
                "supplier_id": {"type": "integer"},
                "search": {"type": "string"},
                "date_from": {"type": "string", "format": "date"},
                "date_to": {"type": "string", "format": "date"},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 20},
            },
        },
    },
    "get_purchase_order_details": {
        "name": "get_purchase_order_details",
        "description": "Get detailed purchase order information",
        "parameters": {
            "type": "object",
            "properties": {"po_id": {"type": "integer"}},
            "required": ["po_id"],
        },
    },
    "list_pending_approvals": {
        "name": "list_pending_approvals",
        "description": "List purchase orders pending approval",
        "parameters": {"type": "object", "properties": {}},
    },
    "search_suppliers": {
        "name": "search_suppliers",
        "description": "Search suppliers",
        "parameters": {
            "type": "object",
            "properties": {
                "search": {"type": "string"},
                "status": {"type": "string", "enum": ["active", "inactive", "on_hold"]},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 20},
            },
        },
    },
    "get_supplier_delivery_summary": {
        "name": "get_supplier_delivery_summary",
        "description": "Get delivery performance summary for a supplier",
        "parameters": {"type": "object", "properties": {"supplier_id": {"type": "integer"}}, "required": ["supplier_id"]},
    },
    "get_inventory_balance": {
        "name": "get_inventory_balance",
        "description": "Get inventory balance for a product",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer"},
                "sku": {"type": "string"},
                "warehouse_id": {"type": "integer"},
            },
        },
    },
    "get_inventory_movements": {
        "name": "get_inventory_movements",
        "description": "Get inventory movement history",
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer"},
                "warehouse_id": {"type": "integer"},
                "movement_type": {"type": "string", "enum": [m.value for m in MovementType]},
                "page": {"type": "integer", "default": 1},
                "page_size": {"type": "integer", "default": 50},
            },
        },
    },
    "list_low_stock_products": {
        "name": "list_low_stock_products",
        "description": "List products below reorder level",
        "parameters": {"type": "object", "properties": {"warehouse_id": {"type": "integer"}}},
    },
    "get_invoice_details": {
        "name": "get_invoice_details",
        "description": "Get invoice details",
        "parameters": {"type": "object", "properties": {"invoice_id": {"type": "integer"}}, "required": ["invoice_id"]},
    },
    "compare_invoice_with_purchase_order": {
        "name": "compare_invoice_with_purchase_order",
        "description": "Compare invoice with purchase order (2-way match)",
        "parameters": {"type": "object", "properties": {"invoice_id": {"type": "integer"}}, "required": ["invoice_id"]},
    },
    "compare_invoice_with_goods_receipt": {
        "name": "compare_invoice_with_goods_receipt",
        "description": "Compare invoice with goods receipt (3-way match)",
        "parameters": {"type": "object", "properties": {"invoice_id": {"type": "integer"}}, "required": ["invoice_id"]},
    },
    "summarize_procurement_exceptions": {
        "name": "summarize_procurement_exceptions",
        "description": "Get summary of procurement exceptions",
        "parameters": {"type": "object", "properties": {}},
    },
    "get_approved_business_policy": {
        "name": "get_approved_business_policy",
        "description": "Get approved business policy",
        "parameters": {"type": "object", "properties": {"policy_name": {"type": "string"}}, "required": ["policy_name"]},
    },
}