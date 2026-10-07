import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LogOut, LayoutDashboard, FileText, Users, FolderKanban, CheckSquare } from 'lucide-react';

export default function AppLayout() {
  const { user, logout } = useAuth();
  const location = useLocation();

  if (!user) return null;

  const navItems = [
    { name: 'Dashboard', path: `/${user.role.toLowerCase()}`, icon: LayoutDashboard, roles: ['ADMIN', 'MANAGER'] },
    { name: 'My Tasks', path: '/my-tasks', icon: CheckSquare, roles: ['AGENT'] },
    { name: 'Transcript', path: '/admin/transcript', icon: FileText, roles: ['ADMIN'] },
    { name: 'Projects', path: '/projects', icon: FolderKanban, roles: ['ADMIN', 'MANAGER'] },
    { name: 'Team', path: '/team', icon: Users, roles: ['ADMIN'] },
  ].filter(item => item.roles.includes(user.role));

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex">
      {/* Sidebar Navigation */}
      <aside className="w-64 glass border-r border-slate-200 dark:border-slate-700 flex flex-col fixed inset-y-0 left-0 z-10">
        <div className="p-6">
          <h1 className="text-xl font-bold text-[#aa3bff]">NovaWorks</h1>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-1">{user.role}</p>
        </div>
        
        <nav className="flex-1 px-4 space-y-1.5">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive 
                    ? 'bg-[#aa3bff] text-white shadow-md shadow-[#aa3bff]/20' 
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`}
              >
                <Icon size={18} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-200 dark:border-slate-700">
          <div className="mb-4 px-2">
            <p className="text-sm font-medium text-slate-900 dark:text-white truncate">{user.name}</p>
            <p className="text-xs text-slate-500 truncate">{user.email}</p>
          </div>
          <button 
            onClick={logout}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
          >
            <LogOut size={16} />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 ml-64 p-8">
        <div className="max-w-6xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
