import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { projectService } from '../../services/api';
import { FolderKanban, Calendar, User, ListTodo, AlertCircle } from 'lucide-react';

export default function ProjectList({ title = 'Projects' }: { title?: string }) {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    projectService.getAll()
      .then(data => setProjects(Array.isArray(data) ? data : []))
      .catch(() => setError('Failed to load projects.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[1,2,3].map(i => (
        <div key={i} className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 animate-pulse h-48" />
      ))}
    </div>
  );

  if (error) return (
    <div className="bg-red-50 text-red-600 p-4 rounded-lg border border-red-100 flex items-center gap-2">
      <AlertCircle size={18} /> {error}
    </div>
  );

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-3">
        <FolderKanban className="text-[#aa3bff]" /> {title}
      </h1>

      {projects.length === 0 ? (
        <div className="bg-white dark:bg-slate-800 p-12 text-center rounded-xl border border-dashed border-slate-300 dark:border-slate-600">
          <FolderKanban size={40} className="text-slate-300 mx-auto mb-4" />
          <p className="text-slate-500 font-medium">No projects yet.</p>
          <p className="text-slate-400 text-sm mt-1">An admin can create projects from a meeting transcript.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((p: any) => (
            <Link
              key={p.id}
              to={`/projects/${p.id}`}
              className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-[#aa3bff]/50 hover:-translate-y-0.5 hover:shadow-md transition-all block"
            >
              <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1 truncate">{p.name}</h2>
              <p className="text-sm font-medium text-slate-400 mb-5">{p.client}</p>

              <div className="space-y-2.5 text-sm text-slate-600 dark:text-slate-400">
                <div className="flex items-center gap-2.5">
                  <User size={15} className="text-slate-400 shrink-0" />
                  <span className="truncate">{p.manager?.name || p.manager || '—'}</span>
                </div>
                <div className="flex items-center gap-2.5">
                  <Calendar size={15} className="text-slate-400 shrink-0" />
                  <span>{p.deadline || '—'}</span>
                </div>
              </div>

              <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-700 flex items-center gap-2 text-sm font-semibold text-[#aa3bff]">
                <ListTodo size={15} />
                {p.task_count ?? 0} Tasks
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
