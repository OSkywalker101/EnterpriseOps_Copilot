import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import async_session_maker, Base, engine
from app.models import (
    User, Role,
    Supplier, SupplierStatus,
    Product, Warehouse,
    InventoryBalance, InventoryMovement, MovementType,
    PurchaseRequisition, RequisitionStatus,
    PurchaseOrder, PurchaseOrderLine, PurchaseOrderStatus,
    ApprovalRecord,
    GoodsReceipt, GoodsReceiptLine,
    SupplierInvoice, SupplierInvoiceLine, InvoiceStatus, PaymentStatus,
)
from app.core.security import get_password_hash


async def seed_data():
    async with async_session_maker() as db:
        print("Seeding database...")
        
        # Create admin user
        admin = User(
            email="admin@enterpriseops.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role=Role.ADMINISTRATOR,
            department="IT",
            is_active=True,
        )
        db.add(admin)
        
        # Create procurement specialist
        proc_user = User(
            email="procurement@enterpriseops.com",
            hashed_password=get_password_hash("proc123"),
            full_name="Procurement Specialist",
            role=Role.PROCUREMENT_SPECIALIST,
            department="Procurement",
            is_active=True,
        )
        db.add(proc_user)
        
        # Create inventory manager
        inv_user = User(
            email="inventory@enterpriseops.com",
            hashed_password=get_password_hash("inv123"),
            full_name="Inventory Manager",
            role=Role.INVENTORY_MANAGER,
            department="Warehouse",
            is_active=True,
        )
        db.add(inv_user)
        
        # Create approver
        approver = User(
            email="approver@enterpriseops.com",
            hashed_password=get_password_hash("appr123"),
            full_name="Approval Manager",
            role=Role.APPROVER,
            department="Finance",
            is_active=True,
        )
        db.add(approver)
        
        # Create employee
        employee = User(
            email="employee@enterpriseops.com",
            hashed_password=get_password_hash("emp123"),
            full_name="John Employee",
            role=Role.EMPLOYEE,
            department="Operations",
            is_active=True,
        )
        db.add(employee)
        
        await db.flush()
        print("Users created")
        
        # Create warehouses
        warehouses = [
            Warehouse(code="WH-001", name="Main Warehouse", address="100 Industrial Blvd, City A", is_active=True),
            Warehouse(code="WH-002", name="Secondary Warehouse", address="200 Commerce St, City B", is_active=True),
            Warehouse(code="WH-003", name="Distribution Center", address="300 Logistics Way, City C", is_active=True),
        ]
        for wh in warehouses:
            db.add(wh)
        await db.flush()
        print("Warehouses created")
        
        # Create suppliers
        suppliers = [
            Supplier(supplier_code="SUP-001", name="Acme Corporation", contact_name="John Smith", contact_email="john@acme.com", contact_phone="+1-555-0101", address="100 Supplier Ave, Supplier City", status=SupplierStatus.ACTIVE, lead_time_days=7, payment_terms_days=30, currency="USD"),
            Supplier(supplier_code="SUP-002", name="Beta Limited", contact_name="Jane Doe", contact_email="jane@beta.com", contact_phone="+1-555-0102", address="200 Vendor Rd, Vendor Town", status=SupplierStatus.ACTIVE, lead_time_days=14, payment_terms_days=45, currency="USD"),
            Supplier(supplier_code="SUP-003", name="Gamma Inc", contact_name="Bob Wilson", contact_email="bob@gamma.com", contact_phone="+1-555-0103", address="300 Partner Ln, Partner City", status=SupplierStatus.ACTIVE, lead_time_days=5, payment_terms_days=30, currency="USD"),
            Supplier(supplier_code="SUP-004", name="Delta Company", contact_name="Alice Brown", contact_email="alice@delta.com", contact_phone="+1-555-0104", address="400 Supply St, Supply City", status=SupplierStatus.ACTIVE, lead_time_days=10, payment_terms_days=60, currency="USD"),
            Supplier(supplier_code="SUP-005", name="Epsilon LLC", contact_name="Charlie Davis", contact_email="charlie@epsilon.com", contact_phone="+1-555-0105", address="500 Source Blvd, Source Town", status=SupplierStatus.ACTIVE, lead_time_days=3, payment_terms_days=15, currency="USD"),
            Supplier(supplier_code="SUP-006", name="Zeta Suppliers", contact_name="Diana Miller", contact_email="diana@zeta.com", contact_phone="+1-555-0106", address="600 Material Way, Material City", status=SupplierStatus.ACTIVE, lead_time_days=21, payment_terms_days=30, currency="EUR"),
            Supplier(supplier_code="SUP-007", name="Eta Distributors", contact_name="Edward Garcia", contact_email="edward@eta.com", contact_phone="+1-555-0107", address="700 Goods Rd, Goods Town", status=SupplierStatus.ON_HOLD, lead_time_days=14, payment_terms_days=45, currency="USD"),
            Supplier(supplier_code="SUP-008", name="Theta Partners", contact_name="Fiona Rodriguez", contact_email="fiona@theta.com", contact_phone="+1-555-0108", address="800 Parts Ave, Parts City", status=SupplierStatus.ACTIVE, lead_time_days=7, payment_terms_days=30, currency="GBP"),
            Supplier(supplier_code="SUP-009", name="Iota Logistics", contact_name="George Martinez", contact_email="george@iota.com", contact_phone="+1-555-0109", address="900 Component St, Component Town", status=SupplierStatus.ACTIVE, lead_time_days=10, payment_terms_days=30, currency="USD"),
            Supplier(supplier_code="SUP-010", name="Kappa Industries", contact_name="Helen Anderson", contact_email="helen@kappa.com", contact_phone="+1-555-0110", address="1000 Hardware Blvd, Hardware City", status=SupplierStatus.INACTIVE, lead_time_days=30, payment_terms_days=60, currency="USD"),
        ]
        for sup in suppliers:
            db.add(sup)
        await db.flush()
        print("Suppliers created")
        
        # Create products
        products = [
            Product(sku="SKU-101", name="Steel Widget A", description="High-grade steel widget", unit_of_measure="EA", standard_cost=Decimal("15.50"), reorder_level=20, is_active=True),
            Product(sku="SKU-102", name="Aluminum Gadget B", description="Lightweight aluminum gadget", unit_of_measure="EA", standard_cost=Decimal("22.75"), reorder_level=15, is_active=True),
            Product(sku="SKU-103", name="Plastic Component C", description="Durable plastic component", unit_of_measure="EA", standard_cost=Decimal("8.25"), reorder_level=30, is_active=True),
            Product(sku="SKU-104", name="Copper Connector D", description="Copper electrical connector", unit_of_measure="EA", standard_cost=Decimal("12.00"), reorder_level=25, is_active=True),
            Product(sku="SKU-105", name="Rubber Seal E", description="Industrial rubber seal", unit_of_measure="EA", standard_cost=Decimal("3.50"), reorder_level=50, is_active=True),
            Product(sku="SKU-106", name="Brass Fitting F", description="Brass pipe fitting", unit_of_measure="EA", standard_cost=Decimal("18.90"), reorder_level=20, is_active=True),
            Product(sku="SKU-107", name="Stainless Bolt G", description="Stainless steel bolt M8", unit_of_measure="EA", standard_cost=Decimal("0.75"), reorder_level=100, is_active=True),
            Product(sku="SKU-108", name="Nylon Washer H", description="Nylon flat washer", unit_of_measure="EA", standard_cost=Decimal("0.25"), reorder_level=200, is_active=True),
            Product(sku="SKU-109", name="PVC Pipe I", description="PVC pipe 1 inch", unit_of_measure="M", standard_cost=Decimal("4.50"), reorder_level=50, is_active=True),
            Product(sku="SKU-110", name="Wire Cable J", description="Electrical wire 14 AWG", unit_of_measure="M", standard_cost=Decimal("1.20"), reorder_level=100, is_active=True),
            Product(sku="SKU-201", name="Hydraulic Valve K", description="Hydraulic control valve", unit_of_measure="EA", standard_cost=Decimal("85.00"), reorder_level=5, is_active=True),
            Product(sku="SKU-202", name="Pneumatic Cylinder L", description="Pneumatic cylinder 50mm", unit_of_measure="EA", standard_cost=Decimal("120.00"), reorder_level=3, is_active=True),
            Product(sku="SKU-203", name="Electric Motor M", description="3-phase electric motor 5HP", unit_of_measure="EA", standard_cost=Decimal("450.00"), reorder_level=2, is_active=True),
            Product(sku="SKU-204", name="Gearbox N", description="Planetary gearbox 10:1", unit_of_measure="EA", standard_cost=Decimal("320.00"), reorder_level=3, is_active=True),
            Product(sku="SKU-205", name="Bearing O", description="Ball bearing 6205", unit_of_measure="EA", standard_cost=Decimal("8.50"), reorder_level=30, is_active=True),
            Product(sku="SKU-206", name="Sensor P", description="Proximity sensor inductive", unit_of_measure="EA", standard_cost=Decimal("45.00"), reorder_level=10, is_active=True),
            Product(sku="SKU-207", name="Controller Q", description="PLC controller module", unit_of_measure="EA", standard_cost=Decimal("280.00"), reorder_level=5, is_active=True),
            Product(sku="SKU-208", name="Drive R", description="VFD drive 10HP", unit_of_measure="EA", standard_cost=Decimal("650.00"), reorder_level=3, is_active=True),
            Product(sku="SKU-209", name="Filter S", description="Air filter element", unit_of_measure="EA", standard_cost=Decimal("25.00"), reorder_level=20, is_active=True),
            Product(sku="SKU-210", name="Lubricant T", description="Industrial lubricant 5L", unit_of_measure="EA", standard_cost=Decimal("35.00"), reorder_level=15, is_active=True),
            Product(sku="SKU-301", name="Safety Helmet U", description="Construction safety helmet", unit_of_measure="EA", standard_cost=Decimal("28.00"), reorder_level=25, is_active=True),
            Product(sku="SKU-302", name="Safety Gloves V", description="Cut-resistant gloves", unit_of_measure="PR", standard_cost=Decimal("12.00"), reorder_level=50, is_active=True),
            Product(sku="SKU-303", name="Safety Boots W", description="Steel-toe safety boots", unit_of_measure="PR", standard_cost=Decimal("85.00"), reorder_level=15, is_active=True),
            Product(sku="SKU-304", name="Fire Extinguisher X", description="ABC fire extinguisher 5kg", unit_of_measure="EA", standard_cost=Decimal("65.00"), reorder_level=10, is_active=True),
            Product(sku="SKU-305", name="First Aid Kit Y", description="Industrial first aid kit", unit_of_measure="EA", standard_cost=Decimal("45.00"), reorder_level=8, is_active=True),
            Product(sku="SKU-306", name="Warning Signs Z", description="Safety warning signs set", unit_of_measure="SET", standard_cost=Decimal("35.00"), reorder_level=20, is_active=True),
            Product(sku="SKU-307", name="Ear Protection AA", description="Noise-canceling ear muffs", unit_of_measure="EA", standard_cost=Decimal("22.00"), reorder_level=30, is_active=True),
            Product(sku="SKU-308", name="Eye Protection BB", description="Safety goggles anti-fog", unit_of_measure="EA", standard_cost=Decimal("15.00"), reorder_level=40, is_active=True),
            Product(sku="SKU-309", name="Respirator CC", description="Half-face respirator", unit_of_measure="EA", standard_cost=Decimal("55.00"), reorder_level=12, is_active=True),
            Product(sku="SKU-310", name="Fall Protection DD", description="Safety harness full body", unit_of_measure="EA", standard_cost=Decimal("180.00"), reorder_level=5, is_active=True),
        ]
        for prod in products:
            db.add(prod)
        await db.flush()
        print("Products created")
        
        # Create inventory balances
        for product in products:
            for warehouse in warehouses:
                qty = 0
                if product.sku in ["SKU-101", "SKU-102", "SKU-103"]:
                    qty = 100 if warehouse.code == "WH-001" else 50
                elif product.sku in ["SKU-104", "SKU-105"]:
                    qty = 5 if warehouse.code == "WH-001" else 10  # Low stock
                elif product.sku in ["SKU-201", "SKU-202"]:
                    qty = 10 if warehouse.code == "WH-001" else 5
                elif product.sku in ["SKU-208"]:
                    qty = 0 if warehouse.code == "WH-001" else 2  # Zero stock
                else:
                    qty = 50 if warehouse.code == "WH-001" else 25
                
                balance = InventoryBalance(
                    product_id=product.id,
                    warehouse_id=warehouse.id,
                    quantity_on_hand=qty,
                    reserved_quantity=0,
                    last_movement_date=datetime.utcnow() - timedelta(days=5),
                )
                db.add(balance)
        await db.flush()
        print("Inventory balances created")
        
        # Create purchase orders
        base_date = datetime.utcnow() - timedelta(days=60)
        
        po_data = [
            ("PO-1001", 0, PurchaseOrderStatus.PENDING_APPROVAL, base_date + timedelta(days=5), base_date + timedelta(days=20), 15000.00),
            ("PO-1002", 1, PurchaseOrderStatus.PARTIALLY_RECEIVED, base_date + timedelta(days=10), base_date + timedelta(days=15), 8500.00),
            ("PO-1003", 2, PurchaseOrderStatus.PENDING_APPROVAL, base_date + timedelta(days=15), base_date + timedelta(days=30), 22000.00),
            ("PO-1004", 3, PurchaseOrderStatus.APPROVED, base_date + timedelta(days=20), base_date + timedelta(days=35), 12500.00),
            ("PO-1005", 4, PurchaseOrderStatus.ORDERED, base_date + timedelta(days=25), base_date + timedelta(days=20), 18000.00),  # Overdue
            ("PO-1006", 5, PurchaseOrderStatus.RECEIVED, base_date + timedelta(days=30), base_date + timedelta(days=40), 9500.00),
            ("PO-1007", 6, PurchaseOrderStatus.PENDING_APPROVAL, base_date + timedelta(days=35), base_date + timedelta(days=50), 35000.00),
            ("PO-1008", 7, PurchaseOrderStatus.APPROVED, base_date + timedelta(days=40), base_date + timedelta(days=55), 7200.00),
            ("PO-1009", 8, PurchaseOrderStatus.PARTIALLY_RECEIVED, base_date + timedelta(days=45), base_date + timedelta(days=60), 14000.00),
            ("PO-1010", 9, PurchaseOrderStatus.CANCELLED, base_date + timedelta(days=50), base_date + timedelta(days=65), 5000.00),
        ]
        
        for i, (po_num, sup_idx, status, order_date, exp_date, total) in enumerate(po_data):
            po = PurchaseOrder(
                po_number=po_num,
                supplier_id=suppliers[sup_idx].id,
                status=status,
                order_date=order_date,
                expected_delivery_date=exp_date,
                currency="USD",
                total_amount=Decimal(str(total)),
                created_by=proc_user.id,
                approved_by=approver.id if status in [PurchaseOrderStatus.APPROVED, PurchaseOrderStatus.ORDERED, PurchaseOrderStatus.PARTIALLY_RECEIVED, PurchaseOrderStatus.RECEIVED] else None,
                approved_at=order_date + timedelta(days=2) if status in [PurchaseOrderStatus.APPROVED, PurchaseOrderStatus.ORDERED, PurchaseOrderStatus.PARTIALLY_RECEIVED, PurchaseOrderStatus.RECEIVED] else None,
            )
            db.add(po)
        await db.flush()
        
        pos = list(await db.execute(select(PurchaseOrder)))
        pos = [p[0] for p in pos]
        print("Purchase orders created")
        
        # Create PO lines
        po_lines_data = [
            # PO-1001
            (0, 0, 1, 100, Decimal("15.50")),
            (0, 1, 2, 200, Decimal("8.25")),
            # PO-1002
            (1, 2, 1, 50, Decimal("22.75")),
            (1, 3, 2, 100, Decimal("12.00")),
            # PO-1003
            (2, 10, 1, 5, Decimal("85.00")),
            (2, 11, 2, 3, Decimal("120.00")),
            # PO-1004
            (3, 4, 1, 200, Decimal("3.50")),
            (3, 5, 2, 150, Decimal("18.90")),
            # PO-1005
            (4, 6, 1, 500, Decimal("0.75")),
            (4, 7, 2, 1000, Decimal("0.25")),
            # PO-1006
            (5, 8, 1, 100, Decimal("4.50")),
            (5, 9, 2, 200, Decimal("1.20")),
            # PO-1007
            (6, 12, 1, 2, Decimal("450.00")),
            (6, 13, 2, 3, Decimal("320.00")),
            # PO-1008
            (7, 14, 1, 50, Decimal("8.50")),
            (7, 15, 2, 20, Decimal("45.00")),
            # PO-1009
            (8, 16, 1, 3, Decimal("280.00")),
            (8, 17, 2, 2, Decimal("650.00")),
            # PO-1010
            (9, 18, 1, 30, Decimal("25.00")),
            (9, 19, 2, 20, Decimal("35.00")),
        ]
        
        for po_idx, prod_idx, line_num, qty, price in po_lines_data:
            line = PurchaseOrderLine(
                purchase_order_id=pos[po_idx].id,
                product_id=products[prod_idx].id,
                line_number=line_num,
                quantity_ordered=qty,
                quantity_received=0,
                unit_price=price,
                currency="USD",
                line_total=price * qty,
            )
            db.add(line)
        await db.flush()
        
        # Update PO-1002 as partially received
        po2_lines = await db.execute(select(PurchaseOrderLine).where(PurchaseOrderLine.purchase_order_id == pos[1].id))
        for line in po2_lines.scalars():
            line.quantity_received = line.quantity_ordered // 2
        
        # Update PO-1006 as received
        po6_lines = await db.execute(select(PurchaseOrderLine).where(PurchaseOrderLine.purchase_order_id == pos[5].id))
        for line in po6_lines.scalars():
            line.quantity_received = line.quantity_ordered
        
        # Update PO-1009 as partially received
        po9_lines = await db.execute(select(PurchaseOrderLine).where(PurchaseOrderLine.purchase_order_id == pos[8].id))
        for line in po9_lines.scalars():
            line.quantity_received = line.quantity_ordered // 3
        
        await db.flush()
        print("PO lines created")
        
        # Create goods receipts
        gr_data = [
            ("GR-3001", pos[1].id, warehouses[0].id, proc_user.id, base_date + timedelta(days=12)),  # PO-1002 partial
            ("GR-3002", pos[5].id, warehouses[0].id, proc_user.id, base_date + timedelta(days=38)),  # PO-1006 full
            ("GR-3003", pos[8].id, warehouses[1].id, proc_user.id, base_date + timedelta(days=50)),  # PO-1009 partial
        ]
        
        for gr_num, po_id, wh_id, recv_by, recv_date in gr_data:
            gr = GoodsReceipt(
                gr_number=gr_num,
                purchase_order_id=po_id,
                warehouse_id=wh_id,
                received_by=recv_by,
                receipt_date=recv_date,
            )
            db.add(gr)
        await db.flush()
        
        grs = list(await db.execute(select(GoodsReceipt)))
        grs = [g[0] for g in grs]
        
        # Create GR lines
        gr_lines_data = [
            # GR-3001 for PO-1002
            (0, pos[1].id, 0, 25, 25),  # 25 of 50 received
            (0, pos[1].id, 1, 50, 50),  # 50 of 100 received
            # GR-3002 for PO-1006
            (1, pos[5].id, 0, 100, 100),  # Full
            (1, pos[5].id, 1, 200, 200),  # Full
            # GR-3003 for PO-1009
            (2, pos[8].id, 0, 1, 1),  # 1 of 3 received
            (2, pos[8].id, 1, 1, 1),  # 1 of 2 received
        ]
        
        po_lines_result = await db.execute(select(PurchaseOrderLine))
        po_lines_by_po = {}
        for l in po_lines_result.scalars().all():
            po_lines_by_po.setdefault(l.purchase_order_id, []).append(l)
        
        for gr_idx, po_id, line_idx, qty_recv, qty_acc in gr_lines_data:
            po_line = po_lines_by_po.get(po_id, [])[line_idx]
            gr_line = GoodsReceiptLine(
                goods_receipt_id=grs[gr_idx].id,
                po_line_id=po_line.id,
                product_id=po_line.product_id,
                quantity_received=qty_recv,
                quantity_accepted=qty_acc,
                quantity_rejected=qty_recv - qty_acc,
            )
            db.add(gr_line)
        await db.flush()
        print("Goods receipts created")
        
        # Create supplier invoices
        inv_data = [
            ("INV-2001", suppliers[0].id, pos[0].id, InvoiceStatus.MATCHED, base_date + timedelta(days=10), base_date + timedelta(days=40), Decimal("15000.00")),
            ("INV-2002", suppliers[1].id, pos[1].id, InvoiceStatus.DISCREPANCY, base_date + timedelta(days=15), base_date + timedelta(days=45), Decimal("8500.00")),
            ("INV-2003", suppliers[2].id, pos[2].id, InvoiceStatus.SUBMITTED, base_date + timedelta(days=20), base_date + timedelta(days=50), Decimal("22000.00")),
            ("INV-2004", suppliers[3].id, pos[3].id, InvoiceStatus.MATCHED, base_date + timedelta(days=25), base_date + timedelta(days=55), Decimal("12500.00")),
            ("INV-2005", suppliers[4].id, pos[4].id, InvoiceStatus.DISCREPANCY, base_date + timedelta(days=30), base_date + timedelta(days=45), Decimal("18000.00")),
            ("INV-2006", suppliers[5].id, pos[5].id, InvoiceStatus.MATCHED, base_date + timedelta(days=40), base_date + timedelta(days=70), Decimal("9500.00")),
            ("INV-2007", suppliers[6].id, pos[6].id, InvoiceStatus.SUBMITTED, base_date + timedelta(days=45), base_date + timedelta(days=75), Decimal("35000.00")),
        ]
        
        for inv_num, sup_id, po_id, status, inv_date, due_date, total in inv_data:
            inv = SupplierInvoice(
                invoice_number=inv_num,
                supplier_id=sup_id,
                purchase_order_id=po_id,
                status=status,
                invoice_date=inv_date,
                due_date=due_date,
                currency="USD",
                total_amount=total,
            )
            db.add(inv)
        await db.flush()
        
        invs = list(await db.execute(select(SupplierInvoice)))
        invs = [i[0] for i in invs]
        
        # Create invoice lines - (inv_idx, line_idx, prod_idx, qty, price)
        inv_lines_data = [
            # INV-2001 for PO-1001 (matching)
            (0, 0, 1, 100, Decimal("15.50")),
            (0, 1, 2, 200, Decimal("8.25")),
            # INV-2002 for PO-1002 (quantity discrepancy - invoiced 50 but received 25)
            (1, 0, 2, 50, Decimal("22.75")),
            (1, 1, 3, 100, Decimal("12.00")),
            # INV-2003 for PO-1003
            (2, 0, 10, 5, Decimal("85.00")),
            (2, 1, 11, 3, Decimal("120.00")),
            # INV-2004 for PO-1004
            (3, 0, 4, 200, Decimal("3.50")),
            (3, 1, 5, 150, Decimal("18.90")),
            # INV-2005 for PO-1005 (amount discrepancy)
            (4, 0, 6, 500, Decimal("0.80")),  # Different price
            (4, 1, 7, 1000, Decimal("0.25")),
            # INV-2006 for PO-1006
            (5, 0, 8, 100, Decimal("4.50")),
            (5, 1, 9, 200, Decimal("1.20")),
            # INV-2007 for PO-1007
            (6, 0, 12, 2, Decimal("450.00")),
            (6, 1, 13, 3, Decimal("320.00")),
        ]
        
        for inv_idx, line_idx, prod_idx, qty, price in inv_lines_data:
            po_line = po_lines_by_po.get(pos[inv_idx].id, [])[line_idx] if inv_idx < len(pos) else None
            line = SupplierInvoiceLine(
                invoice_id=invs[inv_idx].id,
                po_line_id=po_line.id if po_line else None,
                product_id=products[prod_idx].id,
                line_number=line_idx + 1,
                quantity_invoiced=qty,
                unit_price=price,
                currency="USD",
                line_total=price * qty,
            )
            db.add(line)
        await db.flush()
        print("Supplier invoices created")
        
        # Create approval records
        approvals = [
            ApprovalRecord(purchase_order_id=pos[0].id, approver_id=approver.id, action="pending", comments="Awaiting approval"),
            ApprovalRecord(purchase_order_id=pos[2].id, approver_id=approver.id, action="pending", comments="Awaiting approval"),
            ApprovalRecord(purchase_order_id=pos[3].id, approver_id=approver.id, action="approved", comments="Approved"),
            ApprovalRecord(purchase_order_id=pos[4].id, approver_id=approver.id, action="approved", comments="Approved"),
            ApprovalRecord(purchase_order_id=pos[5].id, approver_id=approver.id, action="approved", comments="Approved"),
            ApprovalRecord(purchase_order_id=pos[6].id, approver_id=approver.id, action="pending", comments="Awaiting approval"),
            ApprovalRecord(purchase_order_id=pos[7].id, approver_id=approver.id, action="approved", comments="Approved"),
            ApprovalRecord(purchase_order_id=pos[8].id, approver_id=approver.id, action="approved", comments="Approved"),
        ]
        for appr in approvals:
            db.add(appr)
        
        await db.commit()
        print("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_data())