import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base, get_db
from app.main import app
from app.models import (
    User, Role,
    Supplier, SupplierStatus,
    Product, Warehouse,
    InventoryBalance, InventoryMovement, MovementType,
    PurchaseOrder, PurchaseOrderLine, PurchaseOrderStatus,
    PurchaseRequisition, RequisitionStatus,
    GoodsReceipt, GoodsReceiptLine,
    SupplierInvoice, SupplierInvoiceLine, InvoiceStatus, PaymentStatus,
    ApprovalRecord,
    Conversation,
)
from app.core.security import get_password_hash, create_access_token
from app.services import (
    InventoryService,
    ProcurementService,
    InvoiceService,
)
from app.repositories import (
    SupplierRepository,
    ProductRepository,
    InventoryRepository,
    ProcurementRepository,
)
from httpx import AsyncClient, ASGITransport


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestAsyncSessionMaker = async_sessionmaker(test_engine, expire_on_commit=False)


async def create_test_db():
    print("Creating test database tables...")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully")


async def drop_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_test_session_and_client():
    """Create a fresh database session and async client for testing."""
    session = TestAsyncSessionMaker()
    def override_get_db():
        yield session
    app.dependency_overrides[get_db] = override_get_db
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    return session, client


async def cleanup_session_and_client(session, client):
    try:
        await session.rollback()
    finally:
        await session.close()
        await client.aclose()
        app.dependency_overrides.clear()


# Pytest fixtures
@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    await create_test_db()
    yield
    await drop_test_db()


# Test helper functions
async def create_test_user(db: AsyncSession, email: str, role: Role = Role.EMPLOYEE) -> User:
    user = User(
        email=email,
        hashed_password=get_password_hash("test123"),
        full_name="Test User",
        role=role,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return user


async def create_test_supplier(db: AsyncSession) -> Supplier:
    supplier = Supplier(
        supplier_code="TEST-001",
        name="Test Supplier",
        contact_name="John Doe",
        contact_email="john@test.com",
        status=SupplierStatus.ACTIVE,
        lead_time_days=7,
        payment_terms_days=30,
        currency="USD",
    )
    db.add(supplier)
    await db.flush()
    return supplier


async def create_test_product(db: AsyncSession) -> Product:
    product = Product(
        sku="TEST-SKU",
        name="Test Product",
        unit_of_measure="EA",
        standard_cost=Decimal("10.00"),
        reorder_level=10,
        is_active=True,
    )
    db.add(product)
    await db.flush()
    return product


async def create_test_warehouse(db: AsyncSession) -> Warehouse:
    warehouse = Warehouse(
        code="TEST-WH",
        name="Test Warehouse",
        is_active=True,
    )
    db.add(warehouse)
    await db.flush()
    return warehouse


async def get_auth_headers(user: User) -> dict:
    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role.value})
    return {"Authorization": f"Bearer {token}"}


async def get_test_session_and_client():
    """Create a fresh database session and async client for testing."""
    session = TestAsyncSessionMaker()
    def override_get_db():
        yield session
    app.dependency_overrides[get_db] = override_get_db
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    return session, client


async def cleanup_session_and_client(session, client):
    try:
        await session.rollback()
    finally:
        await session.close()
        await client.aclose()
        app.dependency_overrides.clear()


# Pytest fixtures
@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    await create_test_db()
    yield
    await drop_test_db()


# Test helper functions
async def setup_basic_test_data(db: AsyncSession):
    """Create basic test data: user, admin, supplier, product, warehouse."""
    test_user = await create_test_user(db, "test@example.com", Role.EMPLOYEE)
    admin_user = await create_test_user(db, "admin@example.com", Role.ADMINISTRATOR)
    supplier = await create_test_supplier(db)
    product = await create_test_product(db)
    warehouse = await create_test_warehouse(db)
    return test_user, admin_user, supplier, product, warehouse


