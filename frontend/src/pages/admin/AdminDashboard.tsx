import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { projectService, userService } from '../../services/api';
import type { Project, User } from '../../types';

export default function AdminDashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([projectService.getAll(), userService.getAll()])
      .then(([p, u]) => {
        setProjects(Array.isArray(p) ? p : []);
        setUsers(Array.isArray(u) ? u : []);
      })
      .finally(() => setLoading(false));
  }, []);

  const totalTasks = projects.reduce((sum, p) => sum + (p.task_count || 0), 0);

  return (
    <div>
      {/* Page header */}
      <div className="mb-6 pb-4 border-b border-gray-200">
        <h1 className="text-lg font-semibold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-500 text-sm mt-0.5">NovaWorks CRM — workspace overview</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: 'Total Projects', value: loading ? '—' : projects.length, sub: 'across all managers' },
          { label: 'Total Tasks', value: loading ? '—' : totalTasks, sub: 'assigned to agents' },
          { label: 'Team Members', value: loading ? '—' : users.length, sub: 'active accounts' },
        ].map(stat => (
          <div key={stat.label} className="bg-white border border-gray-200 rounded p-5">
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            <p className="text-sm font-medium text-gray-700 mt-0.5">{stat.label}</p>
            <p className="text-xs text-gray-400 mt-0.5">{stat.sub}</p>
          </div>
        ))}
      </div>

      {/* Primary CTA */}
      <div className="bg-indigo-600 rounded p-5 mb-6 flex items-center justify-between">
        <div>
          <p className="text-white font-semibold text-base">Create Projects from Transcript</p>
          <p className="text-indigo-200 text-sm mt-0.5">Paste a meeting transcript — AI will extract projects, assign managers, and create tasks automatically.</p>
        </div>
        <Link to="/admin/transcript"
          className="shrink-0 bg-white text-indigo-700 hover:bg-indigo-50 font-semibold text-sm px-5 py-2.5 rounded transition-colors"
        >
          Open Transcript →
        </Link>
      </div>

      {/* Recent Projects */}
      <div className="bg-white border border-gray-200 rounded overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 border-b border-gray-100 bg-gray-50">
          <span className="text-sm font-semibold text-gray-700">Recent Projects</span>
          <Link to="/projects" className="text-xs text-indigo-600 hover:underline font-medium">View all →</Link>
        </div>
        {loading ? (
          <div className="divide-y divide-gray-100">
            {[1,2,3].map(i => <div key={i} className="h-12 animate-pulse bg-gray-50 mx-5 my-2 rounded" />)}
          </div>
        ) : projects.length === 0 ? (
          <div className="px-5 py-10 text-center">
            <p className="text-gray-500 text-sm font-medium">No projects yet.</p>
            <p className="text-gray-400 text-xs mt-1">Use the Transcript feature above to generate your first projects.</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 text-xs text-gray-400 uppercase tracking-wider">
                <th className="text-left px-5 py-2.5 font-semibold">Project</th>
                <th className="text-left px-5 py-2.5 font-semibold">Client</th>
                <th className="text-left px-5 py-2.5 font-semibold">Manager</th>
                <th className="text-left px-5 py-2.5 font-semibold">Deadline</th>
                <th className="text-right px-5 py-2.5 font-semibold">Tasks</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {projects.slice(0, 5).map((p) => (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-5 py-3 font-medium text-gray-900">
                    <Link to={`/projects/${p.id}`} className="hover:text-indigo-600">{p.name}</Link>
                  </td>
                  <td className="px-5 py-3 text-gray-600">{p.client_name || '—'}</td>
                  <td className="px-5 py-3 text-gray-600">{p.manager?.name || '—'}</td>
                  <td className="px-5 py-3 text-gray-600">{p.deadline || '—'}</td>
                  <td className="px-5 py-3 text-right">
                    <span className="bg-indigo-50 text-indigo-700 text-xs font-semibold px-2 py-0.5 rounded">{p.task_count ?? 0}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
