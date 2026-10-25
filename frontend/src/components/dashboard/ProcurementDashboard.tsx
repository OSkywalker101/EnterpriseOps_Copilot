import { useQuery } from '@tanstack/react-query';
import { api } from '../../services/api';
import { clsx } from 'clsx';
import {
  Package,
  Clock,
  AlertTriangle,
  TrendingUp,
  Box,
  DollarSign,
  Users,
  FileText,
  Loader2,
} from 'lucide-react';
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

export function ProcurementDashboard() {
  const { data: pendingApprovals, isLoading: loadingApprovals } = useQuery({
    queryKey: ['pendingApprovals'],
    queryFn: () => api.getPendingApprovals(),
  });

  const { data: overdueDeliveries, isLoading: loadingOverdue } = useQuery({
    queryKey: ['overdueDeliveries'],
    queryFn: () => api.getOverdueDeliveries(),
  });

  const { data: purchaseOrders } = useQuery({
    queryKey: ['purchaseOrders'],
    queryFn: () => api.getPurchaseOrders({ page_size: 100 }),
  });

  const { data: invoices } = useQuery({
    queryKey: ['invoices'],
    queryFn: () => api.getInvoices({ status: 'discrepancy', page_size: 100 }),
  });

  const isLoading = loadingApprovals || loadingOverdue;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  const totalPOValue = purchaseOrders?.items?.reduce((sum: number, po: any) => sum + po.total_amount, 0) || 0;
  const pendingCount = pendingApprovals?.length || 0;
  const overdueCount = overdueDeliveries?.length || 0;
  const discrepancyCount = invoices?.items?.length || 0;

  const recentPOs = purchaseOrders?.items?.slice(0, 5) || [];
  const recentOverdue = overdueDeliveries?.slice(0, 5) || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Procurement Dashboard</h1>
          <p className="text-gray-500">Overview of procurement operations</p>
        </div>
        <div className="text-sm text-gray-500">
          Updated {format(new Date(), 'MMM d, yyyy HH:mm')}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Pending Approvals"
          value={pendingCount}
          icon={<Package className="w-6 h-6 text-primary-600" />}
          trend={{ value: 12, label: 'vs last week' }}
        />
        <MetricCard
          title="Overdue Deliveries"
          value={overdueCount}
          icon={<AlertTriangle className="w-6 h-6 text-red-600" />}
          trend={{ value: -5, label: 'vs last week' }}
        />
        <MetricCard
          title="Invoice Discrepancies"
          value={discrepancyCount}
          icon={<FileText className="w-6 h-6 text-yellow-600" />}
        />
        <MetricCard
          title="Total Outstanding PO Value"
          value={`$${totalPOValue.toLocaleString()}`}
          icon={<DollarSign className="w-6 h-6 text-green-600" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Pending Approvals
            </CardTitle>
          </CardHeader>
          <CardContent>
            {pendingApprovals && pendingApprovals.length > 0 ? (
              <div className="space-y-3">
                {pendingApprovals.slice(0, 10).map((po: any) => (
                  <div key={po.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium">{po.po_number}</p>
                      <p className="text-sm text-gray-500">{po.supplier_name} • ${po.total_amount.toLocaleString()}</p>
                    </div>
                    <span className="badge badge-warning">Pending</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No pending approvals</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Overdue Deliveries
            </CardTitle>
          </CardHeader>
          <CardContent>
            {overdueDeliveries && overdueDeliveries.length > 0 ? (
              <div className="space-y-3">
                {recentOverdue.map((po: any) => (
                  <div key={po.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium">{po.po_number}</p>
                      <p className="text-sm text-gray-500">
                        {po.supplier} • Expected: {po.expected_date ? format(new Date(po.expected_date), 'MMM d') : 'N/A'}
                      </p>
                    </div>
                    <span className="badge badge-danger">Overdue</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No overdue deliveries</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="w-5 h-5" />
              Recent Purchase Orders
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentPOs.map((po: any) => (
                <div key={po.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">{po.po_number}</p>
                    <p className="text-sm text-gray-500">{po.supplier_name} • ${po.total_amount.toLocaleString()}</p>
                  </div>
                  <span className={clsx('badge', getStatusBadge(po.status))}>{po.status.replace('_', ' ')}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Invoice Discrepancies
            </CardTitle>
          </CardHeader>
          <CardContent>
            {invoices?.items && invoices.items.length > 0 ? (
              <div className="space-y-3">
                {invoices.items.slice(0, 10).map((inv: any) => (
                  <div key={inv.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium">{inv.invoice_number}</p>
                      <p className="text-sm text-gray-500">{inv.supplier?.name} • ${inv.total_amount.toLocaleString()}</p>
                    </div>
                    <span className="badge badge-danger">Discrepancy</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No invoice discrepancies</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function getStatusBadge(status: string) {
  switch (status) {
    case 'pending_approval': return 'badge-warning';
    case 'approved': return 'badge-info';
    case 'ordered': return 'badge-info';
    case 'partially_received': return 'badge-warning';
    case 'received': return 'badge-success';
    case 'cancelled': return 'badge-gray';
    default: return 'badge-gray';
  }
}