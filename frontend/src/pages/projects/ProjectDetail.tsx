import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { projectService } from '../../services/api';
import { ArrowLeft, Clock, User, CheckCircle2, Calendar, Building2, AlertCircle } from 'lucide-react';

export default function ProjectDetail() {
  const { id } = useParams();
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      projectService.getById(id)
        .then(data => setProject(data))
        .catch(() => setError('Project not found or you do not have access.'))
        .finally(() => setLoading(false));
    }
  }, [id]);

  if (loading) return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl border border-slate-200 dark:border-slate-700 animate-pulse h-40" />
      <div className="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 animate-pulse h-20" />
    </div>
  );

  if (error) return (
    <div className="bg-red-50 text-red-600 p-4 rounded-lg border border-red-100 flex items-center gap-2 max-w-xl">
      <AlertCircle size={18} /> {error}
    </div>
  );

  if (!project) return null;

  const tasks = project.tasks || [];
  const managerName = project.manager?.name || project.manager || '—';

  return (
    <div className="max-w-5xl mx-auto">
      <Link to="/projects" className="inline-flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-[#aa3bff] mb-6 transition-colors">
        <ArrowLeft size={16} /> Back to Projects
      </Link>

      {/* Project Header */}
      <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm mb-6">
        <div className="flex flex-wrap justify-between items-start gap-4 mb-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">{project.name}</h1>
            <p className="text-lg text-slate-500 mt-1">{project.client}</p>
          </div>
          <span className="bg-[#aa3bff]/10 text-[#aa3bff] px-4 py-1.5 rounded-full text-sm font-semibold">
            Active
          </span>
        </div>

        {project.description && (
          <p className="text-slate-600 dark:text-slate-400 leading-relaxed mt-4 pb-6 border-b border-slate-100 dark:border-slate-700">
            {project.description}
          </p>
        )}

        <div className="flex flex-wrap gap-6 mt-5 text-sm">
          <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
            <User size={15} className="text-[#aa3bff]" />
            <span className="font-medium">Manager:</span>
            <span className="font-bold text-slate-900 dark:text-white">{managerName}</span>
          </div>
          <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
            <Calendar size={15} className="text-[#aa3bff]" />
            <span className="font-medium">Deadline:</span>
            <span className="font-bold text-slate-900 dark:text-white">{project.deadline || '—'}</span>
          </div>
          {project.client && (
            <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400">
              <Building2 size={15} className="text-[#aa3bff]" />
              <span className="font-medium">Client:</span>
              <span className="font-bold text-slate-900 dark:text-white">{project.client}</span>
            </div>
          )}
        </div>
      </div>

      {/* Tasks */}
      <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
        <CheckCircle2 className="text-[#aa3bff]" size={20} />
        Tasks ({tasks.length})
      </h2>

      {tasks.length === 0 ? (
        <div className="bg-white dark:bg-slate-800 p-10 text-center rounded-xl border border-dashed border-slate-300 dark:border-slate-600">
          <p className="text-slate-500">No tasks assigned to this project yet.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {tasks.map((t: any) => {
            const agentName = t.assigned_to?.name || t.assigned_to || t.assignedTo || '—';
            return (
              <div key={t.id} className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm hover:border-[#aa3bff]/40 transition-colors">
                <div className="flex flex-wrap justify-between items-start gap-3 mb-2">
                  <h3 className="font-bold text-slate-900 dark:text-white text-base">{t.title}</h3>
                  <div className="flex items-center gap-4 text-sm text-slate-500">
                    <span className="flex items-center gap-1.5">
                      <User size={14} className="text-[#aa3bff]" /> {agentName}
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Calendar size={14} /> {t.deadline || '—'}
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Clock size={14} /> {t.estimated_hours ?? t.estimatedHours ?? '—'}h
                    </span>
                  </div>
                </div>
                {t.description && (
                  <p className="text-sm text-slate-500 leading-relaxed">{t.description}</p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
