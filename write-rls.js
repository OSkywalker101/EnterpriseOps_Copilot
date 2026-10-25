const fs = require('fs');
const sql = `-- RLS Policies
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

CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Admins can view all profiles" ON profiles FOR SELECT USING (
  EXISTS (SELECT 1 FROM profiles p WHERE p.id = auth.uid() AND p.role = 'Administrator')
);

CREATE POLICY "Users can CRUD own conversations" ON conversations FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can CRUD messages in own conversations" ON conversation_messages FOR ALL USING (
  EXISTS (SELECT 1 FROM conversations c WHERE c.id = conversation_messages.conversation_id AND c.user_id = auth.uid())
);

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

CREATE POLICY "Users can view own audit" ON audit_events FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Admins can view all audit" ON audit_events FOR SELECT USING (
  EXISTS (SELECT 1 FROM profiles p WHERE p.id = auth.uid() AND p.role = 'Administrator')
);

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, role)
  VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>"full_name", COALESCE(NEW.raw_user_meta_data->>"role","Employee"));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
`;
fs.writeFileSync("supabase/migrations/20251025_000002_rls.sql", sql);
console.log("Written RLS");