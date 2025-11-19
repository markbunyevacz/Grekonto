import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, CheckSquare, History, Settings, LogOut } from 'lucide-react';
import clsx from 'clsx';

export default function Layout() {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Műszerfal', icon: LayoutDashboard },
    { path: '/matcher', label: 'Párosítás', icon: CheckSquare }, // Usually hidden if no task selected, but good for dev
    { path: '/history', label: 'Előzmények', icon: History },
    { path: '/settings', label: 'Beállítások', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col">
        <div className="p-6 border-b border-slate-100">
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold">G</div>
            GREKONTO AI
          </h1>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={clsx(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                  isActive 
                    ? "bg-indigo-50 text-indigo-700" 
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                )}
              >
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-100">
          <div className="flex items-center gap-3 px-3 py-2 text-sm font-medium text-slate-600">
            <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center text-slate-500">
              OR
            </div>
            <div className="flex-1">
              <p className="text-slate-900">Orbita</p>
              <p className="text-xs text-slate-500">Asszisztens</p>
            </div>
            <Link to="/" className="text-slate-400 hover:text-slate-600">
              <LogOut size={18} />
            </Link>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
