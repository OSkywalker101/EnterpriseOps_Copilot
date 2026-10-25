import { NavLink, useLocation } from 'react-router-dom';
import { clsx } from 'clsx';
import {
  LayoutDashboard,
  MessageSquare,
  Package,
  Box,
  Truck,
  FileText,
  Settings,
  HelpCircle,
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
  { name: 'Procurement', href: '/procurement', icon: Package },
  { name: 'Inventory', href: '/inventory', icon: Box },
  { name: 'Suppliers', href: '/suppliers', icon: Truck },
  { name: 'Invoices', href: '/invoices', icon: FileText },
  { name: 'Settings', href: '/settings', icon: Settings },
  { name: 'Help', href: '/help', icon: HelpCircle },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Navigation</h2>
      </div>
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href || location.pathname.startsWith(item.href + '/');
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={clsx(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              <Icon className={clsx('w-5 h-5', isActive ? 'text-primary-600' : 'text-gray-400')} />
              {item.name}
            </NavLink>
          );
        })}
      </nav>
      <div className="p-4 border-t border-gray-200 text-xs text-gray-500">
        EnterpriseOps Copilot v1.0
      </div>
    </aside>
  );
}