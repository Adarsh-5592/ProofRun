interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

const sizeClasses = {
  sm: 'h-4 w-4 border-2',
  md: 'h-7 w-7 border-2',
  lg: 'h-10 w-10 border-2',
};

export default function LoadingSpinner({ size = 'md', label }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center gap-3">
      <div
        className={`animate-spin rounded-full border-surface-600 border-t-brand-500 ${sizeClasses[size]}`}
      />
      {label && <p className="text-sm text-gray-500">{label}</p>}
    </div>
  );
}
