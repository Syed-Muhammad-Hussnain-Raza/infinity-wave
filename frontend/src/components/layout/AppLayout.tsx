import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function AppLayout() {
  const { user, logout } = useAuth();
  const { pathname } = useLocation();
  if (!user) return null;

  const navGroups = [
    {
      label: null,
      items: [
        { name: 'Dashboard', path: '/admin', roles: ['ADMIN'] },
        { name: 'My Projects', path: '/manager', roles: ['MANAGER'] },
        { name: 'My Tasks', path: '/my-tasks', roles: ['AGENT'] },
      ]
    },
    {
      label: 'Management',
      items: [
        { name: 'Create from Transcript', path: '/admin/transcript', roles: ['ADMIN'] },
        { name: 'All Projects', path: '/projects', roles: ['ADMIN', 'MANAGER'] },
        { name: 'Team Directory', path: '/team', roles: ['ADMIN'] },
      ]
    }
  ];

  const roleColors: Record<string, string> = {
    ADMIN: 'text-red-600 bg-red-50 border-red-200',
    MANAGER: 'text-blue-600 bg-blue-50 border-blue-200',
    AGENT: 'text-green-600 bg-green-50 border-green-200',
  };

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Sidebar */}
      <aside className="w-56 bg-white border-r border-gray-200 flex flex-col fixed inset-y-0 left-0 z-20">
        {/* Logo */}
        <div className="px-4 h-14 flex items-center border-b border-gray-200">
          <span className="text-indigo-600 font-bold text-base tracking-tight">NovaWorks</span>
          <span className="ml-2 text-gray-400 text-xs font-medium">CRM</span>
        </div>

        {/* Nav */}
        <nav className="flex-1 py-3 overflow-y-auto">
          {navGroups.map((group, gi) => {
            const items = group.items.filter(i => i.roles.includes(user.role));
            if (items.length === 0) return null;
            return (
              <div key={gi} className="mb-1">
                {group.label && (
                  <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-widest px-4 py-2">{group.label}</p>
                )}
                {items.map(item => {
                  const isActive = pathname === item.path || (item.path !== '/admin' && item.path !== '/manager' && item.path !== '/my-tasks' && pathname.startsWith(item.path));
                  return (
                    <Link
                      key={item.path} to={item.path}
                      className={`flex items-center px-4 py-2 text-sm transition-colors ${
                        isActive
                          ? 'bg-indigo-50 text-indigo-700 font-semibold border-r-2 border-indigo-600'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      }`}
                    >
                      {item.name}
                    </Link>
                  );
                })}
              </div>
            );
          })}
        </nav>

        {/* User */}
        <div className="border-t border-gray-200 p-3">
          <div className="flex items-center gap-2.5 px-1 mb-2">
            <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-sm font-bold shrink-0">
              {user.name.charAt(0)}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-gray-900 truncate leading-tight">{user.name}</p>
              <span className={`text-[10px] font-semibold border px-1.5 py-0.5 rounded ${roleColors[user.role]}`}>
                {user.role}
              </span>
            </div>
          </div>
          <button onClick={logout}
            className="w-full text-left px-2 py-1.5 text-sm text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 ml-56 min-h-screen">
        <div className="max-w-5xl mx-auto px-8 py-7">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
