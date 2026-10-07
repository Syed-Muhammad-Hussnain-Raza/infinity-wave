import { useEffect, useState } from 'react';
import { userService } from '../../services/api';
import type { User, Role } from '../../types';

const ROLE_ORDER: Role[] = ['ADMIN', 'MANAGER', 'AGENT'];
const ROLE_LABELS: Record<Role, string> = { ADMIN: 'Administrators', MANAGER: 'Managers', AGENT: 'Agents' };
const ROLE_BADGE: Record<Role, string> = {
  ADMIN: 'text-red-600 bg-red-50 border border-red-200',
  MANAGER: 'text-blue-600 bg-blue-50 border border-blue-200',
  AGENT: 'text-green-600 bg-green-50 border border-green-200',
};

export default function TeamDirectory() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    userService.getAll()
      .then(data => setUsers(Array.isArray(data) ? data : []))
      .catch(() => setError('Failed to load team.'))
      .finally(() => setLoading(false));
  }, []);

  const grouped: Record<Role, User[]> = { ADMIN: [], MANAGER: [], AGENT: [] };
  users.forEach(u => {
    if (grouped[u.role]) {
      grouped[u.role].push(u);
    }
  });

  return (
    <div>
      <div className="mb-6 pb-4 border-b border-gray-200">
        <h1 className="text-lg font-semibold text-gray-900">Team Directory</h1>
        <p className="text-gray-500 text-sm mt-0.5">{loading ? 'Loading...' : `${users.length} members`}</p>
      </div>

      {error && <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded mb-4">{error}</div>}

      <div className="space-y-5">
        {ROLE_ORDER.map(role => {
          const members = grouped[role] || [];
          if (members.length === 0) return null;
          return (
            <div key={role}>
              <div className="flex items-center gap-2 mb-2">
                <span className={`text-xs font-semibold px-2 py-0.5 rounded ${ROLE_BADGE[role]}`}>{ROLE_LABELS[role]}</span>
                <span className="text-gray-400 text-xs">({members.length})</span>
              </div>

              <div className="bg-white border border-gray-200 rounded overflow-hidden">
                <div className="grid grid-cols-12 gap-4 px-5 py-2.5 bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  <div className="col-span-3">Name</div>
                  <div className="col-span-4">Email</div>
                  <div className="col-span-3">Specialization</div>
                  <div className="col-span-2 text-right">Role</div>
                </div>
                <div className="divide-y divide-gray-100">
                  {members.map((u) => (
                    <div key={u.id} className="grid grid-cols-12 gap-4 px-5 py-3 hover:bg-gray-50 items-center">
                      <div className="col-span-3 flex items-center gap-2.5">
                        <div className="w-7 h-7 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs font-bold shrink-0">
                          {u.name?.charAt(0) ?? '?'}
                        </div>
                        <span className="font-medium text-gray-900 text-sm">{u.name}</span>
                      </div>
                      <div className="col-span-4 text-sm text-gray-500">{u.email}</div>
                      <div className="col-span-3 text-sm text-gray-600">{u.specialization || '—'}</div>
                      <div className="col-span-2 text-right">
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded ${ROLE_BADGE[u.role]}`}>{u.role}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
