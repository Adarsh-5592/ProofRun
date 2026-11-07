import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import AppLayout from '../components/layout/AppLayout';
import { getTaskHistory } from '../services/tasks';
import { getExecutionHistory, checkHealth } from '../services/executions';
import type { GenerateResponse, ExecuteResponse, HealthResponse } from '../types';
import {
  Code2,
  Terminal,
  History,
  ArrowRight,
  CheckCircle,
  XCircle,
  Wifi,
  WifiOff,
} from 'lucide-react';
import StatusBadge from '../components/common/StatusBadge';

export default function DashboardPage() {
  const { user } = useAuth();
  const [recentTasks, setRecentTasks] = useState<GenerateResponse[]>([]);
  const [recentExecutions, setRecentExecutions] = useState<ExecuteResponse[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthError, setHealthError] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [tasks, execs, h] = await Promise.allSettled([
          getTaskHistory(0, 5),
          getExecutionHistory(0, 5),
          checkHealth(),
        ]);
        if (tasks.status === 'fulfilled') setRecentTasks(tasks.value);
        if (execs.status === 'fulfilled') setRecentExecutions(execs.value);
        if (h.status === 'fulfilled') {
          setHealth(h.value);
          setHealthError(false);
        } else {
          setHealthError(true);
        }
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* Welcome */}
        <div>
          <h1 className="text-2xl font-bold text-white">
            Welcome back, {user?.full_name?.split(' ')[0]} 👋
          </h1>
          <p className="text-gray-400 mt-1 text-sm">
            Generate and execute AI code safely from your dashboard.
          </p>
        </div>

        {/* Backend health */}
        <div className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm border ${
          healthError
            ? 'bg-red-500/10 border-red-500/30 text-red-400'
            : 'bg-green-500/10 border-green-500/30 text-green-400'
        }`}>
          {healthError ? (
            <>
              <WifiOff size={16} />
              <span>Backend is unreachable. Start the FastAPI server at <code className="font-mono text-xs">http://localhost:8000</code>.</span>
            </>
          ) : (
            <>
              <Wifi size={16} />
              <span>Backend connected – {health?.application} v{health?.version}</span>
            </>
          )}
        </div>

        {/* Quick actions */}
        <div>
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Quick Actions</h2>
          <div className="grid sm:grid-cols-3 gap-4">
            <Link to="/generate" className="card hover:border-brand-700 transition-colors flex items-center justify-between group">
              <div>
                <Code2 size={20} className="text-brand-400 mb-2" />
                <p className="font-semibold text-white text-sm">Generate Code</p>
                <p className="text-xs text-gray-500 mt-0.5">New prompt → AI code</p>
              </div>
              <ArrowRight size={16} className="text-gray-600 group-hover:text-brand-400 transition-colors" />
            </Link>
            <Link to="/tasks" className="card hover:border-brand-700 transition-colors flex items-center justify-between group">
              <div>
                <History size={20} className="text-purple-400 mb-2" />
                <p className="font-semibold text-white text-sm">Task History</p>
                <p className="text-xs text-gray-500 mt-0.5">{recentTasks.length > 0 ? `${recentTasks.length} recent tasks` : 'No tasks yet'}</p>
              </div>
              <ArrowRight size={16} className="text-gray-600 group-hover:text-purple-400 transition-colors" />
            </Link>
            <Link to="/executions" className="card hover:border-brand-700 transition-colors flex items-center justify-between group">
              <div>
                <Terminal size={20} className="text-green-400 mb-2" />
                <p className="font-semibold text-white text-sm">Executions</p>
                <p className="text-xs text-gray-500 mt-0.5">{recentExecutions.length > 0 ? `${recentExecutions.length} recent runs` : 'No runs yet'}</p>
              </div>
              <ArrowRight size={16} className="text-gray-600 group-hover:text-green-400 transition-colors" />
            </Link>
          </div>
        </div>

        {/* Recent tasks */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Recent Tasks</h2>
            <Link to="/tasks" className="text-xs text-brand-400 hover:text-brand-300">View all →</Link>
          </div>
          {loading ? (
            <div className="card animate-pulse h-24" />
          ) : recentTasks.length === 0 ? (
            <div className="card text-center py-8">
              <Code2 size={28} className="mx-auto text-gray-600 mb-2" />
              <p className="text-sm text-gray-500">No tasks yet.</p>
              <Link to="/generate" className="text-brand-400 text-sm hover:underline mt-1 inline-block">Generate your first →</Link>
            </div>
          ) : (
            <div className="space-y-2">
              {recentTasks.map((task) => (
                <div key={task.id} className="card flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-gray-200 truncate">{task.prompt}</p>
                    <p className="text-xs text-gray-500 mt-0.5 font-mono">{task.id.slice(0, 8)}…</p>
                  </div>
                  <StatusBadge status={task.generation_status} />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent executions */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Recent Executions</h2>
            <Link to="/executions" className="text-xs text-brand-400 hover:text-brand-300">View all →</Link>
          </div>
          {loading ? (
            <div className="card animate-pulse h-24" />
          ) : recentExecutions.length === 0 ? (
            <div className="card text-center py-8">
              <Terminal size={28} className="mx-auto text-gray-600 mb-2" />
              <p className="text-sm text-gray-500">No executions yet.</p>
              <Link to="/generate" className="text-brand-400 text-sm hover:underline mt-1 inline-block">Generate and run code →</Link>
            </div>
          ) : (
            <div className="space-y-2">
              {recentExecutions.map((exec) => (
                <div key={exec.id} className="card flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    {exec.status === 'success' ? (
                      <CheckCircle size={15} className="text-green-400 flex-shrink-0" />
                    ) : (
                      <XCircle size={15} className="text-red-400 flex-shrink-0" />
                    )}
                    <div className="min-w-0">
                      <p className="text-xs font-mono text-gray-400 truncate">task: {exec.task_id.slice(0, 8)}…</p>
                      {exec.duration_ms != null && (
                        <p className="text-xs text-gray-600">{exec.duration_ms} ms</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <StatusBadge status={exec.status} />
                    {exec.exit_code != null && (
                      <span className="badge bg-surface-700 text-gray-400 border border-surface-500">
                        exit {exec.exit_code}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
