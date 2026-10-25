const fs = require('fs');
const sql = `-- RLS Policies (simplified for Neon + Supabase Auth)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE warehouses ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE purchase_order_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_balances ENABLE ROW LEVEL SECURITY;
ALTER TABLE goods_receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE goods_receipt_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE supplier_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE supplier_invoice_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (id = current_user);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (id = current_user);

CREATE POLICY "Authenticated users can read suppliers" ON suppliers FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read products" ON products FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read warehouses" ON warehouses FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read PO" ON purchase_orders FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read PO lines" ON purchase_order_lines FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read inventory" ON inventory_balances FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read GR" ON goods_receipts FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read GR lines" ON goods_receipt_lines FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read invoices" ON supplier_invoices FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read invoice lines" ON supplier_invoice_lines FOR SELECT TO authenticated USING (true);
`;
fs.writeFileSync("supabase/migrations/20251025_000002_rls.sql", sql);
console.log("Written simple RLS");