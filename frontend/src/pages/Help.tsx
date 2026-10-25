import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { HelpCircle, Search, MessageSquare, Package, Box, Truck, FileText, Lightbulb, AlertTriangle, CheckCircle, XCircle, ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';

const faqs = [
  {
    question: 'How do I ask questions about purchase orders?',
    answer: 'You can ask natural language questions in the Chat interface. For example: "Which purchase orders are awaiting approval?" or "Show me PO-1001 details." The assistant will query the database and provide answers with source citations.',
    icon: MessageSquare,
  },
  {
    question: 'What data can the assistant access?',
    answer: 'The assistant can access purchase orders, suppliers, inventory levels, goods receipts, and supplier invoices. It uses approved tools to retrieve data and cannot access data you don\'t have permission to see.',
    icon: Search,
  },
  {
    question: 'How are answers grounded in real data?',
    answer: 'Every factual answer includes citations referencing actual database records (PO numbers, supplier codes, invoice numbers, SKUs). The assistant never invents data - if information isn\'t available, it will say so.',
    icon: CheckCircle,
  },
  {
    question: 'Can I ask about invoice matching?',
    answer: 'Yes! Ask questions like "Check invoice INV-2002 for discrepancies" or "Compare invoice with purchase order." The assistant performs 2-way and 3-way matching automatically.',
    icon: FileText,
  },
  {
    question: 'How do I check inventory levels?',
    answer: 'Ask "What products are below reorder level?" or "How much SKU-104 is in stock?" The assistant will query inventory balances across all warehouses.',
    icon: Box,
  },
  {
    question: 'What if I need supplier performance data?',
    answer: 'Ask "How is supplier SUP-001 performing?" or "Which suppliers have overdue deliveries?" The assistant provides delivery performance summaries with on-time rates.',
    icon: Truck,
  },
  {
    question: 'Can the assistant make changes to data?',
    answer: 'Currently, the assistant is read-only. It can retrieve and analyze data but cannot create, update, or delete records. For changes, use the respective management pages.',
    icon: AlertTriangle,
  },
  {
    question: 'How do citations work?',
    answer: 'Each answer includes clickable citations showing the source records. Click a citation to navigate to the detailed record view. Citations are generated from actual database queries, not fabricated.',
    icon: Lightbulb,
  },
];

const exampleQueries = [
  'Which purchase orders are awaiting approval?',
  'Show me overdue deliveries',
  'What products are below reorder level?',
  'Check invoice INV-2002 for discrepancies',
  'How is supplier SUP-001 performing?',
  'Summarize outstanding procurement issues',
  'What is the available stock for SKU-104?',
  'List all pending approvals',
  'Compare invoice INV-2001 with its purchase order',
  'Show me recent stock movements for SKU-101',
];

export function HelpPage() {
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Help & Documentation</h1>
        <p className="text-gray-500">Learn how to use EnterpriseOps Copilot effectively</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            Example Questions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-600 mb-4">Try asking the assistant these questions:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {exampleQueries.map((query, i) => (
              <button
                key={i}
                className="p-3 text-left bg-gray-50 hover:bg-gray-100 rounded-lg text-sm text-gray-700 transition-colors border border-gray-100"
              >
                {query}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <HelpCircle className="w-5 h-5" />
            Frequently Asked Questions
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {faqs.map((faq, i) => (
            <div key={i} className="border border-gray-200 rounded-lg overflow-hidden">
              <button
                onClick={() => setExpandedFaq(expandedFaq === i ? null : i)}
                className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-3 flex-1">
                  <faq.icon className="w-5 h-5 text-primary-600 flex-shrink-0" />
                  <span className="font-medium text-gray-900">{faq.question}</span>
                </div>
                <span className="text-gray-400">
                  {expandedFaq === i ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                </span>
              </button>
              {expandedFaq === i && (
                <div className="px-4 pb-4 border-t border-gray-100 text-gray-600">
                  {faq.answer}
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5" />
            Tips for Better Results
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium">Be specific</p>
              <p className="text-sm text-gray-600">Include PO numbers, SKUs, supplier codes, or date ranges when possible.</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium">Ask follow-up questions</p>
              <p className="text-sm text-gray-600">The assistant maintains conversation context. You can ask for more details or clarify.</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium">Check citations</p>
              <p className="text-sm text-gray-600">Every answer includes source references. Click them to verify the data.</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium">Use the dashboards</p>
              <p className="text-sm text-gray-600">For quick overviews, the Procurement and Inventory dashboards show key metrics at a glance.</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium">Don't expect external knowledge</p>
              <p className="text-sm text-gray-600">The assistant only knows what's in your database. It won't answer general knowledge questions.</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-primary-50 border-primary-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-primary-800">
            <HelpCircle className="w-5 h-5" />
            Need More Help?
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-primary-700">
            If you can't find what you're looking for, contact your system administrator or check the
            <a href="#" className="underline hover:text-primary-900">technical documentation</a>.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}