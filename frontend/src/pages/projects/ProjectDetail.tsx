import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { projectService } from '../../services/api';

export default function ProjectDetail() {
  const { id } = useParams();
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) projectService.getById(id).then(setProject).catch(() => setError('Project not found.')).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-gray-500 py-8 text-sm text-center">Loading project...</div>;
  if (error) return <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded">{error}</div>;
  if (!project) return null;

  const tasks = project.tasks || [];
  const managerName = project.manager?.name || project.manager || '—';

  return (
    <div>
      {/* Breadcrumb */}
      <div className="mb-5 text-sm">
        <Link to="/projects" className="text-indigo-600 hover:underline">Projects</Link>
        <span className="text-gray-400 mx-2">/</span>
        <span className="text-gray-700">{project.name}</span>
      </div>

      {/* Project header */}
      <div className="bg-white border border-gray-200 rounded p-6 mb-5">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-lg font-semibold text-gray-900">{project.name}</h1>
            {project.client && <p className="text-gray-500 text-sm mt-0.5">{project.client}</p>}
          </div>
          <span className="text-xs font-semibold bg-green-100 text-green-700 px-2.5 py-1 rounded border border-green-200">Active</span>
        </div>

        {project.description && (
          <p className="text-gray-600 text-sm leading-relaxed border-t border-gray-100 pt-4 mb-4">{project.description}</p>
        )}

        <div className="grid grid-cols-3 gap-6 border-t border-gray-100 pt-4 text-sm">
          <div>
            <p className="text-xs text-gray-400 font-semibold uppercase tracking-wider mb-1">Manager</p>
            <p className="text-gray-900 font-medium">{managerName}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 font-semibold uppercase tracking-wider mb-1">Deadline</p>
            <p className="text-gray-900 font-medium">{project.deadline || '—'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400 font-semibold uppercase tracking-wider mb-1">Total Tasks</p>
            <p className="text-gray-900 font-medium">{tasks.length}</p>
          </div>
        </div>
      </div>

      {/* Tasks table */}
      <div className="bg-white border border-gray-200 rounded overflow-hidden">
        <div className="px-5 py-3 border-b border-gray-200 bg-gray-50 flex items-center gap-2">
          <span className="text-sm font-semibold text-gray-700">Tasks</span>
          <span className="text-xs text-gray-400 font-medium">({tasks.length})</span>
        </div>

        {tasks.length === 0 ? (
          <div className="px-5 py-10 text-center text-sm text-gray-500">No tasks assigned yet.</div>
        ) : (
          <>
            <div className="grid grid-cols-12 gap-4 px-5 py-2.5 bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-400 uppercase tracking-wider">
              <div className="col-span-4">Task</div>
              <div className="col-span-3">Assigned To</div>
              <div className="col-span-2">Deadline</div>
              <div className="col-span-2 text-right">Est. Hours</div>
              <div className="col-span-1"></div>
            </div>
            <div className="divide-y divide-gray-100">
              {tasks.map((t: any) => {
                const agentName = t.assigned_to?.name || t.assigned_to || t.assignedTo || '—';
                return (
                  <div key={t.id} className="grid grid-cols-12 gap-4 px-5 py-3.5 hover:bg-gray-50 items-start">
                    <div className="col-span-4">
                      <p className="font-medium text-gray-900 text-sm">{t.title}</p>
                      {t.description && <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{t.description}</p>}
                    </div>
                    <div className="col-span-3 text-sm text-gray-600">{agentName}</div>
                    <div className="col-span-2 text-sm text-gray-600">{t.deadline || '—'}</div>
                    <div className="col-span-2 text-right">
                      <span className="text-xs font-semibold bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{t.estimated_hours ?? t.estimatedHours ?? '—'}h</span>
                    </div>
                    <div className="col-span-1"></div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
