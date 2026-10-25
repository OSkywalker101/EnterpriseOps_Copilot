-- EnterpriseOps Copilot Schema
CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";

CREATE TABLE IF NOT EXISTS profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  role TEXT NOT NULL DEFAULT 'Employee' CHECK (role IN ('Employee','Procurement Specialist','Inventory Manager','Approver','Administrator')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS suppliers (
  id SERIAL PRIMARY KEY,
  supplier_code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  contact_email TEXT,
  contact_phone TEXT,
  address TEXT,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','inactive')),
  delivery_lead_time_days INTEGER DEFAULT 5,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,
  sku TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  description TEXT,
  unit_price NUMERIC(12,2) NOT NULL DEFAULT 0,
  category TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS warehouses (
  id SERIAL PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  location TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS purchase_orders (
  id SERIAL PRIMARY KEY,
  po_number TEXT UNIQUE NOT NULL,
  supplier_id INTEGER REFERENCES suppliers(id),
  status TEXT NOT NULL DEFAULT 'Draft' CHECK (status IN ('Draft','Pending Approval','Approved','Ordered','Partially Received','Received','Cancelled')),
  order_date DATE NOT NULL DEFAULT CURRENT_DATE,
  expected_delivery_date DATE,
  total_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
  requested_by UUID REFERENCES auth.users(id),
  approved_by UUID REFERENCES auth.users(id),
  approved_at TIMESTAMPTZ,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS purchase_order_lines (
  id SERIAL PRIMARY KEY,
  purchase_order_id INTEGER REFERENCES purchase_orders(id) ON DELETE CASCADE,
  product_id INTEGER REFERENCES products(id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price NUMERIC(12,2) NOT NULL DEFAULT 0,
  line_total NUMERIC(12,2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS inventory_balances (
  id SERIAL PRIMARY KEY,
  product_id INTEGER REFERENCES products(id),
  warehouse_id INTEGER REFERENCES warehouses(id),
  quantity_on_hand INTEGER NOT NULL DEFAULT 0,
  reserved_quantity INTEGER NOT NULL DEFAULT 0,
  reorder_level INTEGER NOT NULL DEFAULT 10,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(product_id, warehouse_id)
);

CREATE TABLE IF NOT EXISTS goods_receipts (
  id SERIAL PRIMARY KEY,
  gr_number TEXT UNIQUE NOT NULL,
  purchase_order_id INTEGER REFERENCES purchase_orders(id),
  received_by UUID REFERENCES auth.users(id),
  received_date DATE NOT NULL DEFAULT CURRENT_DATE,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS goods_receipt_lines (
  id SERIAL PRIMARY KEY,
  goods_receipt_id INTEGER REFERENCES goods_receipts(id) ON DELETE CASCADE,
  purchase_order_line_id INTEGER REFERENCES purchase_order_lines(id),
  product_id INTEGER REFERENCES products(id),
  quantity_received INTEGER NOT NULL CHECK (quantity_received > 0)
);

CREATE TABLE IF NOT EXISTS supplier_invoices (
  id SERIAL PRIMARY KEY,
  invoice_number TEXT UNIQUE NOT NULL,
  purchase_order_id INTEGER REFERENCES purchase_orders(id),
  supplier_id INTEGER REFERENCES suppliers(id),
  invoice_date DATE NOT NULL DEFAULT CURRENT_DATE,
  due_date DATE,
  total_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
  payment_status TEXT NOT NULL DEFAULT 'pending' CHECK (payment_status IN ('pending','matched','paid','disputed')),
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS supplier_invoice_lines (
  id SERIAL PRIMARY KEY,
  supplier_invoice_id INTEGER REFERENCES supplier_invoices(id) ON DELETE CASCADE,
  product_id INTEGER REFERENCES products(id),
  quantity INTEGER NOT NULL CHECK (quantity > 0),
  unit_price NUMERIC(12,2) NOT NULL DEFAULT 0,
  line_total NUMERIC(12,2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS conversation_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user','assistant','system')),
  content TEXT NOT NULL,
  citations JSONB,
  tool_activity JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id),
  action TEXT NOT NULL,
  entity_type TEXT,
  entity_id TEXT,
  metadata JSONB,
  ip_address TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_po_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_po_status ON purchase_orders(status);
CREATE INDEX idx_po_date ON purchase_orders(order_date);
CREATE INDEX idx_inv_po ON supplier_invoices(purchase_order_id);
CREATE INDEX idx_inv_status ON supplier_invoices(payment_status);
CREATE INDEX idx_msg_conv ON conversation_messages(conversation_id);
CREATE INDEX idx_audit_user ON audit_events(user_id);
CREATE INDEX idx_audit_time ON audit_events(created_at);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS \$$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
\$$ language 'plpgsql';

CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_po_updated_at BEFORE UPDATE ON purchase_orders FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_inv_updated_at BEFORE UPDATE ON supplier_invoices FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
CREATE TRIGGER update_conv_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
-- RLS Policies
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

-- Profiles: users can read own, admins can read all
CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Admins can view all profiles" ON profiles FOR SELECT USING (
  EXISTS (SELECT 1 FROM profiles p WHERE p.id = auth.uid() AND p.role = 'Administrator')
);

-- Conversations: users can only access own
CREATE POLICY "Users can CRUD own conversations" ON conversations FOR ALL USING (auth.uid() = user_id);

-- Messages: through conversation ownership
CREATE POLICY "Users can CRUD messages in own conversations" ON conversation_messages FOR ALL USING (
  EXISTS (SELECT 1 FROM conversations c WHERE c.id = conversation_messages.conversation_id AND c.user_id = auth.uid())
);

-- Business data: authenticated users can read (with role restrictions in app)
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

-- Audit: users can read own, admins all
CREATE POLICY "Users can view own audit" ON audit_events FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Admins can view all audit" ON audit_events FOR SELECT USING (
  EXISTS (SELECT 1 FROM profiles p WHERE p.id = auth.uid() AND p.role = 'Administrator')
);

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS \$$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, role)
  VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name', COALESCE(NEW.raw_user_meta_data->>'role','Employee'));
  RETURN NEW;
END;
\$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- Demo Seed Data
INSERT INTO suppliers (supplier_code, name, contact_email, delivery_lead_time_days, status) VALUES
('SUP-001','Acme Supplies','sales@acme.example.com',7,'active'),
('SUP-002','Global Parts Inc','orders@globalparts.example.com',5,'active'),
('SUP-003','TechSource Ltd','info@techsource.example.com',10,'active'),
('SUP-004','Prime Materials','contact@primemats.example.com',6,'active'),
('SUP-005','Office Depot Co','sales@officedepot.example.com',3,'active')
ON CONFLICT (supplier_code) DO NOTHING;

INSERT INTO products (sku, name, description, unit_price, category) VALUES
('SKU-101','Laptop Computer','Business laptop 15 inch',899.99,'Electronics'),
('SKU-102','Wireless Mouse','Ergonomic wireless mouse',29.49,'Electronics'),
('SKU-103','A4 Paper Ream','500 sheets A4 paper',5.99,'Office Supplies'),
('SKU-104','Printer Ink Cartridge','Black ink cartridge',45.75,'Office Supplies'),
('SKU-105','Desk Chair','Ergonomic office chair',249.50,'Furniture'),
('SKU-106','USB Drive 32GB','USB 3.0 flash drive',12.99,'Electronics'),
('SKU-107','Paper Clips Box','1000 count paper clips',3.25,'Office Supplies'),
('SKU-108','Monitor 24 inch','LED monitor 1920x1080',199.99,'Electronics')
ON CONFLICT (sku) DO NOTHING;

INSERT INTO warehouses (code, name, location) VALUES
('WH-01','Main Warehouse','Chicago, IL'),
('WH-02','East Coast DC','New York, NY')
ON CONFLICT (code) DO NOTHING;

INSERT INTO purchase_orders (po_number, supplier_id, status, order_date, expected_delivery_date, total_amount) VALUES
('PO-1001',(SELECT id FROM suppliers WHERE supplier_code='SUP-001'),'Ordered','2025-10-01','2025-10-10',899.99),
('PO-1002',(SELECT id FROM suppliers WHERE supplier_code='SUP-002'),'Pending Approval','2025-10-05','2025-10-12',58.98),
('PO-1003',(SELECT id FROM suppliers WHERE supplier_code='SUP-003'),'Ordered','2025-10-08','2025-10-18',299.25),
('PO-1004',(SELECT id FROM suppliers WHERE supplier_code='SUP-001'),'Partially Received','2025-09-20','2025-09-28',45.75),
('PO-1005',(SELECT id FROM suppliers WHERE supplier_code='SUP-005'),'Ordered','2025-10-12','2025-10-15',15.23)
ON CONFLICT (po_number) DO NOTHING;

INSERT INTO purchase_order_lines (purchase_order_id, product_id, quantity, unit_price, line_total) VALUES
((SELECT id FROM purchase_orders WHERE po_number='PO-1001'),(SELECT id FROM products WHERE sku='SKU-101'),1,899.99,899.99),
((SELECT id FROM purchase_orders WHERE po_number='PO-1002'),(SELECT id FROM products WHERE sku='SKU-102'),2,29.49,58.98),
((SELECT id FROM purchase_orders WHERE po_number='PO-1003'),(SELECT id FROM products WHERE sku='SKU-104'),1,45.75,45.75),
((SELECT id FROM purchase_orders WHERE po_number='PO-1003'),(SELECT id FROM products WHERE sku='SKU-105'),1,249.50,249.50),
((SELECT id FROM purchase_orders WHERE po_number='PO-1004'),(SELECT id FROM products WHERE sku='SKU-104'),1,45.75,45.75),
((SELECT id FROM purchase_orders WHERE po_number='PO-1005'),(SELECT id FROM products WHERE sku='SKU-103'),2,5.99,11.98),
((SELECT id FROM purchase_orders WHERE po_number='PO-1005'),(SELECT id FROM products WHERE sku='SKU-107'),1,3.25,3.25)
ON CONFLICT DO NOTHING;

INSERT INTO inventory_balances (product_id, warehouse_id, quantity_on_hand, reserved_quantity, reorder_level) VALUES
((SELECT id FROM products WHERE sku='SKU-101'),(SELECT id FROM warehouses WHERE code='WH-01'),5,2,10),
((SELECT id FROM products WHERE sku='SKU-102'),(SELECT id FROM warehouses WHERE code='WH-01'),25,0,15),
((SELECT id FROM products WHERE sku='SKU-103'),(SELECT id FROM warehouses WHERE code='WH-01'),150,0,50),
((SELECT id FROM products WHERE sku='SKU-104'),(SELECT id FROM warehouses WHERE code='WH-01'),3,1,20),
((SELECT id FROM products WHERE sku='SKU-105'),(SELECT id FROM warehouses WHERE code='WH-01'),8,0,5),
((SELECT id FROM products WHERE sku='SKU-106'),(SELECT id FROM warehouses WHERE code='WH-02'),45,0,25),
((SELECT id FROM products WHERE sku='SKU-107'),(SELECT id FROM warehouses WHERE code='WH-01'),200,0,100),
((SELECT id FROM products WHERE sku='SKU-108'),(SELECT id FROM warehouses WHERE code='WH-01'),12,0,15)
ON CONFLICT (product_id, warehouse_id) DO NOTHING;

INSERT INTO supplier_invoices (invoice_number, purchase_order_id, supplier_id, invoice_date, due_date, total_amount, payment_status) VALUES
('INV-2001',(SELECT id FROM purchase_orders WHERE po_number='PO-1001'),(SELECT id FROM suppliers WHERE supplier_code='SUP-001'),'2025-10-11','2025-11-10',899.99,'pending'),
('INV-2002',(SELECT id FROM purchase_orders WHERE po_number='PO-1002'),(SELECT id FROM suppliers WHERE supplier_code='SUP-002'),'2025-10-06','2025-11-05',70.00,'disputed'),
('INV-2003',(SELECT id FROM purchase_orders WHERE po_number='PO-1004'),(SELECT id FROM suppliers WHERE supplier_code='SUP-001'),'2025-09-29','2025-10-29',45.75,'matched')
ON CONFLICT (invoice_number) DO NOTHING;

INSERT INTO supplier_invoice_lines (supplier_invoice_id, product_id, quantity, unit_price, line_total) VALUES
((SELECT id FROM supplier_invoices WHERE invoice_number='INV-2001'),(SELECT id FROM products WHERE sku='SKU-101'),1,899.99,899.99),
((SELECT id FROM supplier_invoices WHERE invoice_number='INV-2002'),(SELECT id FROM products WHERE sku='SKU-102'),2,35.00,70.00),
((SELECT id FROM supplier_invoices WHERE invoice_number='INV-2003'),(SELECT id FROM products WHERE sku='SKU-104'),1,45.75,45.75)
ON CONFLICT DO NOTHING;
