import { useState } from 'react';
import { Bot, FileText, CheckCircle2, ArrowRight, Loader2 } from 'lucide-react';
import { transcriptService } from '../../services/api';

export default function CreateTranscript() {
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!transcript.trim()) return;
    
    setIsProcessing(true);
    setError(null);
    
    try {
      // Use the centralized transcript service which currently mocks the backend
      const data = await transcriptService.process(transcript);
      
      setResult(data);
      setTranscript(''); // Clear textarea on success
    } catch (err: any) {
      setError('Failed to process transcript. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  if (result) {
    return (
      <div className="max-w-3xl mx-auto mt-8">
        <div className="glass p-10 rounded-2xl text-center border-green-200/50 dark:border-green-900/30">
          <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm">
            <CheckCircle2 size={32} />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Analysis Complete!</h2>
          <p className="text-slate-600 dark:text-slate-400 mb-10">
            The AI has successfully converted your meeting notes into actionable projects and tasks.
          </p>
          
          <div className="grid grid-cols-2 gap-6 mb-10">
            <div className="bg-white/60 dark:bg-slate-800/60 p-6 rounded-xl border border-slate-200/50 dark:border-slate-700/50 shadow-sm">
              <div className="text-5xl font-bold text-[#aa3bff] mb-2">{result.projects_created}</div>
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Projects Created</div>
            </div>
            <div className="bg-white/60 dark:bg-slate-800/60 p-6 rounded-xl border border-slate-200/50 dark:border-slate-700/50 shadow-sm">
              <div className="text-5xl font-bold text-[#aa3bff] mb-2">{result.tasks_created}</div>
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Tasks Assigned</div>
            </div>
          </div>

          <div className="bg-white/80 dark:bg-slate-800/80 rounded-xl p-6 text-left mb-8 shadow-sm border border-slate-200/50 dark:border-slate-700/50">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-4">Generated Projects Summary</h3>
            <ul className="space-y-3">
              {result.projects.map((p: any, i: number) => (
                <li key={i} className="flex items-center justify-between py-2.5 border-b border-slate-100 dark:border-slate-700/50 last:border-0">
                  <span className="font-medium text-slate-700 dark:text-slate-300 flex items-center gap-2">
                    <FolderKanban size={16} className="text-[#aa3bff]" />
                    {p.name}
                  </span>
                  <span className="text-xs font-medium text-slate-600 bg-slate-100 dark:bg-slate-800 dark:text-slate-300 px-3 py-1.5 rounded-md shadow-sm border border-slate-200 dark:border-slate-700">
                    {p.taskCount} tasks
                  </span>
                </li>
              ))}
            </ul>
          </div>
          
          <button 
            onClick={() => setResult(null)}
            className="text-[#aa3bff] font-medium hover:text-[#aa3bff]/80 transition-colors"
          >
            Process another transcript
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
          <div className="p-2.5 bg-[#aa3bff]/10 rounded-xl">
            <Bot className="text-[#aa3bff]" size={28} />
          </div>
          Create from Transcript
        </h1>
        <p className="text-slate-500 mt-3 text-lg leading-relaxed">
          Paste your raw meeting notes below. The AI will automatically extract projects, assign managers, and break down deliverables into tasks for agents.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg text-sm mb-6 border border-red-100">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="glass rounded-2xl p-1 shadow-sm">
        <div className="bg-white/50 dark:bg-slate-800/50 rounded-xl p-6">
          <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
            <FileText size={16} className="text-[#aa3bff]" />
            Meeting Transcript Input
          </div>
          
          <textarea
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder="Paste meeting transcript here...&#10;&#10;e.g., 'In today's meeting, Ayesha agreed to manage the UrbanCart redesign project...'"
            className="w-full h-[400px] p-5 bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-[#aa3bff] focus:border-[#aa3bff] outline-none transition-all resize-none font-mono text-sm leading-relaxed shadow-inner"
            disabled={isProcessing}
          />
          
          <div className="mt-6 flex justify-end">
            <button
              type="submit"
              disabled={isProcessing || !transcript.trim()}
              className="bg-[#aa3bff] hover:bg-[#aa3bff]/90 text-white px-8 py-3.5 rounded-xl font-medium flex items-center gap-2 transition-all disabled:opacity-70 disabled:cursor-not-allowed shadow-lg shadow-[#aa3bff]/20"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  Analyzing Transcript...
                </>
              ) : (
                <>
                  Generate CRM Data
                  <ArrowRight size={20} />
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

// Added this missing import for the success state UI
import { FolderKanban } from 'lucide-react';
