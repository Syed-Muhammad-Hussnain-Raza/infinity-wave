import { useEffect, useState } from 'react';
import { taskService } from '../../services/api';
import type { Task } from '../../types';

export default function MyTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    taskService.getMyTasks()
      .then(data => setTasks(Array.isArray(data) ? data : []))
      .catch(() => setError('Failed to load tasks.'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="mb-6 pb-4 border-b border-gray-200">
        <h1 className="text-lg font-semibold text-gray-900">My Tasks</h1>
        <p className="text-gray-500 text-sm mt-0.5">
          {loading ? 'Loading...' : `${tasks.length} task${tasks.length !== 1 ? 's' : ''} assigned to you`}
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded overflow-hidden">
        {/* Column headers */}
        <div className="grid grid-cols-12 gap-4 px-5 py-2.5 bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-400 uppercase tracking-wider">
          <div className="col-span-4">Task</div>
          <div className="col-span-3">Project</div>
          <div className="col-span-2">Deadline</div>
          <div className="col-span-2 text-right">Est. Hours</div>
          <div className="col-span-1"></div>
        </div>

        {loading ? (
          <div className="divide-y divide-gray-100">
            {[1,2,3].map(i => <div key={i} className="h-14 px-5 py-4 animate-pulse"><div className="h-3 bg-gray-100 rounded w-1/2 mb-2" /><div className="h-3 bg-gray-100 rounded w-1/3" /></div>)}
          </div>
        ) : error ? (
          <div className="px-5 py-8 text-center text-red-600 text-sm">{error}</div>
        ) : tasks.length === 0 ? (
          <div className="px-5 py-12 text-center">
            <p className="text-gray-600 font-medium mb-1">No tasks assigned</p>
            <p className="text-gray-400 text-sm">You currently have no tasks. Check back after your manager assigns work.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {tasks.map((t) => {
              const projectName = t.project_name || '—';
              const hours = t.estimated_hours != null ? `${t.estimated_hours}h` : '—';
              return (
                <div key={t.id} className="grid grid-cols-12 gap-4 px-5 py-3.5 hover:bg-gray-50 items-start">
                  <div className="col-span-4">
                    <p className="font-medium text-gray-900 text-sm">{t.title}</p>
                    {t.description && <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{t.description}</p>}
                  </div>
                  <div className="col-span-3 text-sm text-indigo-600 font-medium">{projectName}</div>
                  <div className="col-span-2 text-sm text-gray-600">{t.deadline || '—'}</div>
                  <div className="col-span-2 text-right">
                    <span className="text-xs font-semibold bg-gray-100 text-gray-600 px-2 py-0.5 rounded">{hours}</span>
                  </div>
                  <div className="col-span-1"></div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
