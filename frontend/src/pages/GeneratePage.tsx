import { useState, type FormEvent } from 'react';
import AppLayout from '../components/layout/AppLayout';
import { generateCode } from '../services/tasks';
import { executeCode } from '../services/executions';
import type { GenerateResponse, ExecuteResponse } from '../types';
import { getErrorMessage } from '../services/api';
import ErrorAlert from '../components/common/ErrorAlert';
import StatusBadge from '../components/common/StatusBadge';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import {
  Code2,
  Play,
  Copy,
  CheckCheck,
  Trash2,
  Loader2,
  Terminal,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Shield,
  Cpu,
  Database,
} from 'lucide-react';

export default function GeneratePage() {
  const [prompt, setPrompt] = useState('');
  const [task, setTask] = useState<GenerateResponse | null>(null);
  const [execution, setExecution] = useState<ExecuteResponse | null>(null);
  const [timeoutSeconds, setTimeoutSeconds] = useState(10);

  const [generating, setGenerating] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [genError, setGenError] = useState('');
  const [execError, setExecError] = useState('');
  const [copied, setCopied] = useState(false);

  const handleGenerate = async (e: FormEvent) => {
    e.preventDefault();
    setGenError('');
    setTask(null);
    setExecution(null);
    setGenerating(true);
    try {
      const result = await generateCode({ prompt });
      setTask(result);
    } catch (err) {
      setGenError(getErrorMessage(err));
    } finally {
      setGenerating(false);
    }
  };

  const handleExecute = async () => {
    if (!task) return;
    setExecError('');
    setExecution(null);
    setExecuting(true);
    try {
      const result = await executeCode({ task_id: task.id, timeout_seconds: timeoutSeconds });
      setExecution(result);
    } catch (err) {
      setExecError(getErrorMessage(err));
    } finally {
      setExecuting(false);
    }
  };

  const handleCopy = async () => {
    if (!task?.generated_code) return;
    await navigator.clipboard.writeText(task.generated_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClear = () => {
    setPrompt('');
    setTask(null);
    setExecution(null);
    setGenError('');
    setExecError('');
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Generate Code</h1>
          <p className="text-gray-400 mt-1 text-sm">
            Describe a Python programming task. The AI will generate code for you to review and run.
          </p>
        </div>

        {/* Prompt form */}
        <form onSubmit={handleGenerate} className="card space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1.5">Your prompt</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              required
              minLength={3}
              maxLength={5000}
              rows={4}
              placeholder="e.g. Write a Python program to calculate the factorial of a number using recursion."
              className="input-field resize-none"
            />
            <p className="text-xs text-gray-600 mt-1">{prompt.length}/5000 characters</p>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            <button
              type="submit"
              disabled={generating || !prompt.trim()}
              className="btn-primary"
            >
              {generating ? (
                <>
                  <Loader2 size={15} className="animate-spin" />
                  Generating…
                </>
              ) : (
                <>
                  <Code2 size={15} />
                  Generate Code
                </>
              )}
            </button>
            {(task || prompt) && (
              <button type="button" onClick={handleClear} className="btn-ghost text-xs">
                <Trash2 size={14} />
                Clear
              </button>
            )}
          </div>

          <ErrorAlert message={genError} />
        </form>

        {/* Generated code */}
        {task && task.generation_status === 'completed' && (
          <div className="card space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Code2 size={16} className="text-brand-400" />
                <span className="text-sm font-semibold text-white">Generated Code</span>
                <span className="badge bg-surface-700 text-gray-400 border border-surface-500 text-xs font-mono">
                  {task.model_name}
                </span>
              </div>
              <button onClick={handleCopy} className="btn-ghost text-xs">
                {copied ? <><CheckCheck size={13} className="text-green-400" /> Copied</> : <><Copy size={13} /> Copy</>}
              </button>
            </div>

            <div className="rounded-lg overflow-hidden border border-surface-600 text-sm">
              <SyntaxHighlighter
                language="python"
                style={vscDarkPlus}
                customStyle={{
                  margin: 0,
                  padding: '1rem',
                  background: '#0d0e17',
                  fontSize: '0.8rem',
                  lineHeight: '1.6',
                }}
                showLineNumbers
              >
                {task.generated_code}
              </SyntaxHighlighter>
            </div>

            {/* Run Controls */}
            <div className="flex items-center gap-4 pt-1 flex-wrap">
              <div className="flex items-center gap-2">
                <label className="text-xs text-gray-400">Timeout (seconds):</label>
                <select
                  value={timeoutSeconds}
                  onChange={(e) => setTimeoutSeconds(Number(e.target.value))}
                  className="input-field w-auto py-1 text-xs"
                >
                  {[5, 10, 15, 20, 30].map((t) => (
                    <option key={t} value={t}>{t}s</option>
                  ))}
                </select>
              </div>
              <button
                onClick={handleExecute}
                disabled={executing}
                className="btn-primary bg-green-700 hover:bg-green-600"
              >
                {executing ? (
                  <>
                    <Loader2 size={15} className="animate-spin" />
                    Executing…
                  </>
                ) : (
                  <>
                    <Play size={15} />
                    Run Code
                  </>
                )}
              </button>
            </div>

            <ErrorAlert message={execError} />
          </div>
        )}

        {task && task.generation_status === 'failed' && (
          <ErrorAlert message="Code generation failed. Please try again with a different prompt." />
        )}

        {/* Execution result */}
        {execution && <ExecutionResult execution={execution} />}
      </div>
    </AppLayout>
  );
}

function ExecutionResult({ execution }: { execution: ExecuteResponse }) {
  const isSuccess = execution.status === 'success';
  const Icon = isSuccess ? CheckCircle : XCircle;
  const iconColor = isSuccess ? 'text-green-400' : 'text-red-400';

  return (
    <div className="card space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal size={16} className="text-green-400" />
          <span className="text-sm font-semibold text-white">Execution Result</span>
        </div>
        <StatusBadge status={execution.status} />
      </div>

      {/* Meta grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <MetaItem icon={<Icon size={14} className={iconColor} />} label="Status" value={execution.status} />
        <MetaItem icon={<Terminal size={14} className="text-gray-400" />} label="Exit Code" value={execution.exit_code?.toString() ?? 'N/A'} />
        <MetaItem icon={<Clock size={14} className="text-gray-400" />} label="Duration" value={execution.duration_ms != null ? `${execution.duration_ms} ms` : 'N/A'} />
        <MetaItem icon={<Shield size={14} className={execution.cleanup_ok ? 'text-green-400' : 'text-red-400'} />} label="Cleanup" value={execution.cleanup_ok ? 'OK' : 'Failed'} />
      </div>

      {/* Security flags */}
      <div className="flex flex-wrap gap-2">
        <Flag label="Timed Out" active={execution.timed_out} icon={<Clock size={11} />} />
        <Flag label="Output Limited" active={execution.output_limited} icon={<Terminal size={11} />} />
        <Flag label="OOM Killed" active={execution.oom_killed} icon={<Database size={11} />} />
        <Flag label="Cleanup OK" active={!execution.cleanup_ok} invert icon={<Cpu size={11} />} />
      </div>

      {/* Stdout */}
      {execution.stdout && (
        <OutputBlock label="Standard Output" content={execution.stdout} colorClass="text-green-300" />
      )}

      {/* Stderr */}
      {execution.stderr && (
        <OutputBlock label="Standard Error" content={execution.stderr} colorClass="text-red-300" icon={<AlertTriangle size={13} className="text-red-400" />} />
      )}

      {/* Error */}
      {execution.error && (
        <div className="rounded-lg bg-red-500/10 border border-red-500/30 p-3">
          <p className="text-xs text-red-400 font-semibold mb-1">Error</p>
          <p className="text-xs text-red-300 font-mono">{execution.error}</p>
        </div>
      )}

      {!execution.stdout && !execution.stderr && !execution.error && (
        <p className="text-sm text-gray-500 italic">(No output)</p>
      )}
    </div>
  );
}

function MetaItem({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-surface-700 rounded-lg px-3 py-2.5">
      <div className="flex items-center gap-1.5 mb-1 text-gray-500 text-xs">{icon}{label}</div>
      <p className="text-sm font-medium text-gray-200">{value}</p>
    </div>
  );
}

function Flag({ label, active, invert = false, icon }: { label: string; active: boolean; invert?: boolean; icon: React.ReactNode }) {
  const isWarn = invert ? !active : active;
  return (
    <span className={`badge ${isWarn ? 'bg-red-500/15 text-red-400 border border-red-500/30' : 'bg-surface-700 text-gray-500 border border-surface-500'}`}>
      {icon}
      {label}: {active ? 'Yes' : 'No'}
    </span>
  );
}

function OutputBlock({ label, content, colorClass, icon }: { label: string; content: string; colorClass: string; icon?: React.ReactNode }) {
  return (
    <div>
      <div className="flex items-center gap-1.5 mb-1.5 text-xs text-gray-400">
        {icon}
        {label}
      </div>
      <pre className={`bg-surface-900 border border-surface-600 rounded-lg px-3 py-2.5 text-xs font-mono ${colorClass} overflow-x-auto whitespace-pre-wrap max-h-60 overflow-y-auto`}>
        {content}
      </pre>
    </div>
  );
}
