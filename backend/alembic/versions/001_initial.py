"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('employee', 'procurement_specialist', 'inventory_manager', 'approver', 'administrator', name='role'), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('warehouse_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_email_active', 'users', ['email', 'is_active'])

    op.create_table(
        'warehouses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )

    op.create_table(
        'suppliers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('supplier_code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('contact_name', sa.String(length=255), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'on_hold', name='supplierstatus'), nullable=False, default='active'),
        sa.Column('lead_time_days', sa.Integer(), nullable=False, default=0),
        sa.Column('payment_terms_days', sa.Integer(), nullable=False, default=30),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('supplier_code'),
    )
    op.create_index('ix_suppliers_status_code', 'suppliers', ['status', 'supplier_code'])

    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sku', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('unit_of_measure', sa.String(length=20), nullable=False, default='EA'),
        sa.Column('standard_cost', sa.Numeric(precision=12, scale=4), nullable=True),
        sa.Column('reorder_level', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sku'),
    )
    op.create_index('ix_products_sku_active', 'products', ['sku', 'is_active'])

    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])

    op.create_table(
        'conversation_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', sa.Text(), nullable=True),
        sa.Column('tool_results', sa.Text(), nullable=True),
        sa.Column('citations', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_messages_conversation_created', 'conversation_messages', ['conversation_id', 'created_at'])

    op.create_table(
        'purchase_requisitions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('requisition_number', sa.String(length=50), nullable=False),
        sa.Column('requested_by', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('draft', 'submitted', 'approved', 'rejected', 'converted_to_po', name='requisitionstatus'), nullable=False, default='draft'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('required_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['requested_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('requisition_number'),
    )

    op.create_table(
        'purchase_orders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('po_number', sa.String(length=50), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('requisition_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'pending_approval', 'approved', 'ordered', 'partially_received', 'received', 'cancelled', name='purchaseorderstatus'), nullable=False, default='draft'),
        sa.Column('order_date', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('expected_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('total_amount', sa.Numeric(precision=14, scale=2), nullable=False, default=0),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id']),
        sa.ForeignKeyConstraint(['requisition_id'], ['purchase_requisitions.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('po_number'),
    )
    op.create_index('ix_po_status_supplier_date', 'purchase_orders', ['status', 'supplier_id', 'order_date'])
    op.create_index('ix_po_expected_delivery', 'purchase_orders', ['expected_delivery_date'])

    op.create_table(
        'purchase_order_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('purchase_order_id', sa.Integer(), nullable=False),
        sa.Column('requisition_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('quantity_ordered', sa.Integer(), nullable=False),
        sa.Column('quantity_received', sa.Integer(), nullable=False, default=0),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('line_total', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requisition_id'], ['purchase_requisitions.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('purchase_order_id', 'line_number', name='uq_po_line_number'),
    )

    op.create_table(
        'approval_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('purchase_order_id', sa.Integer(), nullable=False),
        sa.Column('approver_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_approval_po_approver', 'approval_records', ['purchase_order_id', 'approver_id'])

    op.create_table(
        'goods_receipts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('gr_number', sa.String(length=50), nullable=False),
        sa.Column('purchase_order_id', sa.Integer(), nullable=False),
        sa.Column('receipt_date', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('received_by', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id']),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id']),
        sa.ForeignKeyConstraint(['received_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('gr_number'),
    )

    op.create_table(
        'goods_receipt_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('goods_receipt_id', sa.Integer(), nullable=False),
        sa.Column('po_line_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity_received', sa.Integer(), nullable=False),
        sa.Column('quantity_accepted', sa.Integer(), nullable=False),
        sa.Column('quantity_rejected', sa.Integer(), nullable=False, default=0),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['goods_receipt_id'], ['goods_receipts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['po_line_id'], ['purchase_order_lines.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_gr_line_po_line', 'goods_receipt_lines', ['po_line_id'])

    op.create_table(
        'supplier_invoices',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('invoice_number', sa.String(length=50), nullable=False),
        sa.Column('supplier_id', sa.Integer(), nullable=False),
        sa.Column('purchase_order_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'submitted', 'matched', 'discrepancy', 'approved', 'paid', 'cancelled', name='invoicestatus'), nullable=False, default='draft'),
        sa.Column('invoice_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('total_amount', sa.Numeric(precision=14, scale=2), nullable=False, default=0),
        sa.Column('payment_status', sa.Enum('unpaid', 'partial', 'paid', name='paymentstatus'), nullable=False, default='unpaid'),
        sa.Column('paid_amount', sa.Numeric(precision=14, scale=2), nullable=False, default=0),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id']),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_number'),
    )
    op.create_index('ix_invoice_supplier_date_status', 'supplier_invoices', ['supplier_id', 'invoice_date', 'status'])
    op.create_index('ix_invoice_due_date', 'supplier_invoices', ['due_date'])

    op.create_table(
        'supplier_invoice_lines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('po_line_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('quantity_invoiced', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('line_total', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['invoice_id'], ['supplier_invoices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['po_line_id'], ['purchase_order_lines.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_invoice_line_po_line', 'supplier_invoice_lines', ['po_line_id'])

    op.create_table(
        'inventory_balances',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('quantity_on_hand', sa.Integer(), nullable=False, default=0),
        sa.Column('reserved_quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('last_movement_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'warehouse_id', name='uq_product_warehouse'),
    )

    op.create_table(
        'inventory_movements',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('movement_type', sa.Enum('receipt', 'issue', 'transfer_in', 'transfer_out', 'adjustment', 'reservation', 'release', name='movementtype'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_movements_product_date', 'inventory_movements', ['product_id', 'created_at'])
    op.create_index('ix_movements_reference', 'inventory_movements', ['reference_type', 'reference_id'])

    op.create_table(
        'audit_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_audit_user_action_date', 'audit_events', ['user_id', 'action', 'created_at'])
    op.create_index('ix_audit_resource', 'audit_events', ['resource_type', 'resource_id'])


def downgrade() -> None:
    op.drop_table('audit_events')
    op.drop_table('inventory_movements')
    op.drop_table('inventory_balances')
    op.drop_table('supplier_invoice_lines')
    op.drop_table('supplier_invoices')
    op.drop_table('goods_receipt_lines')
    op.drop_table('goods_receipts')
    op.drop_table('approval_records')
    op.drop_table('purchase_order_lines')
    op.drop_table('purchase_orders')
    op.drop_table('purchase_requisitions')
    op.drop_table('conversation_messages')
    op.drop_table('conversations')
    op.drop_table('products')
    op.drop_table('suppliers')
    op.drop_table('warehouses')
    op.drop_table('users')