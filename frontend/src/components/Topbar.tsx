import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut } from 'lucide-react';

export function Topbar() {
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('hrpulse_token');
    navigate('/login');
  };

  return (
    <header className="h-16 bg-hr-white border-b border-hr-border flex items-center justify-between px-8 sticky top-0 z-10">
      <div className="flex items-center text-sm text-gray-500 font-sans tracking-wide">
        <span>Strategic Platform</span>
        <span className="mx-3 text-hr-border">/</span>
        <span className="text-hr-black">HR Intelligence</span>
      </div>

      <div className="flex items-center space-x-6">
        <div className="flex flex-col items-end">
          <span className="text-sm font-medium">Admin User</span>
          <span className="text-xs text-hr-gold tracking-widest uppercase">C-Suite</span>
        </div>
        <div className="relative">
          <button 
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="w-8 h-8 bg-hr-black text-hr-white flex items-center justify-center rounded text-sm font-serif cursor-pointer hover:bg-gray-800 transition-colors"
          >
            A
          </button>
          
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-white border border-hr-border shadow-sm rounded flex flex-col py-1 animate-fade-in z-50">
              <button 
                onClick={handleLogout}
                className="flex items-center px-4 py-2 text-sm text-hr-danger hover:bg-red-50 transition-colors w-full text-left"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