# Tests
class TestInventoryCalculations:
    @pytest.mark.asyncio
    async def test_available_quantity_calculation(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            
            balance = InventoryBalance(
                product_id=product.id,
                warehouse_id=warehouse.id,
                quantity_on_hand=100,
                reserved_quantity=20,
            )
            assert balance.available_quantity == 80
        finally:
            await cleanup_session_and_client(session, client)

    @pytest.mark.asyncio
    async def test_available_quantity_zero_when_fully_reserved(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            
            balance = InventoryBalance(
                product_id=product.id,
                warehouse_id=warehouse.id,
                quantity_on_hand=50,
                reserved_quantity=50,
            )
            assert balance.available_quantity == 0
        finally:
            await cleanup_session_and_client(session, client)


class TestPurchaseOrderLifecycle:
    @pytest.mark.asyncio
    async def test_po_status_transitions(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            
            po = PurchaseOrder(
                po_number="TEST-PO-001",
                supplier_id=supplier.id,
                status=PurchaseOrderStatus.DRAFT,
                order_date=datetime.utcnow(),
                currency="USD",
                total_amount=Decimal("1000.00"),
                created_by=admin_user.id,
            )
            session.add(po)
            await session.flush()

            assert po.status == PurchaseOrderStatus.DRAFT

            po.status = PurchaseOrderStatus.PENDING_APPROVAL
            await session.flush()
            assert po.status == PurchaseOrderStatus.PENDING_APPROVAL

            po.status = PurchaseOrderStatus.APPROVED
            po.approved_by = admin_user.id
            po.approved_at = datetime.utcnow()
            await session.flush()
            assert po.status == PurchaseOrderStatus.APPROVED
        finally:
            await cleanup_session_and_client(session, client)


class TestThreeWayMatching:
    @pytest.mark.asyncio
    async def test_invoice_match_success(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            
            po = PurchaseOrder(
                po_number="TEST-PO-MATCH",
                supplier_id=supplier.id,
                status=PurchaseOrderStatus.RECEIVED,
                order_date=datetime.utcnow() - timedelta(days=10),
                expected_delivery_date=datetime.utcnow() - timedelta(days=5),
                actual_delivery_date=datetime.utcnow() - timedelta(days=5),
                currency="USD",
                total_amount=Decimal("1000.00"),
                created_by=admin_user.id,
                approved_by=admin_user.id,
                approved_at=datetime.utcnow() - timedelta(days=9),
            )
            session.add(po)
            await session.flush()

            po_line = PurchaseOrderLine(
                purchase_order_id=po.id,
                product_id=product.id,
                line_number=1,
                quantity_ordered=100,
                quantity_received=100,
                unit_price=Decimal("10.00"),
                currency="USD",
                line_total=Decimal("1000.00"),
            )
            session.add(po_line)
            await session.flush()

            gr = GoodsReceipt(
                gr_number="TEST-GR-001",
                purchase_order_id=po.id,
                receipt_date=datetime.utcnow() - timedelta(days=5),
                warehouse_id=warehouse.id,
                received_by=admin_user.id,
            )
            session.add(gr)
            await session.flush()

            gr_line = GoodsReceiptLine(
                goods_receipt_id=gr.id,
                po_line_id=po_line.id,
                product_id=product.id,
                quantity_received=100,
                quantity_accepted=100,
                quantity_rejected=0,
            )
            session.add(gr_line)
            await session.flush()

            invoice = SupplierInvoice(
                invoice_number="TEST-INV-001",
                supplier_id=supplier.id,
                purchase_order_id=po.id,
                status=InvoiceStatus.SUBMITTED,
                invoice_date=datetime.utcnow() - timedelta(days=3),
                due_date=datetime.utcnow() + timedelta(days=27),
                currency="USD",
                total_amount=Decimal("1000.00"),
            )
            session.add(invoice)
            await session.flush()

            inv_line = SupplierInvoiceLine(
                invoice_id=invoice.id,
                po_line_id=po_line.id,
                product_id=product.id,
                line_number=1,
                quantity_invoiced=100,
                unit_price=Decimal("10.00"),
                currency="USD",
                line_total=Decimal("1000.00"),
            )
            session.add(inv_line)
            await session.flush()

            service = InvoiceService(session)
            result = await service.three_way_match(invoice.id)

            assert result["matched"] is True
            assert len(result["discrepancies"]) == 0
        finally:
            await cleanup_session_and_client(session, client)

    @pytest.mark.asyncio
    async def test_invoice_quantity_discrepancy(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            
            po = PurchaseOrder(
                po_number="TEST-PO-DISC-QTY",
                supplier_id=supplier.id,
                status=PurchaseOrderStatus.RECEIVED,
                order_date=datetime.utcnow() - timedelta(days=10),
                expected_delivery_date=datetime.utcnow() - timedelta(days=5),
                actual_delivery_date=datetime.utcnow() - timedelta(days=5),
                currency="USD",
                total_amount=Decimal("1000.00"),
                created_by=admin_user.id,
                approved_by=admin_user.id,
                approved_at=datetime.utcnow() - timedelta(days=9),
            )
            session.add(po)
            await session.flush()

            po_line = PurchaseOrderLine(
                purchase_order_id=po.id,
                product_id=product.id,
                line_number=1,
                quantity_ordered=100,
                quantity_received=90,
                unit_price=Decimal("10.00"),
                currency="USD",
                line_total=Decimal("1000.00"),
            )
            session.add(po_line)
            await session.flush()

            gr = GoodsReceipt(
                gr_number="TEST-GR-DISC-001",
                purchase_order_id=po.id,
                receipt_date=datetime.utcnow() - timedelta(days=5),
                warehouse_id=warehouse.id,
                received_by=admin_user.id,
            )
            session.add(gr)
            await session.flush()

            gr_line = GoodsReceiptLine(
                goods_receipt_id=gr.id,
                po_line_id=po_line.id,
                product_id=product.id,
                quantity_received=90,
                quantity_accepted=90,
                quantity_rejected=0,
            )
            session.add(gr_line)
            await session.flush()

            invoice = SupplierInvoice(
                invoice_number="TEST-INV-DISC-001",
                supplier_id=supplier.id,
                purchase_order_id=po.id,
                status=InvoiceStatus.SUBMITTED,
                invoice_date=datetime.utcnow() - timedelta(days=3),
                due_date=datetime.utcnow() + timedelta(days=27),
                currency="USD",
                total_amount=Decimal("1000.00"),
            )
            session.add(invoice)
            await session.flush()

            inv_line = SupplierInvoiceLine(
                invoice_id=invoice.id,
                po_line_id=po_line.id,
                product_id=product.id,
                line_number=1,
                quantity_invoiced=100,
                unit_price=Decimal("10.00"),
                currency="USD",
                line_total=Decimal("1000.00"),
            )
            session.add(inv_line)
            await session.flush()

            service = InvoiceService(session)
            result = await service.three_way_match(invoice.id)

            assert result["matched"] is False
            assert len(result["discrepancies"]) > 0
            assert any("Invoiced qty 100 vs Received qty 90" in d for d in result["discrepancies"])
        finally:
            await cleanup_session_and_client(session, client)


class TestAuthEndpoints:
    @pytest.mark.asyncio
    async def test_login_success(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            
            response = await client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "test123",
            })
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
        finally:
            await cleanup_session_and_client(session, client)

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            
            response = await client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "wrongpassword",
            })
            assert response.status_code == 401
        finally:
            await cleanup_session_and_client(session, client)

    @pytest.mark.asyncio
    async def test_get_current_user(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            headers = await get_auth_headers(test_user)
            
            response = await client.get("/api/v1/auth/me", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"
        finally:
            await cleanup_session_and_client(session, client)


class TestSupplierEndpoints:
    @pytest.mark.asyncio
    async def test_create_supplier(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            headers = await get_auth_headers(admin_user)
            
            response = await client.post("/api/v1/suppliers", json={
                "supplier_code": "NEW-001",
                "name": "New Supplier",
                "contact_name": "Jane Smith",
                "contact_email": "jane@new.com",
                "status": "active",
                "lead_time_days": 10,
                "payment_terms_days": 30,
                "currency": "USD",
            }, headers=headers)
            assert response.status_code == 201
            data = response.json()
            assert data["supplier_code"] == "NEW-001"
            assert data["name"] == "New Supplier"
        finally:
            await cleanup_session_and_client(session, client)

    @pytest.mark.asyncio
    async def test_list_suppliers(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            headers = await get_auth_headers(test_user)
            
            response = await client.get("/api/v1/suppliers", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert len(data["items"]) >= 1
        finally:
            await cleanup_session_and_client(session, client)


class TestProductEndpoints:
    @pytest.mark.asyncio
    async def test_create_product(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            headers = await get_auth_headers(admin_user)
            
            response = await client.post("/api/v1/products", json={
                "sku": "NEW-SKU-001",
                "name": "New Product",
                "unit_of_measure": "EA",
                "standard_cost": 25.00,
                "reorder_level": 15,
            }, headers=headers)
            assert response.status_code == 201
            data = response.json()
            assert data["sku"] == "NEW-SKU-001"
        finally:
            await cleanup_session_and_client(session, client)

    @pytest.mark.asyncio
    async def test_duplicate_sku_rejected(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            headers = await get_auth_headers(admin_user)
            
            response = await client.post("/api/v1/products", json={
                "sku": product.sku,
                "name": "Duplicate Product",
                "unit_of_measure": "EA",
            }, headers=headers)
            assert response.status_code == 400
        finally:
            await cleanup_session_and_client(session, client)


class TestInventoryEndpoints:
    @pytest.mark.asyncio
    async def test_get_low_stock(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            headers = await get_auth_headers(test_user)
            
            balance = InventoryBalance(
                product_id=product.id,
                warehouse_id=warehouse.id,
                quantity_on_hand=5,
                reserved_quantity=0,
            )
            product.reorder_level = 10
            session.add(balance)
            await session.flush()

            response = await client.get("/api/v1/inventory/low-stock", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert len(data) >= 1
            assert any(item["product_sku"] == product.sku for item in data)
        finally:
            await cleanup_session_and_client(session, client)


class TestProcurementEndpoints:
    @pytest.mark.asyncio
    async def test_create_purchase_order(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            headers = await get_auth_headers(admin_user)
            
            response = await client.post("/api/v1/purchase-orders", json={
                "po_number": "NEW-PO-001",
                "supplier_id": supplier.id,
                "status": "draft",
                "currency": "USD",
                "lines": [
                    {
                        "product_id": product.id,
                        "line_number": 1,
                        "quantity_ordered": 50,
                        "unit_price": 20.00,
                    }
                ],
            }, headers=headers)
            assert response.status_code == 201
            data = response.json()
            assert data["po_number"] == "NEW-PO-001"
            assert data["total_amount"] == 1000.00
        finally:
            await cleanup_session_and_client(session, client)

    @pytest.mark.asyncio
    async def test_approve_purchase_order(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            headers = await get_auth_headers(admin_user)
            
            po = PurchaseOrder(
                po_number="PO-TO-APPROVE",
                supplier_id=supplier.id,
                status=PurchaseOrderStatus.PENDING_APPROVAL,
                order_date=datetime.utcnow(),
                currency="USD",
                total_amount=Decimal("500.00"),
                created_by=admin_user.id,
            )
            session.add(po)
            await session.flush()

            line = PurchaseOrderLine(
                purchase_order_id=po.id,
                product_id=product.id,
                line_number=1,
                quantity_ordered=50,
                unit_price=Decimal("10.00"),
                currency="USD",
                line_total=Decimal("500.00"),
            )
            session.add(line)
            await session.flush()

            response = await client.post(f"/api/v1/purchase-orders/{po.id}/approve", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "approved"
        finally:
            await cleanup_session_and_client(session, client)


class TestInvoiceEndpoints:
    @pytest.mark.asyncio
    async def test_create_invoice(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            headers = await get_auth_headers(admin_user)
            
            po = PurchaseOrder(
                po_number="PO-FOR-INV",
                supplier_id=supplier.id,
                status=PurchaseOrderStatus.APPROVED,
                order_date=datetime.utcnow(),
                currency="USD",
                total_amount=Decimal("500.00"),
                created_by=admin_user.id,
                approved_by=admin_user.id,
                approved_at=datetime.utcnow(),
            )
            session.add(po)
            await session.flush()

            line = PurchaseOrderLine(
                purchase_order_id=po.id,
                product_id=product.id,
                line_number=1,
                quantity_ordered=50,
                unit_price=Decimal("10.00"),
                currency="USD",
                line_total=Decimal("500.00"),
            )
            session.add(line)
            await session.flush()

            response = await client.post("/api/v1/supplier-invoices", json={
                "invoice_number": "INV-NEW-001",
                "supplier_id": supplier.id,
                "purchase_order_id": po.id,
                "status": "draft",
                "invoice_date": datetime.utcnow().isoformat(),
                "currency": "USD",
                "lines": [
                    {
                        "po_line_id": line.id,
                        "product_id": product.id,
                        "line_number": 1,
                        "quantity_invoiced": 50,
                        "unit_price": 10.00,
                    }
                ],
            }, headers=headers)
            assert response.status_code == 201
            data = response.json()
            assert data["invoice_number"] == "INV-NEW-001"
        finally:
            await cleanup_session_and_client(session, client)


class TestConversationEndpoints:
    @pytest.mark.asyncio
    async def test_create_conversation(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            headers = await get_auth_headers(test_user)
            
            response = await client.post("/api/v1/conversations", json={
                "title": "Test Conversation",
            }, headers=headers)
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Test Conversation"
        finally:
            await cleanup_session_and_client(session, client)

    @pytest.mark.asyncio
    async def test_send_message(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            headers = await get_auth_headers(test_user)
            
            conv = Conversation(
                user_id=test_user.id,
                title="Chat Test",
            )
            session.add(conv)
            await session.flush()

            response = await client.post(f"/api/v1/conversations/{conv.id}/messages", json={
                "message": "Hello",
            }, headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "conversation" in data
        finally:
            await cleanup_session_and_client(session, client)


class TestSecurity:
    @pytest.mark.asyncio
    async def test_unauthorized_access_blocked(self):
        session, client = await get_test_session_and_client()
        try:
            response = await client.get("/api/v1/suppliers")
            assert response.status_code == 401
        finally:
            await cleanup_session_and_client(session, client)

    @pytest.mark.asyncio
    async def test_role_based_access(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            headers = await get_auth_headers(test_user)
            
            response = await client.post("/api/v1/suppliers", json={
                "supplier_code": "TEST-ROLE",
                "name": "Test",
            }, headers=headers)
            assert response.status_code == 403
        finally:
            await cleanup_session_and_client(session, client)

    @pytest.mark.asyncio
    async def test_admin_can_create_supplier(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            headers = await get_auth_headers(admin_user)
            
            response = await client.post("/api/v1/suppliers", json={
                "supplier_code": "ADMIN-001",
                "name": "Admin Supplier",
            }, headers=headers)
            assert response.status_code == 201
        finally:
            await cleanup_session_and_client(session, client)


class TestTools:
    @pytest.mark.asyncio
    async def test_search_purchase_orders_tool(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            
            po = PurchaseOrder(
                po_number="TOOL-PO-001",
                supplier_id=supplier.id,
                status=PurchaseOrderStatus.APPROVED,
                order_date=datetime.utcnow(),
                currency="USD",
                total_amount=Decimal("1000.00"),
                created_by=admin_user.id,
                approved_by=admin_user.id,
                approved_at=datetime.utcnow(),
            )
            session.add(po)
            await session.flush()

            from app.tools import search_purchase_orders, ToolContext
            ctx = ToolContext(session, test_user.id)
            result = await search_purchase_orders(ctx, status="approved")
            assert result.success is True
            assert len(result.data["items"]) >= 1
        finally:
            await cleanup_session_and_client(session, client)

    @pytest.mark.asyncio
    async def test_get_inventory_balance_tool(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            
            balance = InventoryBalance(
                product_id=product.id,
                warehouse_id=warehouse.id,
                quantity_on_hand=100,
                reserved_quantity=10,
            )
            session.add(balance)
            await session.flush()

            from app.tools import get_inventory_balance, ToolContext
            ctx = ToolContext(session, test_user.id)
            result = await get_inventory_balance(ctx, product_id=product.id)
            assert result.success is True
            assert len(result.data["items"]) == 1
            assert result.data["items"][0]["available_quantity"] == 90
        finally:
            await cleanup_session_and_client(session, client)

    @pytest.mark.asyncio
    async def test_list_low_stock_tool(self):
        session, client = await get_test_session_and_client()
        try:
            test_user, admin_user, supplier, product, warehouse = await setup_basic_test_data(session)
            
            product.reorder_level = 20
            balance = InventoryBalance(
                product_id=product.id,
                warehouse_id=warehouse.id,
                quantity_on_hand=10,
                reserved_quantity=0,
            )
            session.add(balance)
            await session.flush()

            from app.tools import list_low_stock_products, ToolContext
            ctx = ToolContext(session, test_user.id)
            result = await list_low_stock_products(ctx)
            assert result.success is True
            assert len(result.data["items"]) >= 1
        finally:
            await cleanup_session_and_client(session, client)