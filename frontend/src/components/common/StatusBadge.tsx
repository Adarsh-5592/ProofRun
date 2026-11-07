interface StatusBadgeProps {
  status: string;
  className?: string;
}

const statusStyles: Record<string, string> = {
  success: 'bg-green-500/15 text-green-400 border border-green-500/30',
  error: 'bg-red-500/15 text-red-400 border border-red-500/30',
  timeout: 'bg-yellow-500/15 text-yellow-400 border border-yellow-500/30',
  output_limit: 'bg-orange-500/15 text-orange-400 border border-orange-500/30',
  memory_limit: 'bg-orange-500/15 text-orange-400 border border-orange-500/30',
  sandbox_error: 'bg-red-500/15 text-red-400 border border-red-500/30',
  sandbox_busy: 'bg-yellow-500/15 text-yellow-400 border border-yellow-500/30',
  cleanup_error: 'bg-purple-500/15 text-purple-400 border border-purple-500/30',
  completed: 'bg-green-500/15 text-green-400 border border-green-500/30',
  generating: 'bg-blue-500/15 text-blue-400 border border-blue-500/30',
  failed: 'bg-red-500/15 text-red-400 border border-red-500/30',
};

const statusLabels: Record<string, string> = {
  success: 'Success',
  error: 'Error',
  timeout: 'Timeout',
  output_limit: 'Output Limit',
  memory_limit: 'Memory Limit',
  sandbox_error: 'Sandbox Error',
  sandbox_busy: 'Sandbox Busy',
  cleanup_error: 'Cleanup Error',
  completed: 'Completed',
  generating: 'Generating',
  failed: 'Failed',
};

export default function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const style = statusStyles[status] ?? 'bg-gray-500/15 text-gray-400 border border-gray-500/30';
  const label = statusLabels[status] ?? status;
  return (
    <span className={`badge ${style} ${className}`}>
      {label}
    </span>
  );
}
