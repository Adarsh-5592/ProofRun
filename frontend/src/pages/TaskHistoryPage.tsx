import { useEffect, useState } from 'react';
import AppLayout from '../components/layout/AppLayout';
import { getTaskHistory } from '../services/tasks';
import type { GenerateResponse } from '../types';
import { getErrorMessage } from '../services/api';
import ErrorAlert from '../components/common/ErrorAlert';
import LoadingSpinner from '../components/common/LoadingSpinner';
import StatusBadge from '../components/common/StatusBadge';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { History, ChevronDown, ChevronUp, ChevronLeft, ChevronRight } from 'lucide-react';

const PAGE_SIZE = 10;

export default function TaskHistoryPage() {
  const [tasks, setTasks] = useState<GenerateResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await getTaskHistory(page * PAGE_SIZE, PAGE_SIZE);
        setTasks(data);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [page]);

  const toggleExpand = (id: string) => {
    setExpanded((prev) => (prev === id ? null : id));
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-5">
        <div>
          <h1 className="text-2xl font-bold text-white">Task History</h1>
          <p className="text-gray-400 mt-1 text-sm">All your code-generation tasks.</p>
        </div>

        <ErrorAlert message={error} />

        {loading ? (
          <div className="flex justify-center py-16">
            <LoadingSpinner label="Loading tasks…" />
          </div>
        ) : tasks.length === 0 ? (
          <div className="card text-center py-12">
            <History size={32} className="mx-auto text-gray-600 mb-3" />
            <p className="text-gray-400 font-medium">No tasks found</p>
            <p className="text-sm text-gray-600 mt-1">
              {page > 0 ? 'No more tasks on this page.' : 'Generate your first task to get started.'}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {tasks.map((task) => (
              <div key={task.id} className="card">
                {/* Summary row */}
                <button
                  onClick={() => toggleExpand(task.id)}
                  className="w-full flex items-start justify-between gap-3 text-left"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <StatusBadge status={task.generation_status} />
                      <span className="text-xs font-mono text-gray-500">{task.id.slice(0, 12)}…</span>
                    </div>
                    <p className="text-sm text-gray-200 truncate">{task.prompt}</p>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      <span>{new Date(task.created_at).toLocaleString()}</span>
                      {task.model_name && <span className="font-mono">{task.model_name}</span>}
                    </div>
                  </div>
                  {expanded === task.id ? (
                    <ChevronUp size={16} className="text-gray-500 flex-shrink-0 mt-1" />
                  ) : (
                    <ChevronDown size={16} className="text-gray-500 flex-shrink-0 mt-1" />
                  )}
                </button>

                {/* Expanded code */}
                {expanded === task.id && task.generated_code && (
                  <div className="mt-4 rounded-lg overflow-hidden border border-surface-600">
                    <SyntaxHighlighter
                      language="python"
                      style={vscDarkPlus}
                      customStyle={{
                        margin: 0,
                        padding: '1rem',
                        background: '#0d0e17',
                        fontSize: '0.78rem',
                        lineHeight: '1.6',
                        maxHeight: '400px',
                      }}
                      showLineNumbers
                    >
                      {task.generated_code}
                    </SyntaxHighlighter>
                  </div>
                )}

                {expanded === task.id && task.generation_status === 'failed' && (
                  <p className="mt-3 text-sm text-red-400 italic">Code generation failed for this task.</p>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        <div className="flex items-center justify-between pt-2">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0 || loading}
            className="btn-secondary text-xs"
          >
            <ChevronLeft size={14} />
            Previous
          </button>
          <span className="text-xs text-gray-500">Page {page + 1}</span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={tasks.length < PAGE_SIZE || loading}
            className="btn-secondary text-xs"
          >
            Next
            <ChevronRight size={14} />
          </button>
        </div>
      </div>
    </AppLayout>
  );
}
