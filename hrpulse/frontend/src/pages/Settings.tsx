import { User, Bell, Shield, Palette, Globe } from 'lucide-react';
import { Card, PageHeader } from '../components/ui';

export function Settings() {
  return (
    <div className="space-y-8 animate-fade-in">
      <PageHeader 
        title="Settings & Governance" 
        subtitle="Manage your executive profile, system preferences, and platform security."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Navigation / Categories */}
        <Card className="lg:col-span-1 p-0 overflow-hidden">
          <nav className="flex flex-col">
            <button className="flex items-center space-x-4 px-6 py-4 bg-hr-black text-white text-sm font-medium transition-colors">
              <User className="w-4 h-4" />
              <span>Profile Information</span>
            </button>
            <button className="flex items-center space-x-4 px-6 py-4 text-gray-500 hover:bg-gray-50 text-sm font-medium transition-colors border-b border-hr-border">
              <Bell className="w-4 h-4" />
              <span>Notifications</span>
            </button>
            <button className="flex items-center space-x-4 px-6 py-4 text-gray-500 hover:bg-gray-50 text-sm font-medium transition-colors border-b border-hr-border">
              <Shield className="w-4 h-4" />
              <span>Privacy & Security</span>
            </button>
            <button className="flex items-center space-x-4 px-6 py-4 text-gray-500 hover:bg-gray-50 text-sm font-medium transition-colors border-b border-hr-border">
              <Palette className="w-4 h-4" />
              <span>Appearance</span>
            </button>
            <button className="flex items-center space-x-4 px-6 py-4 text-gray-500 hover:bg-gray-50 text-sm font-medium transition-colors">
              <Globe className="w-4 h-4" />
              <span>Regional & Language</span>
            </button>
          </nav>
        </Card>

        {/* Content Area */}
        <Card className="lg:col-span-2 p-8">
          <div className="space-y-8">
            <section className="space-y-6">
              <h3 className="text-sm font-semibold uppercase tracking-widest text-hr-gold">Executive Profile</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="text-[10px] text-gray-500 uppercase tracking-widest mb-1 block">Full Name</label>
                  <input type="text" defaultValue="Admin User" className="input-field" />
                </div>
                <div>
                  <label className="text-[10px] text-gray-500 uppercase tracking-widest mb-1 block">Role Title</label>
                  <input type="text" defaultValue="Chief People Officer" className="input-field" disabled />
                </div>
                <div className="md:col-span-2">
                  <label className="text-[10px] text-gray-500 uppercase tracking-widest mb-1 block">Email Address</label>
                  <input type="email" defaultValue="admin@hrpulse.com" className="input-field" />
                </div>
              </div>
            </section>

            <section className="space-y-6 pt-8 border-t border-hr-border">
              <h3 className="text-sm font-semibold uppercase tracking-widest text-hr-gold">Security Credentials</h3>
              <div className="space-y-4">
                <button className="btn-secondary w-full md:w-auto">Update System Password</button>
                <button className="btn-secondary w-full md:w-auto ml-0 md:ml-4">Enable Multi-Factor Auth</button>
              </div>
            </section>

            <div className="pt-8 flex justify-end space-x-4">
              <button className="btn-secondary border-none text-gray-400">Discard Changes</button>
              <button className="btn-primary">Save Preferences</button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
