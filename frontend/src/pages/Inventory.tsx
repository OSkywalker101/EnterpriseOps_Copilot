import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import { clsx } from 'clsx';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Loader2, Search, AlertTriangle, Box, Download } from 'lucide-react';
import { useState } from 'react';

export function InventoryPage() {
  const [filters, setFilters] = useState({ product_id: '', warehouse_id: '', page: 1 });

  const { data: balances, isLoading: loadingBalances } = useQuery({
    queryKey: ['inventoryBalances', filters],
    queryFn: () => api.getInventoryBalances({ product_id: filters.product_id || undefined, page: filters.page, page_size: 50 }),
  });

  const { data: lowStock } = useQuery({
    queryKey: ['lowStock'],
    queryFn: () => api.getLowStock(),
  });

  const { data: warehouses } = useQuery({
    queryKey: ['warehouses'],
    queryFn: () => api.getWarehouses(),
  });

  if (loadingBalances) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-primary-600" /></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inventory</h1>
          <p className="text-gray-500">View and manage inventory levels</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary">
            <Download className="w-4 h-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {lowStock && lowStock.length > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-red-800">
              <AlertTriangle className="w-5 h-5" />
              {lowStock.length} Products Below Reorder Level
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="pb-2">Product</th>
                    <th className="pb-2">Warehouse</th>
                    <th className="pb-2 text-right">On Hand</th>
                    <th className="pb-2 text-right">Reserved</th>
                    <th className="pb-2 text-right">Available</th>
                    <th className="pb-2 text-right">Reorder Level</th>
                  </tr>
                </thead>
                <tbody>
                  {lowStock.slice(0, 20).map((item: any) => (
                    <tr key={`${item.product_id}-${item.warehouse_id}`} className="border-b hover:bg-red-50">
                      <td className="py-2 font-medium">{item.product_sku} - {item.product_name}</td>
                      <td className="py-2 text-gray-600">{item.warehouse_code}</td>
                      <td className="py-2 text-right">{item.quantity_on_hand}</td>
                      <td className="py-2 text-right">{item.reserved_quantity}</td>
                      <td className="py-2 text-right font-medium text-red-600">{item.available_quantity}</td>
                      <td className="py-2 text-right">{item.reorder_level}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Inventory Balances</CardTitle>
          <div className="flex items-center gap-2">
            <select
              value={filters.warehouse_id}
              onChange={(e) => setFilters({ ...filters, warehouse_id: e.target.value, page: 1 })}
              className="input py-1 px-2 text-sm w-auto"
            >
              <option value="">All Warehouses</option>
              {warehouses?.map((w: any) => (
                <option key={w.id} value={w.id}>{w.code} - {w.name}</option>
              ))}
            </select>
            <input
              type="text"
              placeholder="Search product..."
              value={filters.product_id}
              onChange={(e) => setFilters({ ...filters, product_id: e.target.value, page: 1 })}
              className="input py-1 px-2 text-sm w-64"
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-3">Product</th>
                  <th className="pb-3">Warehouse</th>
                  <th className="pb-3 text-right">On Hand</th>
                  <th className="pb-3 text-right">Reserved</th>
                  <th className="pb-3 text-right">Available</th>
                  <th className="pb-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {balances?.items?.map((item: any) => (
                  <tr key={`${item.product_id}-${item.warehouse_id}`} className="border-b hover:bg-gray-50">
                    <td className="py-3 font-medium">{item.product_sku} - {item.product_name}</td>
                    <td className="py-3">{item.warehouse_code}</td>
                    <td className="py-3 text-right">{item.quantity_on_hand}</td>
                    <td className="py-3 text-right">{item.reserved_quantity}</td>
                    <td className="py-3 text-right font-medium">{item.available_quantity}</td>
                    <td className="py-3">
                      {item.available_quantity <= (item.reorder_level || 0) ? (
                        <span className="badge badge-danger">Low Stock</span>
                      ) : item.available_quantity < (item.reorder_level || 0) * 2 ? (
                        <span className="badge badge-warning">Watch</span>
                      ) : (
                        <span className="badge badge-success">OK</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {balances && balances.total_pages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <span className="text-sm text-gray-500">
                Page {balances.page} of {balances.total_pages} â€¢ {balances.total} total
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
                  disabled={filters.page >= balances.total_pages}
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