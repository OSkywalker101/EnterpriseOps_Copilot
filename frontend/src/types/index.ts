export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  department: string | null;
  warehouse_id: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type UserRole = 'employee' | 'procurement_specialist' | 'inventory_manager' | 'approver' | 'administrator';

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface Conversation {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationMessage {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_calls: string | null;
  tool_results: string | null;
  citations: string | null;
  created_at: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: number;
}

export interface ChatResponse {
  message: ConversationMessage;
  conversation: Conversation;
}

export interface Supplier {
  id: number;
  supplier_code: string;
  name: string;
  contact_name: string | null;
  contact_email: string | null;
  contact_phone: string | null;
  address: string | null;
  status: 'active' | 'inactive' | 'on_hold';
  lead_time_days: number;
  payment_terms_days: number;
  currency: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  sku: string;
  name: string;
  description: string | null;
  unit_of_measure: string;
  standard_cost: number | null;
  reorder_level: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Warehouse {
  id: number;
  code: string;
  name: string;
  address: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface InventoryBalance {
  id: number;
  product_id: number;
  warehouse_id: number;
  quantity_on_hand: number;
  reserved_quantity: number;
  available_quantity: number;
  last_movement_date: string | null;
  created_at: string;
  updated_at: string;
  product?: Product;
  warehouse?: Warehouse;
}

export interface InventoryMovement {
  id: number;
  product_id: number;
  warehouse_id: number;
  movement_type: MovementType;
  quantity: number;
  reference_type: string | null;
  reference_id: number | null;
  notes: string | null;
  created_at: string;
  created_by: number | null;
  product?: Product;
  warehouse?: Warehouse;
}

export type MovementType = 'receipt' | 'issue' | 'transfer_in' | 'transfer_out' | 'adjustment' | 'reservation' | 'release';

export interface PurchaseOrder {
  id: number;
  po_number: string;
  supplier_id: number;
  requisition_id: number | null;
  status: PurchaseOrderStatus;
  order_date: string;
  expected_delivery_date: string | null;
  actual_delivery_date: string | null;
  currency: string;
  total_amount: number;
  notes: string | null;
  created_by: number;
  approved_by: number | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
  supplier?: Supplier;
  lines?: PurchaseOrderLine[];
}

export type PurchaseOrderStatus = 'draft' | 'pending_approval' | 'approved' | 'ordered' | 'partially_received' | 'received' | 'cancelled';

export interface PurchaseOrderLine {
  id: number;
  purchase_order_id: number;
  requisition_id: number | null;
  product_id: number;
  line_number: number;
  quantity_ordered: number;
  quantity_received: number;
  unit_price: number;
  currency: string;
  line_total: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
  product?: Product;
}

export interface GoodsReceipt {
  id: number;
  gr_number: string;
  purchase_order_id: number;
  receipt_date: string;
  warehouse_id: number;
  received_by: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
  purchase_order?: PurchaseOrder;
  lines?: GoodsReceiptLine[];
}

export interface GoodsReceiptLine {
  id: number;
  goods_receipt_id: number;
  po_line_id: number;
  product_id: number;
  quantity_received: number;
  quantity_accepted: number;
  quantity_rejected: number;
  notes: string | null;
  created_at: string;
  product?: Product;
}

export interface SupplierInvoice {
  id: number;
  invoice_number: string;
  supplier_id: number;
  purchase_order_id: number | null;
  status: InvoiceStatus;
  invoice_date: string;
  due_date: string | null;
  currency: string;
  total_amount: number;
  payment_status: PaymentStatus;
  paid_amount: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
  supplier?: Supplier;
  purchase_order?: PurchaseOrder;
  lines?: SupplierInvoiceLine[];
}

export type InvoiceStatus = 'draft' | 'submitted' | 'matched' | 'discrepancy' | 'approved' | 'paid' | 'cancelled';
export type PaymentStatus = 'unpaid' | 'partial' | 'paid';

export interface SupplierInvoiceLine {
  id: number;
  invoice_id: number;
  po_line_id: number | null;
  product_id: number;
  line_number: number;
  quantity_invoiced: number;
  unit_price: number;
  currency: string;
  line_total: number;
  notes: string | null;
  created_at: string;
  product?: Product;
}

export interface Citation {
  type: string;
  id: number | string;
  reference: string;
}

export interface ToolCall {
  tool: string;
  args: Record<string, unknown>;
  result: boolean;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface FilterParams {
  search?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}