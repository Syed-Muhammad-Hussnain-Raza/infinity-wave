import { useEffect, useState } from 'react';
import { userService } from '../../services/api';
import { Users, Shield, Briefcase, User } from 'lucide-react';

export default function TeamDirectory() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    userService.getAll().then(data => {
      setUsers(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="p-12 text-center text-slate-500 animate-pulse font-medium">Loading team directory...</div>;

  const RoleIcon = ({ role }: { role: string }) => {
    if (role === 'ADMIN') return <Shield size={14} className="text-red-500" />;
    if (role === 'MANAGER') return <Briefcase size={14} className="text-blue-500" />;
    return <User size={14} className="text-green-500" />;
  };

  return (
    <div className="max-w-5xl">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-3">
        <Users className="text-[#aa3bff]" /> Team Directory
      </h1>
      
      <div className="glass rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 dark:bg-slate-800/80 text-slate-500 border-b border-slate-200 dark:border-slate-700">
            <tr>
              <th className="px-6 py-4 font-semibold uppercase tracking-wider text-xs">Name</th>
              <th className="px-6 py-4 font-semibold uppercase tracking-wider text-xs">Email</th>
              <th className="px-6 py-4 font-semibold uppercase tracking-wider text-xs">Role</th>
              <th className="px-6 py-4 font-semibold uppercase tracking-wider text-xs">Specialization</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-700/50 bg-white dark:bg-slate-900/20">
            {users.map(u => (
              <tr key={u.id} className="hover:bg-slate-50/80 dark:hover:bg-slate-800/50 transition-colors">
                <td className="px-6 py-4 font-bold text-slate-900 dark:text-white">{u.name}</td>
                <td className="px-6 py-4 text-slate-500 font-medium">{u.email}</td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 w-fit px-3 py-1.5 rounded-md border border-slate-200 dark:border-slate-700">
                    <RoleIcon role={u.role} /> {u.role}
                  </div>
                </td>
                <td className="px-6 py-4 text-slate-600 dark:text-slate-400 font-medium">{u.specialization}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
