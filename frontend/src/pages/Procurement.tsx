import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import { clsx } from 'clsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Loader2, Plus, Search, Package, Truck, FileText, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import { format } from 'date-fns';
import { useState } from 'react';

export function ProcurementPage() {
  const [filters, setFilters] = useState({ status: '', search: '', page: 1 });
  const [showCreate, setShowCreate] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['purchaseOrders', filters],
    queryFn: () => api.getPurchaseOrders({
      status: filters.status || undefined,
      search: filters.search || undefined,
      page: filters.page,
      page_size: 20,
    }),
  });

  const { data: pendingApprovals } = useQuery({
    queryKey: ['pendingApprovals'],
    queryFn: () => api.getPendingApprovals(),
  });

  const statusBadges: Record<string, string> = {
    draft: 'badge-gray',
    pending_approval: 'badge-warning',
    approved: 'badge-info',
    ordered: 'badge-info',
    partially_received: 'badge-warning',
    received: 'badge-success',
    cancelled: 'badge-gray',
  };

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-primary-600" /></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Purchase Orders</h1>
          <p className="text-gray-500">Manage purchase orders and approvals</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary">
          <Plus className="w-4 h-4 mr-2" />
          Create PO
        </button>
      </div>

      {pendingApprovals && pendingApprovals.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
              <span className="font-medium text-yellow-800">{pendingApprovals.length} purchase orders awaiting approval</span>
            </div>
          </div>
        </div>
      )}

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Purchase Orders</CardTitle>
          <div className="flex items-center gap-2">
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value, page: 1 })}
              className="input py-1 px-2 text-sm w-auto"
            >
              <option value="">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="pending_approval">Pending Approval</option>
              <option value="approved">Approved</option>
              <option value="ordered">Ordered</option>
              <option value="partially_received">Partially Received</option>
              <option value="received">Received</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <input
              type="text"
              placeholder="Search..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
              className="input py-1 px-2 text-sm w-64"
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-3">PO Number</th>
                  <th className="pb-3">Supplier</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Order Date</th>
                  <th className="pb-3">Expected Delivery</th>
                  <th className="pb-3 text-right">Amount</th>
                  <th className="pb-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.items?.map((po: any) => (
                  <tr key={po.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 font-medium">{po.po_number}</td>
                    <td className="py-3">{po.supplier_name}</td>
                    <td className="py-3">
                      <span className={clsx('badge', statusBadges[po.status] || 'badge-gray')}>
                        {po.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3">{format(new Date(po.order_date), 'MMM d, yyyy')}</td>
                    <td className="py-3">
                      {po.expected_delivery_date ? format(new Date(po.expected_delivery_date), 'MMM d, yyyy') : 'â€”'}
                    </td>
                    <td className="py-3 text-right">${po.total_amount.toLocaleString()}</td>
                    <td className="py-3">
                      <div className="flex items-center gap-2">
                        <button className="text-primary-600 hover:text-primary-800 text-sm">View</button>
                        {po.status === 'pending_approval' && (
                          <>
                            <button className="text-green-600 hover:text-green-800 text-sm">Approve</button>
                            <button className="text-red-600 hover:text-red-800 text-sm">Reject</button>
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