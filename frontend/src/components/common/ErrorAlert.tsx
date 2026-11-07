import { AlertCircle } from 'lucide-react';

interface ErrorAlertProps {
  message: string;
  className?: string;
}

export default function ErrorAlert({ message, className = '' }: ErrorAlertProps) {
  if (!message) return null;
  return (
    <div className={`flex items-start gap-3 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm ${className}`}>
      <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
      <span>{message}</span>
    </div>
  );
}
