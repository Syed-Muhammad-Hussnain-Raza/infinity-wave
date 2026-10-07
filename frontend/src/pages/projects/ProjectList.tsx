import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { projectService } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import type { Project } from '../../types';

export default function ProjectList({ title = 'All Projects' }: { title?: string }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    projectService.getAll()
      .then(data => setProjects(Array.isArray(data) ? data : []))
      .catch(() => setError('Failed to load projects.'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="mb-6 pb-4 border-b border-gray-200 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-gray-900">{title}</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            {loading ? 'Loading...' : `${projects.length} project${projects.length !== 1 ? 's' : ''}`}
          </p>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded overflow-hidden">
        {/* Table header */}
        <div className="grid grid-cols-12 gap-4 px-5 py-2.5 bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-400 uppercase tracking-wider">
          <div className="col-span-4">Project Name</div>
          <div className="col-span-2">Client</div>
          <div className="col-span-3">Manager</div>
          <div className="col-span-2">Deadline</div>
          <div className="col-span-1 text-right">Tasks</div>
        </div>

        {loading ? (
          <div className="divide-y divide-gray-100">
            {[1,2,3,4].map(i => <div key={i} className="h-12 px-5 py-3 animate-pulse"><div className="h-4 bg-gray-100 rounded w-2/3" /></div>)}
          </div>
        ) : error ? (
          <div className="px-5 py-8 text-center text-red-600 text-sm">{error}</div>
        ) : projects.length === 0 ? (
          <div className="px-5 py-12 text-center">
            <p className="text-gray-600 font-medium mb-1">No projects found</p>
            <p className="text-gray-400 text-sm">No projects currently available.</p>
            {user?.role === 'ADMIN' && (
              <Link to="/admin/transcript" className="inline-block mt-4 bg-indigo-600 text-white text-sm font-medium px-4 py-2 rounded hover:bg-indigo-700 transition-colors">
                Create from Transcript →
              </Link>
            )}
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {projects.map((p) => (
              <Link
                key={p.id}
                to={`/projects/${p.id}`}
                className="grid grid-cols-12 gap-4 px-5 py-3.5 hover:bg-gray-50 transition-colors items-center"
              >
                <div className="col-span-4 font-medium text-gray-900 hover:text-indigo-600 truncate">{p.name}</div>
                <div className="col-span-2 text-gray-600 text-sm truncate">{p.client_name || '—'}</div>
                <div className="col-span-3 text-gray-600 text-sm truncate">{p.manager?.name || '—'}</div>
                <div className="col-span-2 text-gray-600 text-sm">{p.deadline || '—'}</div>
                <div className="col-span-1 text-right">
                  <span className="text-xs font-semibold bg-indigo-50 text-indigo-700 px-2 py-1 rounded">{p.task_count ?? 0}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
