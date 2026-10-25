export function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight mb-6">
              EnterpriseOps Copilot
            </h1>
            <p className="text-xl sm:text-2xl text-blue-100 mb-8 max-w-3xl mx-auto">
              AI-powered assistant for procurement, inventory, and invoice operations.
              Ask questions in plain English, get grounded answers with real data citations.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a
                href="/login"
                className="bg-white text-indigo-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors text-lg"
              >
                Sign In to Demo
              </a>
              <a
                href="#features"
                className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors text-lg"
              >
                View Features
              </a>
            </div>
          </div>
        </div>
        {/* Decorative elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-white/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-white/10 rounded-full blur-3xl" />
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              What EnterpriseOps Copilot Does
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Natural language interface over real enterprise data. No hallucinations — every answer cites actual records.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: "📦",
                title: "Procurement Intelligence",
                desc: "Track purchase orders, approvals, overdue deliveries, and supplier performance. Ask: \"Which POs await approval?\" or \"Show overdue deliveries.\""
              },
              {
                icon: "📊",
                title: "Inventory Visibility",
                desc: "Real-time stock levels, reorder alerts, warehouse views. Ask: \"What\\'s below reorder level?\" or \"Available stock for SKU-104.\""
              },
              {
                icon: "🧾",
                title: "Invoice Matching",
                desc: "Three-way matching (PO, Goods Receipt, Invoice). Automatic discrepancy detection. Ask: \"Which invoices have quantity mismatches?\""
              },
              {
                icon: "🤖",
                title: "Grounded AI Answers",
                desc: "Every response cites real database records (PO numbers, invoice IDs, SKUs). No fabricated data. Expandable evidence panel shows tools used."
              },
              {
                icon: "🔐",
                title: "Role-Based Access",
                desc: "5 roles (Employee, Procurement, Inventory, Approver, Admin). Row-level security. Users only see authorized data."
              },
              {
                icon: "📝",
                title: "Audit & Compliance",
                desc: "Immutable audit log for all actions. Conversation history persisted. Human-in-the-loop for any write operations."
              }
            ].map((feature, i) => (
              <div key={i} className="bg-gray-50 rounded-xl p-6 border border-gray-100 hover:border-blue-200 transition-colors">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-20 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center mb-12">Architecture</h2>
          <div className="grid md:grid-cols-4 gap-8 text-center">
            {[
              { label: "Frontend", tech: "React 18 • TypeScript • Vite • Tailwind • TanStack Query" },
              { label: "Backend", tech: "Netlify Functions (TypeScript) • Serverless" },
              { label: "Database", tech: "Neon PostgreSQL • Supabase Auth • Row Level Security" },
              { label: "AI", tech: "Groq (Llama 3.1) • Tool calling • Deterministic calculations" }
            ].map((item, i) => (
              <div key={i} className="bg-gray-800 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-blue-300 mb-2">{item.label}</h3>
                <p className="text-gray-300 text-sm">{item.tech}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Credentials */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Demo Access</h2>
            <p className="text-gray-600 mb-8">Pre-seeded with realistic procurement/inventory data. Try the chat with these questions:</p>
            <div className="bg-white rounded-xl p-6 border border-gray-200 text-left">
              <div className="mb-4">
                <span className="font-semibold text-gray-900">Admin:</span> oskywalker@gmail.com / OS10
              </div>
              <div className="space-y-2 text-sm text-gray-700">
                <div>• "Which purchase orders are awaiting approval?"</div>
                <div>• "Show me products below reorder level"</div>
                <div>• "Which invoices have quantity mismatches?"</div>
                <div>• "How is supplier SUP-001 performing?"</div>
                <div>• "Summarize current procurement exceptions"</div>
              </div>
              <a
                href="/login"
                className="mt-6 inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
              >
                Try It Now
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>EnterpriseOps Copilot — Built for technical interviews • Not a real SAP integration</p>
          <p className="mt-2 text-sm">Serverless • Secure • Grounded AI</p>
        </div>
      </footer>
    </div>
  );
}