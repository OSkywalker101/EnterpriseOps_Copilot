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
