import { useEffect, useState } from 'react';
import AppLayout from '../components/layout/AppLayout';
import { getExecutionHistory } from '../services/executions';
import type { ExecuteResponse } from '../types';
import { getErrorMessage } from '../services/api';
import ErrorAlert from '../components/common/ErrorAlert';
import LoadingSpinner from '../components/common/LoadingSpinner';
import StatusBadge from '../components/common/StatusBadge';
import { Terminal, ChevronDown, ChevronUp, ChevronLeft, ChevronRight, Clock, Shield, AlertTriangle } from 'lucide-react';

const PAGE_SIZE = 10;

export default function ExecutionHistoryPage() {
  const [executions, setExecutions] = useState<ExecuteResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const data = await getExecutionHistory(page * PAGE_SIZE, PAGE_SIZE);
        setExecutions(data);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [page]);

  const toggle = (id: string) => setExpanded((p) => (p === id ? null : id));

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-5">
        <div>
          <h1 className="text-2xl font-bold text-white">Execution History</h1>
          <p className="text-gray-400 mt-1 text-sm">Every sandboxed code execution run.</p>
        </div>

        <ErrorAlert message={error} />

        {loading ? (
          <div className="flex justify-center py-16">
            <LoadingSpinner label="Loading executions…" />
          </div>
        ) : executions.length === 0 ? (
          <div className="card text-center py-12">
            <Terminal size={32} className="mx-auto text-gray-600 mb-3" />
            <p className="text-gray-400 font-medium">No executions found</p>
            <p className="text-sm text-gray-600 mt-1">
              {page > 0 ? 'No more executions on this page.' : 'Run your first generated code to see results here.'}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {executions.map((exec) => (
              <div key={exec.id} className="card">
                <button
                  onClick={() => toggle(exec.id)}
                  className="w-full flex items-start justify-between gap-3 text-left"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <StatusBadge status={exec.status} />
                      {exec.exit_code != null && (
                        <span className="badge bg-surface-700 text-gray-400 border border-surface-500">
                          exit {exec.exit_code}
                        </span>
                      )}
                      {exec.timed_out && (
                        <span className="badge bg-yellow-500/15 text-yellow-400 border border-yellow-500/30">
                          <Clock size={10} /> Timeout
                        </span>
                      )}
                      {exec.oom_killed && (
                        <span className="badge bg-orange-500/15 text-orange-400 border border-orange-500/30">
                          OOM
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 font-mono">
                      exec: {exec.id.slice(0, 10)}… · task: {exec.task_id.slice(0, 10)}…
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-600">
                      <span>{new Date(exec.created_at).toLocaleString()}</span>
                      {exec.duration_ms != null && <span>{exec.duration_ms} ms</span>}
                      <span className="flex items-center gap-1">
                        <Shield size={10} className={exec.cleanup_ok ? 'text-green-500' : 'text-red-500'} />
                        Cleanup: {exec.cleanup_ok ? 'OK' : 'Failed'}
                      </span>
                    </div>
                  </div>
                  {expanded === exec.id ? (
                    <ChevronUp size={16} className="text-gray-500 flex-shrink-0 mt-1" />
                  ) : (
                    <ChevronDown size={16} className="text-gray-500 flex-shrink-0 mt-1" />
                  )}
                </button>

                {expanded === exec.id && (
                  <div className="mt-4 space-y-3">
                    {/* Security flags */}
                    <div className="flex flex-wrap gap-2">
                      {[
                        { label: 'Timed Out', active: exec.timed_out },
                        { label: 'Output Limited', active: exec.output_limited },
                        { label: 'OOM Killed', active: exec.oom_killed },
                      ].map(({ label, active }) => (
                        <span
                          key={label}
                          className={`badge ${active ? 'bg-red-500/15 text-red-400 border border-red-500/30' : 'bg-surface-700 text-gray-500 border border-surface-500'}`}
                        >
                          {label}: {active ? 'Yes' : 'No'}
                        </span>
                      ))}
                    </div>

                    {exec.stdout && (
                      <div>
                        <p className="text-xs text-gray-400 mb-1">Standard Output</p>
                        <pre className="bg-surface-900 border border-surface-600 rounded-lg p-3 text-xs font-mono text-green-300 overflow-x-auto whitespace-pre-wrap max-h-48 overflow-y-auto">
                          {exec.stdout}
                        </pre>
                      </div>
                    )}

                    {exec.stderr && (
                      <div>
                        <div className="flex items-center gap-1.5 mb-1 text-xs text-gray-400">
                          <AlertTriangle size={12} className="text-red-400" />
                          Standard Error
                        </div>
                        <pre className="bg-surface-900 border border-surface-600 rounded-lg p-3 text-xs font-mono text-red-300 overflow-x-auto whitespace-pre-wrap max-h-48 overflow-y-auto">
                          {exec.stderr}
                        </pre>
                      </div>
                    )}

                    {exec.error && (
                      <div className="rounded-lg bg-red-500/10 border border-red-500/30 p-3">
                        <p className="text-xs text-red-400 font-semibold mb-1">Error</p>
                        <p className="text-xs text-red-300 font-mono">{exec.error}</p>
                      </div>
                    )}

                    {!exec.stdout && !exec.stderr && !exec.error && (
                      <p className="text-sm text-gray-500 italic">(No output)</p>
                    )}
                  </div>
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
            disabled={executions.length < PAGE_SIZE || loading}
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
