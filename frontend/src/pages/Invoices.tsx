import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import { clsx } from 'clsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Loader2, Search, FileText, AlertTriangle, CheckCircle, XCircle, DollarSign, Clock } from 'lucide-react';
import { format } from 'date-fns';
import { useState } from 'react';

export function InvoicesPage() {
  const [filters, setFilters] = useState({ status: '', supplier_id: '', page: 1 });

  const { data, isLoading } = useQuery({
    queryKey: ['invoices', filters],
    queryFn: () => api.getInvoices({ status: filters.status || undefined, supplier_id: filters.supplier_id || undefined, page: filters.page, page_size: 20 }),
  });

  const { data: suppliers } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => api.getSuppliers({ page_size: 100 }),
  });

  const statusBadges: Record<string, string> = {
    draft: 'badge-gray',
    submitted: 'badge-info',
    matched: 'badge-success',
    discrepancy: 'badge-danger',
    approved: 'badge-info',
    paid: 'badge-success',
    cancelled: 'badge-gray',
  };

  const paymentStatusBadges: Record<string, string> = {
    unpaid: 'badge-danger',
    partial: 'badge-warning',
    paid: 'badge-success',
  };

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-primary-600" /></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Supplier Invoices</h1>
          <p className="text-gray-500">Manage and match supplier invoices</p>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Invoices</CardTitle>
          <div className="flex items-center gap-2">
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value, page: 1 })}
              className="input py-1 px-2 text-sm w-auto"
            >
              <option value="">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="submitted">Submitted</option>
              <option value="matched">Matched</option>
              <option value="discrepancy">Discrepancy</option>
              <option value="approved">Approved</option>
              <option value="paid">Paid</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <select
              value={filters.supplier_id}
              onChange={(e) => setFilters({ ...filters, supplier_id: e.target.value, page: 1 })}
              className="input py-1 px-2 text-sm w-auto"
            >
              <option value="">All Suppliers</option>
              {suppliers?.items?.map((s: any) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-3">Invoice #</th>
                  <th className="pb-3">Supplier</th>
                  <th className="pb-3">PO Reference</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Payment</th>
                  <th className="pb-3">Invoice Date</th>
                  <th className="pb-3">Due Date</th>
                  <th className="pb-3 text-right">Amount</th>
                  <th className="pb-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.items?.map((invoice: any) => (
                  <tr key={invoice.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 font-mono font-medium">{invoice.invoice_number}</td>
                    <td className="py-3">{invoice.supplier?.name || 'Unknown'}</td>
                    <td className="py-3">
                      {invoice.purchase_order_id ? `PO-${invoice.purchase_order_id}` : 'â€”'}
                    </td>
                    <td className="py-3">
                      <span className={clsx('badge', statusBadges[invoice.status] || 'badge-gray')}>
                        {invoice.status}
                      </span>
                    </td>
                    <td className="py-3">
                      <span className={clsx('badge', paymentStatusBadges[invoice.payment_status] || 'badge-gray')}>
                        {invoice.payment_status}
                      </span>
                    </td>
                    <td className="py-3">{format(new Date(invoice.invoice_date), 'MMM d, yyyy')}</td>
                    <td className="py-3">
                      {invoice.due_date ? format(new Date(invoice.due_date), 'MMM d, yyyy') : 'â€”'}
                    </td>
                    <td className="py-3 text-right">${invoice.total_amount.toLocaleString()}</td>
                    <td className="py-3">
                      <div className="flex items-center gap-2">
                        <button className="text-primary-600 hover:text-primary-800 text-sm">View</button>
                        {invoice.status === 'discrepancy' && (
                          <>
                            <button className="text-blue-600 hover:text-blue-800 text-sm">Match PO</button>
                            <button className="text-green-600 hover:text-green-800 text-sm">Match GR</button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data && data.total_pages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <span className="text-sm text-gray-500">
                Page {data.page} of {data.total_pages} â€¢ {data.total} total
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                  disabled={filters.page === 1}
                  className="btn-secondary text-sm"
                >
                  Previous
                </button>
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                  disabled={filters.page >= data.total_pages}
                  className="btn-secondary text-sm"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}