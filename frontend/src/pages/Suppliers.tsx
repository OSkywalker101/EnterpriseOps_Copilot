import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import { clsx } from 'clsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Loader2, Search, Truck, Plus, Users, Clock, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';
import { useState } from 'react';

export function SuppliersPage() {
  const [filters, setFilters] = useState({ status: '', search: '', page: 1 });

  const { data, isLoading } = useQuery({
    queryKey: ['suppliers', filters],
    queryFn: () => api.getSuppliers({ status: filters.status || undefined, search: filters.search || undefined, page: filters.page, page_size: 20 }),
  });

  const statusBadges = {
    active: 'badge-success',
    inactive: 'badge-gray',
    on_hold: 'badge-warning',
  };

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-primary-600" /></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Suppliers</h1>
          <p className="text-gray-500">Manage supplier information and performance</p>
        </div>
        <button className="btn-primary">
          <Plus className="w-4 h-4 mr-2" />
          Add Supplier
        </button>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Suppliers</CardTitle>
          <div className="flex items-center gap-2">
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value, page: 1 })}
              className="input py-1 px-2 text-sm w-auto"
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="on_hold">On Hold</option>
            </select>
            <input
              type="text"
              placeholder="Search suppliers..."
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
                  <th className="pb-3">Code</th>
                  <th className="pb-3">Name</th>
                  <th className="pb-3">Contact</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Lead Time</th>
                  <th className="pb-3">Payment Terms</th>
                  <th className="pb-3">Currency</th>
                  <th className="pb-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {data?.items?.map((supplier: any) => (
                  <tr key={supplier.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 font-mono font-medium">{supplier.supplier_code}</td>
                    <td className="py-3 font-medium">{supplier.name}</td>
                    <td className="py-3">
                      <div>
                        {supplier.contact_name && <p>{supplier.contact_name}</p>}
                        {supplier.contact_email && <p className="text-sm text-gray-500">{supplier.contact_email}</p>}
                      </div>
                    </td>
                    <td className="py-3">
                      <span className={clsx('badge', statusBadges[supplier.status as keyof typeof statusBadges] || 'badge-gray')}>
                        {supplier.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3">{supplier.lead_time_days} days</td>
                    <td className="py-3">Net {supplier.payment_terms_days}</td>
                    <td className="py-3">{supplier.currency}</td>
                    <td className="py-3">
                      <button className="text-primary-600 hover:text-primary-800 text-sm mr-2">View</button>
                      <button className="text-gray-600 hover:text-gray-800 text-sm">Edit</button>
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