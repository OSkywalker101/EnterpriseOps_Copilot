import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';
import { clsx } from 'clsx';
import { Box, AlertTriangle, TrendingUp, Package, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { format } from 'date-fns';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: { value: number; label: string };
  className?: string;
}

function MetricCard({ title, value, icon, trend, className }: MetricCardProps) {
  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-gray-500">{title}</CardTitle>
        <div className="p-2 bg-gray-100 rounded-lg">{icon}</div>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold text-gray-900">{value}</div>
        {trend && (
          <div className={clsx('text-sm mt-1', trend.value >= 0 ? 'text-green-600' : 'text-red-600')}>
            {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}% {trend.label}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function InventoryDashboard() {
  const { data: lowStock } = useQuery({
    queryKey: ['lowStock'],
    queryFn: () => api.getLowStock(),
  });

  const { data: balances } = useQuery({
    queryKey: ['inventoryBalances'],
    queryFn: () => api.getInventoryBalances({ page_size: 1000 }),
  });

  const { data: movements } = useQuery({
    queryKey: ['recentMovements'],
    queryFn: () => api.getInventoryMovements({ page_size: 20 }),
  });

  const isLoading = !lowStock || !balances;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  const lowStockCount = lowStock.length;
  const totalProducts = new Set(balances.items?.map((b: any) => b.product_id) || []).size;
  const totalWarehouses = new Set(balances.items?.map((b: any) => b.warehouse_id) || []).size;
  const totalOnHand = balances.items?.reduce((sum: number, b: any) => sum + b.quantity_on_hand, 0) || 0;
  const totalReserved = balances.items?.reduce((sum: number, b: any) => sum + b.reserved_quantity, 0) || 0;
  const totalAvailable = totalOnHand - totalReserved;

  const recentMovements = movements?.items?.slice(0, 10) || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inventory Dashboard</h1>
          <p className="text-gray-500">Overview of inventory levels and movements</p>
        </div>
        <div className="text-sm text-gray-500">
          Updated {format(new Date(), 'MMM d, yyyy HH:mm')}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Products Below Reorder"
          value={lowStockCount}
          icon={<AlertTriangle className="w-6 h-6 text-red-600" />}
        />
        <MetricCard
          title="Total Products Tracked"
          value={totalProducts}
          icon={<Package className="w-6 h-6 text-primary-600" />}
        />
        <MetricCard
          title="Quantity On Hand"
          value={totalOnHand.toLocaleString()}
          icon={<Box className="w-6 h-6 text-blue-600" />}
        />
        <MetricCard
          title="Available Quantity"
          value={totalAvailable.toLocaleString()}
          icon={<TrendingUp className="w-6 h-6 text-green-600" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Products Below Reorder Level
            </CardTitle>
          </CardHeader>
          <CardContent>
            {lowStock.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-500 border-b">
                      <th className="pb-2">Product</th>
                      <th className="pb-2">Warehouse</th>
                      <th className="pb-2 text-right">On Hand</th>
                      <th className="pb-2 text-right">Reserved</th>
                      <th className="pb-2 text-right">Available</th>
                      <th className="pb-2 text-right">Reorder</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lowStock.slice(0, 15).map((item: any) => (
                      <tr key={`${item.product_id}-${item.warehouse_id}`} className="border-b hover:bg-gray-50">
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
            ) : (
              <p className="text-gray-500 text-center py-4">All products above reorder level</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="w-5 h-5" />
              Recent Stock Movements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentMovements.length > 0 ? (
                recentMovements.map((movement: any) => (
                  <div key={movement.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={clsx('p-2 rounded-lg', getMovementColor(movement.movement_type))}>
                        {getMovementIcon(movement.movement_type)}
                      </div>
                      <div>
                        <p className="font-medium">{movement.product_sku}</p>
                        <p className="text-sm text-gray-500">{movement.warehouse_code} • {movement.movement_type.replace('_', ' ')}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={clsx('font-medium', movement.movement_type === 'receipt' ? 'text-green-600' : 'text-red-600')}>
                        {movement.movement_type === 'receipt' ? '+' : '-'}{movement.quantity}
                      </p>
                      <p className="text-xs text-gray-500">{format(new Date(movement.created_at), 'MMM d, HH:mm')}</p>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-gray-500 text-center py-4">No recent movements</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Inventory by Warehouse</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="pb-2">Warehouse</th>
                    <th className="pb-2 text-right">Products</th>
                    <th className="pb-2 text-right">On Hand</th>
                    <th className="pb-2 text-right">Reserved</th>
                    <th className="pb-2 text-right">Available</th>
                    <th className="pb-2">Low Stock</th>
                  </tr>
                </thead>
                <tbody>
                  {balances.items?.reduce((acc: any, item: any) => {
                    if (!acc[item.warehouse_id]) {
                      acc[item.warehouse_id] = {
                        code: item.warehouse_code,
                        products: new Set(),
                        onHand: 0,
                        reserved: 0,
                        lowStock: 0,
                      };
                    }
                    acc[item.warehouse_id].products.add(item.product_id);
                    acc[item.warehouse_id].onHand += item.quantity_on_hand;
                    acc[item.warehouse_id].reserved += item.reserved_quantity;
                    if (item.available_quantity <= (item.reorder_level || 0)) {
                      acc[item.warehouse_id].lowStock++;
                    }
                    return acc;
                  }, {}) && Object.entries(balances.items?.reduce((acc: any, item: any) => {
                    if (!acc[item.warehouse_id]) {
                      acc[item.warehouse_id] = { code: item.warehouse_code, products: new Set(), onHand: 0, reserved: 0, lowStock: 0 };
                    }
                    acc[item.warehouse_id].products.add(item.product_id);
                    acc[item.warehouse_id].onHand += item.quantity_on_hand;
                    acc[item.warehouse_id].reserved += item.reserved_quantity;
                    if (item.available_quantity <= (item.reorder_level || 0)) acc[item.warehouse_id].lowStock++;
                    return acc;
                  }, {})).map(([id, data]: any) => (
                    <tr key={id} className="border-b hover:bg-gray-50">
                      <td className="py-2 font-medium">{data.code}</td>
                      <td className="py-2 text-right">{data.products.size}</td>
                      <td className="py-2 text-right">{data.onHand.toLocaleString()}</td>
                      <td className="py-2 text-right">{data.reserved.toLocaleString()}</td>
                      <td className="py-2 text-right">{(data.onHand - data.reserved).toLocaleString()}</td>
                      <td className="py-2">
                        {data.lowStock > 0 ? (
                          <span className="badge badge-danger">{data.lowStock}</span>
                        ) : (
                          <span className="badge badge-success">0</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <button className="btn-secondary w-full justify-start gap-2">
              <Box className="w-4 h-4" />
              View All Inventory
            </button>
            <button className="btn-secondary w-full justify-start gap-2">
              <AlertTriangle className="w-4 h-4" />
              Replenishment Recommendations
            </button>
            <button className="btn-secondary w-full justify-start gap-2">
              <Package className="w-4 h-4" />
              Stock Movement History
            </button>
            <button className="btn-secondary w-full justify-start gap-2">
              <TrendingUp className="w-4 h-4" />
              Inventory Analytics
            </button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function getMovementColor(type: string) {
  switch (type) {
    case 'receipt': return 'bg-green-100 text-green-600';
    case 'issue': return 'bg-red-100 text-red-600';
    case 'transfer_in': return 'bg-blue-100 text-blue-600';
    case 'transfer_out': return 'bg-orange-100 text-orange-600';
    case 'adjustment': return 'bg-yellow-100 text-yellow-600';
    default: return 'bg-gray-100 text-gray-600';
  }
}

function getMovementIcon(type: string) {
  return <Box className="w-5 h-5" />;
}