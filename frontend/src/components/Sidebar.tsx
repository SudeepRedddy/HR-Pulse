import { NavLink } from 'react-router-dom';
import { LayoutDashboard, BarChart3, Users, UploadCloud, Settings } from 'lucide-react';
import clsx from 'clsx';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Analytics', path: '/analytics', icon: BarChart3 },
  { name: 'Directory', path: '/employees', icon: Users },
  { name: 'Recruitment', path: '/recruitment', icon: UploadCloud },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-hr-white border-r border-hr-border h-screen sticky top-0 flex flex-col pt-8">
      <div className="px-8 pb-8 border-b border-hr-border">
        <h1 className="text-2xl font-serif tracking-tight">HRPulse</h1>
        <p className="text-[10px] tracking-[0.2em] font-sans uppercase text-gray-400 mt-1">Intelligence</p>
      </div>

      <nav className="flex-1 overflow-y-auto py-8">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center px-8 py-3 text-sm transition-all duration-200 border-r-2 group',
                    isActive
                      ? 'text-hr-black border-hr-gold bg-gray-50'
                      : 'text-gray-500 border-transparent hover:text-hr-black hover:bg-gray-50'
                  )
                }
              >
                <item.icon className="w-4 h-4 mr-4 text-inherit transition-transform duration-200 group-hover:scale-110" />
                {item.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="p-8 border-t border-hr-border">
        <NavLink 
          to="/settings"
          className={({ isActive }) => 
            clsx(
              "flex items-center text-sm transition-colors",
              isActive ? "text-hr-black font-medium" : "text-gray-500 hover:text-hr-black"
            )
          }
        >
          <Settings className="w-4 h-4 mr-4" />
          Settings
        </NavLink>
      </div>
    </aside>
  );
}
