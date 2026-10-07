import { useEffect, useState } from 'react';
import { userService } from '../../services/api';
import { Users, Shield, Briefcase, User, AlertCircle } from 'lucide-react';

const ROLE_CONFIG: Record<string, { label: string; color: string; icon: JSX.Element }> = {
  ADMIN: { label: 'Admin', color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400', icon: <Shield size={13} /> },
  MANAGER: { label: 'Manager', color: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400', icon: <Briefcase size={13} /> },
  AGENT: { label: 'Agent', color: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400', icon: <User size={13} /> },
};

export default function TeamDirectory() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    userService.getAll()
      .then(data => setUsers(Array.isArray(data) ? data : []))
      .catch(() => setError('Failed to load team directory.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 animate-pulse h-64" />
  );

  if (error) return (
    <div className="bg-red-50 text-red-600 p-4 rounded-lg border border-red-100 flex items-center gap-2">
      <AlertCircle size={18} /> {error}
    </div>
  );

  const grouped: Record<string, any[]> = { ADMIN: [], MANAGER: [], AGENT: [] };
  users.forEach(u => {
    if (grouped[u.role]) grouped[u.role].push(u);
  });

  return (
    <div className="max-w-5xl">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-3">
        <Users className="text-[#aa3bff]" /> Team Directory
      </h1>

      <div className="space-y-8">
        {Object.entries(grouped).filter(([, members]) => members.length > 0).map(([role, members]) => {
          const cfg = ROLE_CONFIG[role];
          return (
            <div key={role}>
              <div className="flex items-center gap-2 mb-4">
                <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${cfg.color}`}>
                  {cfg.icon} {cfg.label}s
                </span>
                <span className="text-slate-400 text-sm">({members.length})</span>
              </div>

              <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden shadow-sm">
                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-700">
                    <tr>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Email</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Specialization</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-700/50">
                    {members.map((u: any) => (
                      <tr key={u.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
                        <td className="px-6 py-4 font-bold text-slate-900 dark:text-white">{u.name}</td>
                        <td className="px-6 py-4 text-slate-500">{u.email}</td>
                        <td className="px-6 py-4 text-slate-600 dark:text-slate-400">{u.specialization || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
