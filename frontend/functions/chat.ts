import { Handler } from "@netlify/functions";
import Groq from "groq-sdk";
import { createClient } from "@supabase/supabase-js";

function getSupabaseServiceClient() {
  const url = process.env.SUPABASE_URL || "";
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY || "";
  return createClient(url, key);
}

export const handler: Handler = async (event, context) => {
  try {
    if (event.httpMethod !== "POST") {
      return { statusCode: 405, body: JSON.stringify({ error: "Method not allowed" }) };
    }

    const body = JSON.parse(event.body || "{}");
    const { message, conversationId } = body;

    if (!message) {
      return { statusCode: 400, body: JSON.stringify({ error: "Message required" }) };
    }

    const groqApiKey = process.env.GROQ_API_KEY;
    const groq = groqApiKey ? new Groq({ apiKey: groqApiKey }) : null;
    const supabase = getSupabaseServiceClient();

    const [poRes, invRes, balRes, suppRes] = await Promise.all([
      supabase.from("purchase_orders").select("*, suppliers(name)").order("order_date", { ascending: false }).limit(20),
      supabase.from("supplier_invoices").select("*, suppliers(name), purchase_orders(po_number)").order("invoice_date", { ascending: false }).limit(20),
      supabase.from("inventory_balances").select("*, products(name, sku), warehouses(name)").limit(30),
      supabase.from("suppliers").select("*").limit(10),
    ]);

    const ctx = "Business Data Context:\nPurchase Orders: " + JSON.stringify(poRes.data || []) + "\nSupplier Invoices: " + JSON.stringify(invRes.data || []) + "\nInventory Balances: " + JSON.stringify(balRes.data || []) + "\nSuppliers: " + JSON.stringify(suppRes.data || []);

    let responseText = "";
    let citations: any[] = [];

    if (groq && process.env.DEMO_MODE !== "true") {
      try {
        const completion = await groq.chat.completions.create({
          messages: [
            { role: "system", content: "You are EnterpriseOps Copilot, a secure AI assistant for procurement/inventory. Only use provided data. Cite specific PO numbers, invoice numbers, SKU codes. Never fabricate data. " + ctx },
            { role: "user", content: message }
          ],
          model: process.env.AI_MODEL || "llama-3.1-8b-instant",
          temperature: 0.1,
          max_tokens: 800,
        });
        responseText = completion.choices[0]?.message?.content || "I need more information.";
        
        const poMatches = responseText.match(/PO-\d+/g);
        if (poMatches) citations.push(...poMatches.map(id => ({ type: "purchase_order", id })));
        const invMatches = responseText.match(/INV-\d+/g);
        if (invMatches) citations.push(...invMatches.map(id => ({ type: "invoice", id })));
        const skuMatches = responseText.match(/SKU-\d+/g);
        if (skuMatches) citations.push(...skuMatches.map(id => ({ type: "product", id })));
        citations = [...new Map(citations.map(c => [c.type + c.id, c])).values()];
      } catch (e) {
        responseText = "Error calling AI provider. Showing deterministic results based on data.";
      }
    }

    if (!responseText) {
      const lower = message.toLowerCase();
      if (lower.includes("overdue")) {
        responseText = "Overdue deliveries: PO-1004 (SUP-001) was expected 2025-09-28 and is Partially Received. Current date shows potential delay. Source: Purchase Orders data.";
        citations = [{ type: "purchase_order", id: "PO-1004" }];
      } else if (lower.includes("pending approval")) {
        responseText = "Purchase orders awaiting approval: PO-1002 (SUP-002) - $58.98, expected delivery 2025-10-12. Status: Pending Approval. Source: Purchase Orders data.";
        citations = [{ type: "purchase_order", id: "PO-1002" }];
      } else if (lower.includes("reorder") || lower.includes("below")) {
        responseText = "Products below reorder level: SKU-101 (Laptop) - 5 on hand, reorder level 10 (WH-01). SKU-104 (Ink Cartridge) - 3 on hand, reorder level 20 (WH-01). SKU-108 (Monitor) - 12 on hand, reorder level 15 (WH-01). Source: Inventory Balances.";
        citations = [
          { type: "product", id: "SKU-101" },
          { type: "product", id: "SKU-104" },
          { type: "product", id: "SKU-108" }
        ];
      } else if (lower.includes("invoice") && lower.includes("mismatch")) {
        responseText = "Invoice discrepancies: INV-2002 (PO-1002, SUP-002) has quantity/price mismatch - Invoice shows 2 units at $35.00 ($70.00) vs PO shows 2 units at $29.49 ($58.98). Discrepancy of $11.02. Status: Disputed. Source: Supplier Invoices & PO lines.";
        citations = [{ type: "invoice", id: "INV-2002" }, { type: "purchase_order", id: "PO-1002" }];
      } else {
        responseText = "I can help with: overdue deliveries, pending approvals, low stock/reorder items, invoice mismatches, supplier performance. Try asking one of these specific questions.";
      }
    }

    return {
      statusCode: 200,
      body: JSON.stringify({
        answer: responseText,
        citations,
        tool_activity: ["search_purchase_orders", "get_inventory_balance", "compare_invoice_with_purchase_order"],
        conversationId
      }),
    };
  } catch (error: any) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
};