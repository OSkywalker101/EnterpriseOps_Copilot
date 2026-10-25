import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { User, Shield, Bell, Database, Key, Globe, Loader2 } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

export function SettingsPage() {
  const { user } = useAuth();

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500">Manage your account and application settings</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="w-5 h-5" />
            Account Settings
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
            <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
              <User className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <p className="font-medium">{user?.full_name}</p>
              <p className="text-sm text-gray-500">{user?.email}</p>
              <p className="text-sm text-gray-500 capitalize">{user?.role?.replace('_', ' ')}</p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Full Name</label>
              <input type="text" defaultValue={user?.full_name} className="input" />
            </div>
            <div>
              <label className="label">Email</label>
              <input type="email" defaultValue={user?.email} className="input" disabled />
            </div>
            <div>
              <label className="label">Department</label>
              <input type="text" defaultValue={user?.department || ''} className="input" />
            </div>
            <div>
              <label className="label">Role</label>
              <select className="input" disabled>
                <option>{user?.role?.replace('_', ' ')}</option>
              </select>
            </div>
          </div>
          <button className="btn-primary">Save Changes</button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Security
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="border-t pt-4">
            <h4 className="font-medium mb-2">Change Password</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">Current Password</label>
                <input type="password" className="input" />
              </div>
              <div>
                <label className="label">New Password</label>
                <input type="password" className="input" />
              </div>
              <div>
                <label className="label">Confirm New Password</label>
                <input type="password" className="input" />
              </div>
            </div>
            <button className="btn-primary">Update Password</button>
          </div>
          <div className="border-t pt-4">
            <h4 className="font-medium mb-2">API Keys</h4>
            <p className="text-sm text-gray-500 mb-4">Manage your API access tokens for integrations.</p>
            <button className="btn-secondary">Generate New API Key</button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="w-5 h-5" />
            Notifications
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <label className="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" defaultChecked />
            <span>Email notifications for pending approvals</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" defaultChecked />
            <span>Email notifications for overdue deliveries</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
            <span>Email notifications for low stock alerts</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer">
            <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500" defaultChecked />
            <span>In-app notifications</span>
          </label>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="w-5 h-5" />
            Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="label">Theme</label>
            <select className="input w-auto">
              <option>System</option>
              <option>Light</option>
              <option>Dark</option>
            </select>
          </div>
          <div>
            <label className="label">Date Format</label>
            <select className="input w-auto">
              <option>MMM d, yyyy</option>
              <option>yyyy-MM-dd</option>
              <option>dd/MM/yyyy</option>
            </select>
          </div>
          <div>
            <label className="label">Timezone</label>
            <select className="input w-auto">
              <option>UTC</option>
              <option>America/New_York</option>
              <option>America/Los_Angeles</option>
              <option>Europe/London</option>
              <option>Asia/Tokyo</option>
            </select>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}