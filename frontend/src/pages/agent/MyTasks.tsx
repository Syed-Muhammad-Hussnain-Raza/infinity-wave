import { useEffect, useState } from 'react';
import { taskService } from '../../services/api';
import { CheckSquare, Clock, FolderKanban, Calendar, AlertCircle } from 'lucide-react';

export default function MyTasks() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    taskService.getMyTasks()
      .then(data => setTasks(Array.isArray(data) ? data : []))
      .catch(() => setError('Failed to load tasks.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="space-y-4 max-w-4xl">
      {[1,2,3].map(i => (
        <div key={i} className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 animate-pulse h-28" />
      ))}
    </div>
  );

  if (error) return (
    <div className="bg-red-50 text-red-600 p-4 rounded-lg border border-red-100 flex items-center gap-2">
      <AlertCircle size={18} /> {error}
    </div>
  );

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-3">
        <CheckSquare className="text-[#aa3bff]" /> My Assigned Tasks
      </h1>

      {tasks.length === 0 ? (
        <div className="bg-white dark:bg-slate-800 p-12 text-center rounded-xl border border-dashed border-slate-300 dark:border-slate-600">
          <CheckSquare size={40} className="text-slate-300 mx-auto mb-4" />
          <p className="text-slate-500 font-medium">No tasks assigned to you right now.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((t: any) => {
            const projectName = t.project_name || t.projectName || '—';
            const estimatedHours = t.estimated_hours ?? t.estimatedHours ?? '—';
            return (
              <div key={t.id} className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm hover:border-[#aa3bff]/40 transition-colors">
                <div className="flex flex-wrap justify-between items-start mb-3">
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">{t.title}</h3>
                  <span className="bg-[#aa3bff]/10 text-[#aa3bff] px-3 py-1 rounded-full text-xs font-bold">
                    Due {t.deadline || '—'}
                  </span>
                </div>

                {t.description && (
                  <p className="text-sm text-slate-500 leading-relaxed mb-4">{t.description}</p>
                )}

                <div className="flex items-center gap-5 text-sm text-slate-600 dark:text-slate-400 flex-wrap">
                  <span className="flex items-center gap-1.5 font-medium">
                    <FolderKanban size={15} className="text-[#aa3bff]" /> {projectName}
                  </span>
                  <div className="w-px h-4 bg-slate-200 dark:bg-slate-600" />
                  <span className="flex items-center gap-1.5">
                    <Clock size={15} /> {estimatedHours}h estimated
                  </span>
                  {t.deadline && (
                    <>
                      <div className="w-px h-4 bg-slate-200 dark:bg-slate-600" />
                      <span className="flex items-center gap-1.5">
                        <Calendar size={15} /> {t.deadline}
                      </span>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
