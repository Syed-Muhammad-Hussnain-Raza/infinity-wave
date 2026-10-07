import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { transcriptService } from '../../services/api';
import type { TranscriptProcessResponse } from '../../types';

export default function CreateTranscript() {
  const [transcript, setTranscript] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<TranscriptProcessResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!transcript.trim() || isProcessing) return;
    setIsProcessing(true);
    setError(null);
    try {
      const data = await transcriptService.process(transcript);
      setResult(data);
      setTranscript('');
    } catch (err: unknown) {
      let msg = 'Failed to process transcript. Please check the backend is running.';
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        msg = err.response.data.detail;
      }
      setError(msg);
    } finally {
      setIsProcessing(false);
    }
  };

  if (result) {
    return (
      <div>
        <div className="mb-6 pb-4 border-b border-gray-200">
          <h1 className="text-lg font-semibold text-gray-900">Transcript Processed</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            AI has extracted CRM data from your meeting notes
            {result.ai_provider && (
              <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-200">
                Provider: {result.ai_provider}
              </span>
            )}
          </p>
        </div>

        {/* Result stats */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white border border-gray-200 rounded p-6 text-center">
            <p className="text-4xl font-bold text-indigo-600 mb-1">{result.projects_created}</p>
            <p className="text-sm font-semibold text-gray-700">Projects Created</p>
          </div>
          <div className="bg-white border border-gray-200 rounded p-6 text-center">
            <p className="text-4xl font-bold text-indigo-600 mb-1">{result.tasks_created}</p>
            <p className="text-sm font-semibold text-gray-700">Tasks Assigned</p>
          </div>
        </div>

        {/* Projects table */}
        {result.projects && result.projects.length > 0 && (
          <div className="bg-white border border-gray-200 rounded overflow-hidden mb-6">
            <div className="px-5 py-3 border-b border-gray-100 bg-gray-50">
              <span className="text-sm font-semibold text-gray-700">Generated Projects</span>
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 text-xs text-gray-400 uppercase tracking-wider">
                  <th className="text-left px-5 py-2.5 font-semibold">#</th>
                  <th className="text-left px-5 py-2.5 font-semibold">Project Name</th>
                  <th className="text-left px-5 py-2.5 font-semibold">Client</th>
                  <th className="text-right px-5 py-2.5 font-semibold">Tasks</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {result.projects.map((p, i) => (
                  <tr key={p.id || i} className="hover:bg-gray-50">
                    <td className="px-5 py-3 text-gray-400 text-xs">{i + 1}</td>
                    <td className="px-5 py-3 font-medium text-gray-900">{p.name}</td>
                    <td className="px-5 py-3 text-gray-600">{p.client_name}</td>
                    <td className="px-5 py-3 text-right">
                      <span className="bg-indigo-50 text-indigo-700 text-xs font-semibold px-2 py-0.5 rounded">
                        {p.task_count ?? '—'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={() => navigate('/projects')}
            className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm px-5 py-2 rounded transition-colors"
          >
            View All Projects →
          </button>
          <button
            onClick={() => setResult(null)}
            className="border border-gray-300 text-gray-600 hover:bg-gray-50 font-medium text-sm px-5 py-2 rounded transition-colors"
          >
            Process Another Transcript
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 pb-4 border-b border-gray-200">
        <h1 className="text-lg font-semibold text-gray-900">Create from Transcript</h1>
        <p className="text-gray-500 text-sm mt-0.5">
          Paste a meeting transcript to auto-generate projects, assign managers, and create tasks
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded mb-5">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Instructions */}
        <div className="bg-indigo-50 border border-indigo-200 rounded p-4 mb-4 text-sm text-indigo-800">
          <p className="font-semibold mb-1">How it works</p>
          <ol className="list-decimal list-inside space-y-0.5 text-indigo-700 text-xs">
            <li>Paste the full meeting transcript (raw notes, action items, decisions)</li>
            <li>The AI identifies projects, assigns managers by name, and extracts tasks</li>
            <li>Projects and tasks are saved to the CRM automatically in a single atomic transaction</li>
          </ol>
        </div>

        <div className="bg-white border border-gray-300 rounded overflow-hidden">
          <div className="flex items-center justify-between px-4 py-2.5 bg-gray-50 border-b border-gray-200">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Meeting Transcript</span>
            <span className="text-xs text-gray-400">{transcript.length} characters</span>
          </div>
          <textarea
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder="Paste your full meeting transcript here..."
            className="w-full h-80 px-4 py-3.5 text-sm font-mono leading-relaxed resize-none outline-none text-gray-800 placeholder:text-gray-400"
            disabled={isProcessing}
          />
          <div className="flex items-center justify-end px-4 py-3 bg-gray-50 border-t border-gray-200 gap-3">
            <span className="text-xs text-gray-400">Minimum ~100 characters recommended</span>
            <button
              type="submit"
              disabled={isProcessing || !transcript.trim()}
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm px-5 py-2 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? 'Analyzing transcript...' : 'Generate CRM Data →'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
